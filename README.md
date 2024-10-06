# signal-noise
These are tools to apply measured signal-to-noise ratio and distortion to audio samples of baseband digital modulation. They are intended to help modem users and developers measure and compare performance of different modulation and demodulation systems and techniques, under repeatable and measured conditions.
# Requirements
- Python3
- SciPy
# Tools
Three tools are provided. All three tools accept single-channle (mono) .wav audio files as their input, and generate a new .wav file as their output.
- **awgn.py** removes periods of silence and applies measured additive white gaussian noise to achieve the specified signal-to-noise ration within the specified bandwidth
- **fade.py** applies cyclic fading with the specified magnitude and period
- **multipath.py** adds a single multipath image at a swept delay time within the specified time range, and at the specified attenuation
# awgn.py
Usage: `python3 awgn.py <input sound file> <bandwidth> <SNR> <optional output file>`\
Parameters:
- **input sound file** path and name of input .wav file
- **bandwidth** noise bandwidth in Hz
- **SNR** signal to noise ratio in dB, can be positive or negative, can have decimal
- **output file**  path and name of output .wav file, optional


Example: \
`python3 awgn.py bpsk_1200.wav 3000 3`\
\
This will attempt to remove the silence from the user-provided file "bpsk_1200.wav", then add white gaussian-distributed noise within a 3000 Hz bandwidth to achieve 3dB signal-to-noise ratio. **NOTE: SILENCE REMOVAL DOESN'T WORK WELL YET, DON'T RELY ON IT.** Remove the silent sections of the audio file before using this tool. The program assumes that all the signal energy in the input file is **intentional modulation**, so the input file should only contain the intended signal. No output file was specified in this example, so the program will attempt to make a new directory named "run1", increasing the number in sequence as more runs are executed, and save the output file there.

# fade.py
Usage: `python3 fade.py <input sound file> <fade depth dB> <fade period sec> <optional output file>`\
Parameters:
- **input sound file** path and name of input .wav file
- **fade depth dB** the depth of the fade, higher number results in more attenuation
- **fade period sec** the sinusoidal period of the fade in seconds
- **output file**  path and name of output .wav file, optional

Example: \
`python3 fade.py bpsk_1200.wav 6 4`\
\
This will generate an output file with 6 dB sinusoidal fading with a 4 second period.



# multipath.py **EXPERIMENTAL - PROBABLY ALL WRONG AND DOESN'T WORK**
Usage: `python3 multipath.py <input sound file> <start milliseconds> <end milliseconds> <path dB> <optional output file>`\
Parameters:
- **input sound file** path and name of input .wav file
- **start milliseconds** the starting multipath delay in milliseconds
- **end milliseconds** the ending multipath delay in milliseconds
- **path dB** the gain of the delayed path, in dB, negative means the delay signal is weaker
- **output file**  path and name of output .wav file, optional

Example: \
`python3 multipath.py bpsk_1200.wav 0 3 -3`\
\
This will generate an output file with multipath delay that sweeps from 0 milliseconds at the start of the file to 3 milliseconds at the end of the file, and apply -3 dB gain to the delayed signal.
