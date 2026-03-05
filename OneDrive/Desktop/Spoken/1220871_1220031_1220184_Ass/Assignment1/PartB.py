# ================================
# SLP Assignment - Part B (Python)
# Pitch extraction using parselmouth
# ================================

import parselmouth
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# -------------------------------
# Configuration
# -------------------------------


speakers = [1, 2, 3]  # Speaker1, Speaker2, Speaker3
vowels = ["a", "e", "i", "o", "u"]


def make_filename(speaker_id, vowel):
    filename = f"Speaker{speaker_id}_{vowel}.wav"
    return f"./Recordings_wav/Speaker{speaker_id}_wav/{filename}"


# -------------------------------
# Core pitch analysis function
# -------------------------------

def analyze_pitch(filename, plot=True):
    """
    Load a WAV file, extract pitch using parselmouth,
    compute min/max/mean F0 (ignoring unvoiced frames).
    """

    if not os.path.exists(filename):
        print(f"[WARNING] File not found: {filename}")
        return None

    # Load sound
    snd = parselmouth.Sound(filename)

    # to_pitch(time_step, pitch_floor, pitch_ceiling)
    # Match the assignment settings: time step = 0.01s, range = 75–500 Hz
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500)

    # Extract arrays
    pitch_values = pitch.selected_array['frequency']  # F0 values (Hz)
    times = pitch.xs()                                # time stamps (s)

    # Remove unvoiced frames (zeros)
    voiced = pitch_values[pitch_values > 0]

    if len(voiced) == 0:
        print(f"[WARNING] No voiced frames found in {filename}")
        return None

    f0_min = np.min(voiced)
    f0_max = np.max(voiced)
    f0_mean = np.mean(voiced)

    # Plot pitch contour
    if plot:
        plt.figure()
        plt.plot(times, pitch_values)
        plt.title(f"Pitch contour - {filename}")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.tight_layout()
        plt.show()

    # Print results
    print(f"Results for {filename}:")
    print(f"  Min F0:  {f0_min:.2f} Hz")
    print(f"  Max F0:  {f0_max:.2f} Hz")
    print(f"  Mean F0: {f0_mean:.2f} Hz")
    print("-" * 40)

    # Return as a dictionary
    return {
        "filename": filename,
        "f0_min": f0_min,
        "f0_max": f0_max,
        "f0_mean": f0_mean
    }


# -------------------------------
# Run analysis for all speakers & vowels
# -------------------------------

all_results = []

for s in speakers:
    for v in vowels:
        fname = make_filename(s, v)
        result = analyze_pitch(fname, plot=True)  
        if result is not None:
           
            result["speaker"] = s
            result["vowel"] = v
            all_results.append(result)

# -------------------------------
# Save results to a table
# -------------------------------

if len(all_results) > 0:
    df = pd.DataFrame(all_results)
    print("\n===== Summary Table (Per Vowel) =====\n")
    print(df)

    # -------------------------------
    # Speaker-level pitch ranges
    # -------------------------------
    
    speaker_summary = df.groupby("speaker")[["f0_min", "f0_max", "f0_mean"]].agg({
        "f0_min": "min",
        "f0_max": "max",
        "f0_mean": "mean"
    })

    print("\n===== Pitch Range Per Speaker =====\n")
    print(speaker_summary)


else:
    print("No valid results to save.")
