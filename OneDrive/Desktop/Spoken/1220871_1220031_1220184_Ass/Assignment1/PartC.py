"""
Part C 
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.signal import iirpeak, lfilter, butter, filtfilt
import parselmouth

# ----------------------------------------
# Global settings
# ----------------------------------------
FS = 16000        # sampling rate (Hz)
DURATION = 1.0    # seconds
 
# Formant frequencies + bandwidths (Hz)

FORMANTS_DICT = {
    "i": [(300, 80),  (2400, 200), (3000, 250)],
    "e": [(500, 90),  (1900, 200), (2500, 250)],
    "a": [(800, 120), (1200, 220), (2600, 300)],
    "o": [(500, 100), (900, 180),  (2400, 260)],
    "u": [(350, 90),  (700, 170),  (2400, 260)],
}

# ----------------------------------------
# Source: smoothed impulse train + envelope
# ----------------------------------------

def glottal_source(F0=90, fs=16000, duration=1.0):
    
    N = int(fs * duration)
    period = int(fs / F0)

    # raw impulse train
    x = np.zeros(N)
    x[::period] = 1.0

    # smooth each impulse
    win_len = max(3, int(0.003 * fs))       # about 3 ms
    win = np.hamming(win_len)
    x = np.convolve(x, win, mode="same")

    # gentle spectral tilt (low-pass around 2 kHz)
    b_lp, a_lp = butter(1, 2000 / (fs / 2.0), btype='low')
    x = filtfilt(b_lp, a_lp, x)

    # normalize
    x /= np.max(np.abs(x) + 1e-9)

    # fade in/out to avoid boundary clicks (20 ms)
    fade_len = int(0.02 * fs)
    env = np.ones(N)
    env[:fade_len] = np.linspace(0.0, 1.0, fade_len)
    env[-fade_len:] = np.linspace(1.0, 0.0, fade_len)

    return x * env

# ----------------------------------------
# Vocal-tract resonators (filters)
# ----------------------------------------

def resonator(center_freq, bandwidth, fs):
    """
    Second-order resonator at center_freq with given bandwidth.
    """
    Q = center_freq / bandwidth
    w0 = center_freq / (fs / 2.0)  
    b, a = iirpeak(w0, Q)
    return b, a

def apply_resonators(x, formants, fs):
    """
    Cascade of resonators (one per formant).
    """
    y = x.copy()
    for (f, bw) in formants:
        b, a = resonator(f, bw, fs)
        y = lfilter(b, a, y)
    return y


# Synthesis pipeline


def synthesize_vowel(vowel_label,
                     F0=90,
                     fs=16000,
                     duration=1.0,
                     save_wav=True):
    """
    Source – filter synthesis for a single vowel.
    """
    if vowel_label not in FORMANTS_DICT:
        raise ValueError(f"Unknown vowel '{vowel_label}'")

    # 1) source
    s = glottal_source(F0=F0, fs=fs, duration=duration)

    # 2) vocal tract
    formants = FORMANTS_DICT[vowel_label]
    y = apply_resonators(s, formants, fs)

    # 3) normalize
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.9

    # 4) save
    fname = None
    if save_wav:
        fname = f"synth_{vowel_label}.wav"
        sf.write(fname, y, fs)

    return y, fname

def plot_waveform(signal, fs, title):
    t = np.linspace(0, len(signal) / fs, len(signal), endpoint=False)
    plt.figure()
    plt.plot(t, signal)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()

def plot_spectrogram(signal, fs, title):
    plt.figure()
    plt.specgram(signal, NFFT=1024, Fs=fs, noverlap=512)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.tight_layout()
    plt.show()

# ----------------------------------------
# Formant estimation
# ----------------------------------------

def estimate_formants_praat(wav_path):
    snd = parselmouth.Sound(wav_path)
    formants = snd.to_formant_burg()
    mid = snd.get_total_duration() / 2
    f1 = formants.get_value_at_time(1, mid)
    f2 = formants.get_value_at_time(2, mid)
    return f1, f2


# MAIN


if __name__ == "__main__":
    F0_demo = 90  # lower pitch for clearer formants

    vowels = ["i", "e", "a", "o", "u"]
    F1_syn, F2_syn = [], []

    for v in vowels:
        print("=" * 40)
        print(f"Synthesizing /{v}/ ...")

        y, fname = synthesize_vowel(vowel_label=v,
                                    F0=F0_demo,
                                    fs=FS,
                                    duration=DURATION,
                                    save_wav=True)

        print("Saved:", fname)

        # Plots
        plot_waveform(y, FS, f"/{v}/ waveform")
        plot_spectrogram(y, FS, f"/{v}/ spectrogram")

        # Estimate formants
        f1, f2 = estimate_formants_praat(fname)
        F1_syn.append(f1)
        F2_syn.append(f2)
        print(f"Estimated formants /{v}/: F1={f1:.1f} Hz, F2={f2:.1f} Hz")

    print("\nSummary synthetic formants:")
    for v, f1, f2 in zip(vowels, F1_syn, F2_syn):
        print(f"/{v}/  F1={f1:.1f} Hz   F2={f2:.1f} Hz")


# ----------------------------------------
# interactive GUI for F1/F2 tuning

import tkinter as tk
from tkinter import ttk
import sounddevice as sd

def synth_play_gui(vowel_label, f1_val, f2_val,breathy=False):

    formants_orig = FORMANTS_DICT[vowel_label]
    formants = [(f1_val, formants_orig[0][1]), 
                (f2_val, formants_orig[1][1]), 
                formants_orig[2]]
    
    s = glottal_source(F0=90, fs=FS, duration=DURATION)
    if breathy:
         noise = np.random.normal(0, 0.02, len(s))  # small Gaussian noise(can be 0.02–0.05)
         s += noise

    y = apply_resonators(s, formants, FS)
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.9
    sd.play(y, FS)
    sd.wait()

# Build GUI
root = tk.Tk()
root.title("Interactive F1/F2 Vowel Synth")

vowel_label = tk.StringVar(value="i")
tk.Label(root, text="Vowel").grid(row=0,column=0)
vowel_menu = ttk.Combobox(root, textvariable=vowel_label, values=list(FORMANTS_DICT.keys()), state="readonly")
vowel_menu.grid(row=0,column=1)

tk.Label(root, text="F1 (Hz)").grid(row=1,column=0)
f1_slider = tk.Scale(root, from_=200, to=1000, orient='horizontal')
f1_slider.set(FORMANTS_DICT["i"][0][0])
f1_slider.grid(row=1,column=1)

tk.Label(root, text="F2 (Hz)").grid(row=2,column=0)
f2_slider = tk.Scale(root, from_=800, to=3500, orient='horizontal')
f2_slider.set(FORMANTS_DICT["i"][1][0])
f2_slider.grid(row=2,column=1)

breathy_var = tk.BooleanVar(value=False)
breath_chk = tk.Checkbutton(root, text="Add Breathiness", variable=breathy_var)
breath_chk.grid(row=3,column=0,columnspan=2)

def update_play():
    synth_play_gui(vowel_label.get(), f1_slider.get(), f2_slider.get(),breathy_var.get())

play_btn = ttk.Button(root, text="Play Vowel", command=update_play)
play_btn.grid(row=4,column=0,columnspan=2,pady=10)

root.mainloop()
import parselmouth
from parselmouth.praat import call
import matplotlib.pyplot as plt

# Vowels to include
vowels = ["i", "e", "a", "o", "u"]

# Storage for values
natural_F1 = []
natural_F2 = []
synthetic_F1 = []
synthetic_F2 = []

def get_mid_formants(filename):
    snd = parselmouth.Sound(filename)
    duration = snd.get_total_duration()
    midpoint = duration / 2

    formants = call(snd, "To Formant (burg)", 0.005, 5, 4500, 0.025, 50)
    f1 = call(formants, "Get value at time", 1, midpoint, "Hertz", "Linear")
    f2 = call(formants, "Get value at time", 2, midpoint, "Hertz", "Linear")
    return f1, f2

# ----- Extract natural vowels (Speaker 3) -----
for v in vowels:
    filename = f"Speaker3_{v}.wav"
    fname = f"./Recordings_wav/Speaker3_wav/{filename}"
    f1, f2 = get_mid_formants(fname)
    natural_F1.append(f1)
    natural_F2.append(f2)

# ----- Extract synthetic vowels -----
for v in vowels:
    fname = f"synth_{v}.wav"  
    f1, f2 = get_mid_formants(fname)
    synthetic_F1.append(f1)
    synthetic_F2.append(f2)

# ----- Plot vowel space -----
plt.figure(figsize=(7, 6))
plt.scatter(natural_F1, natural_F2, label="Natural (Speaker 3)", s=80)
plt.scatter(synthetic_F1, synthetic_F2, label="Synthetic", s=80, marker="x")

for i, v in enumerate(vowels):
    plt.text(natural_F1[i]+20, natural_F2[i]+20, v)
    plt.text(synthetic_F1[i]+20, synthetic_F2[i]+20, v+"_synth")

plt.gca().invert_xaxis() 
plt.gca().invert_yaxis()
plt.xlabel("F1 (Hz)")
plt.ylabel("F2 (Hz)")
plt.title("Natural vs Synthetic Vowel Space")
plt.legend()
plt.grid(True)
plt.show()
