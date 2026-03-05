# SLP Assignment 01 — Vowel Acoustics, Pitch & Source–Filter Synthesis

**Spoken Language Processing — Fall 2025/2026**  
Group: 1220871, 1220031, 1220184

This repository contains the implementation for **Assignment 01** (Section 2): vowel data collection & acoustic analysis (**Part A**), pitch (F₀) measurement (**Part B**), and source–filter vowel synthesis (**Part C**).

---

## Assignment overview (from handout)

| Part | Goal |
|------|------|
| **A** | Data collection & acoustic analysis: record vowels, measure F1/F2, duration, spectrograms (Praat/parselmouth). |
| **B** | Measure pitch (F₀) from Part A recordings using **Praat** and **Python (parselmouth)**; compare methods, report min/max/mean F₀ and pitch contours. |
| **C** | Source–filter synthesis: glottal source (impulse train), formant resonators (IIR biquad), synthesize vowels; compare natural vs synthetic (vowel space F1–F2). |

---

## Repository structure

```
1220871_1220031_1220184_Ass/
├── README.md
├── Assignment1/
│   ├── PartB.py              # Pitch (F₀) extraction with parselmouth
│   ├── PartC.py              # Source–filter synthesis + formant comparison + GUI
│   └── Spoken_partB_pitch_to_text/
│       ├── speaker1_a.Pitch   # Praat pitch export (Speaker 1, vowel /a/)
│       ├── speaker1_a.Matrix
│       ├── Speaker2_a.Pitch
│       ├── Speaker2_a.Matrix
│       ├── Speaker3_a.Pitch
│       └── Speaker3_a.Matrix
└── (optional) Recordings_wav/   # WAVs for Part B: Speaker1_wav/, Speaker2_wav/, Speaker3_wav/
```

- **Part B** expects WAV files under `Assignment1/Recordings_wav/Speaker{N}_wav/` (e.g. `Speaker1_a.wav`, `Speaker2_e.wav`, …).  
- **Part C** generates `synth_i.wav`, `synth_e.wav`, etc., and can compare with natural vowels if the same recording paths exist.

---

## Requirements

- Python 3.7+
- **parselmouth** (Praat in Python)
- **numpy**, **scipy**, **matplotlib**
- **soundfile** (write WAV in Part C)
- **pandas** (Part B summary table)
- **sounddevice** (Part C GUI playback)
- **tkinter** (usually with Python; Part C GUI)

Install:

```bash
pip install parselmouth numpy scipy matplotlib soundfile pandas sounddevice
```

---

## How to run

### Part B — Pitch (F₀) extraction

From the `Assignment1` folder:

```bash
cd Assignment1
python PartB.py
```

- Reads WAVs from `./Recordings_wav/Speaker{N}_wav/Speaker{N}_{vowel}.wav` (vowels: a, e, i, o, u).
- Uses parselmouth with time step 0.01 s, pitch range 75–500 Hz (matching Praat settings).
- Prints min/max/mean F₀ per file and a summary table; plots pitch contour per recording.

### Part C — Source–filter synthesis

From the `Assignment1` folder:

```bash
cd Assignment1
python PartC.py
```

- Synthesizes vowels **/i, e, a, o, u/** (glottal source + formant resonators F1–F3).
- Saves `synth_i.wav`, `synth_e.wav`, … and shows waveform + spectrogram per vowel.
- Estimates formants (parselmouth) and prints F1/F2.
- Plots **natural vs synthetic vowel space** (F1 vs F2) if natural WAVs are present.
- Opens an **interactive GUI** to change F1/F2, select vowel, add breathiness, and play the synthetic sound.

---

## Part C — Technical summary

- **Glottal source:** Smoothed impulse train at configurable F₀ (default 90 Hz), low-pass filtered, fade in/out.
- **Formants:** Second-order IIR peak filters (F1, F2, F3) per vowel; cascade of resonators.
- **Vowel formants (Hz):**  
  /i/ 300, 2400, 3000 | /e/ 500, 1900, 2500 | /a/ 800, 1200, 2600 | /o/ 500, 900, 2400 | /u/ 350, 700, 2400 (bandwidths in code).

---

## Assignment PDF

The full handout (tasks, deliverables, report structure) is: **SLP_Assignment01_Section2.pdf** (in the course materials). Submit the report (2–4 pages) plus this code/data folder as required.

---

## Authors

- 1220871  
- 1220031  
- 1220184  

## License

For academic/educational use. When using participant recordings, ensure consent and do not include identifying information in the submission.
