# pyawgn
A tool to apply measured signal-to-noise ratio to audio samples of baseband digital modulation. Intended to help modem users and developers measure and compare performance of different modulation and demodulation systems and techniques, under repeatable and measured conditions. **This is experimental, and I may have the concepts and/or math wrong. If you use this program for any purpose, please validate your own results.**
# Requirements
- Python3
- SciPy
# pyawgn.py
Removes periods of silence and applies measured additive white gaussian noise to achieve the specified signal-to-noise ration within the specified bandwidth. The program accepts single-channle (mono) .wav audio files as input, and generates a new .wav file as output.
Usage: `python3 pyawgn.py <input sound file> <bandwidth> <SNR> <optional output file>`\
Parameters:
- **input sound file** path and name of input .wav file
- **bandwidth** noise bandwidth in Hz
- **SNR** signal to noise ratio in dB, can be positive or negative, can have decimal
- **output file**  path and name of output .wav file, optional


Example: \
`python3 pyawgn.py bpsk_1200.wav 3000 3`\
\
This will attempt to remove the silence from the user-provided file "bpsk_1200.wav", then add white gaussian-distributed noise within a 3000 Hz bandwidth to achieve 3dB signal-to-noise ratio. The program assumes that all the signal energy in the input file is **intentional modulation**, so the input file should only contain the intended signal. No output file was specified in this example, so the program will attempt to make a new directory named "run1", increasing the number in sequence as more runs are executed, and save the output file there.
