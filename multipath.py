# Python3
# Add measured noise to signal samples for modem performance testing.
# Nino Carrillo
# 10 Sep 2024
# Exit codes
# 1 Wrong Python version
# 2 Wrong argument count
# 3 Unable to open audio file
# 4 Unable to generate filter at requested bandwidth

import sys
from scipy.io.wavfile import read as readwav
from scipy.io.wavfile import write as writewav
from scipy.signal import firwin
from numpy import zeros, concatenate, int16
from numpy.random import normal
from os import mkdir
import string

def calc_energy(samples):
	energy = 0
	for sample in samples:
		energy += sample * sample
	return 10*log10(energy)

def main():
	# check correct version of Python
	if sys.version_info < (3, 0):
		print("Python version should be 3.x, exiting")
		sys.exit(1)
	# check correct number of parameters were passed to command line
	if len(sys.argv) != 4:
		print("Wrong argument count. Usage: python3 multipath.py <sound file> <start milliseconds> <end milliseconds>")
		sys.exit(2)
	# try to open audio file
	try:
		input_sample_rate, input_audio = readwav(sys.argv[1])
	except:
		print('Unable to open audio file.')
		sys.exit(3)

	print(f'opened {sys.argv[1]}, sample rate {input_sample_rate}')

	sample_count = len(input_audio)

	# calculate multipath sample delay
	start_milliseconds = float(sys.argv[2]) * input_sample_rate / 1000
	end_milliseconds = float(sys.argv[3]) * input_sample_rate / 1000
	delta_milliseconds = start_milliseconds - end_milliseconds
	increment_milliseconds = delta_milliseconds / sample_count

	input_audio_copy = input_audio.copy()
	millisecond_delay = start_milliseconds
	for i in range(sample_count):
		sample_delay = int(round(millisecond_delay * input_sample_rate / 1000,0))
		delay_index = i - sample_delay
		while delay_index < 0:
			delay_index += sample_count
		while delay_index > (sample_count - 1):
			delay_index -= sample_count
		input_audio[i] += int(input_audio_copy[delay_index])
		millisecond_delay += increment_milliseconds

	# Make 16 bit compatible
	#input_audio = input_audio * 32767 / max(input_audio)


	#generate a new directory for the outputs
	run_number = 0
	print('trying to make a new directory')
	while True:
		run_number = run_number + 1
		dirname = f'./run{run_number}/'
		try:
			mkdir(dirname)
		except:
			print(dirname + ' exists')
			continue
		break
	print(f'made directory {dirname}')

	filename = f'output_{sys.argv[2]}-{sys.argv[3]}ms.wav'

	writewav(dirname+filename, input_sample_rate, input_audio.astype(int16))


if __name__ == "__main__":
	main()
