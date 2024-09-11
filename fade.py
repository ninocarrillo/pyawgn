# Python3
# Apply measured fading to signal samples for modem performance testing.
# Nino Carrillo
# 10 Sep 2024
# Exit codes
# 1 Wrong Python version
# 2 Wrong argument count
# 3 Unable to open audio file

import sys
from scipy.io.wavfile import read as readwav
from scipy.io.wavfile import write as writewav
from numpy import int16, power, log10, sin, linspace, pi
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
		print("Not enough arguments. Usage: python3 fade.py <sound file> <fade depth dB> <period sec>")
		sys.exit(2)
	# try to open audio file
	try:
		input_sample_rate, input_audio = readwav(sys.argv[1])
	except:
		print('Unable to open audio file.')
		sys.exit(3)

	print(f'opened {sys.argv[1]}, sample rate {input_sample_rate}')

	sample_count = len(input_audio)

	# create fading profile as a sine wave from 0 dB to -(fade magnitude) dB
	fade_depth = float(sys.argv[2])
	fade_period = float(sys.argv[3])
	fade_time = linspace(0, sample_count / input_sample_rate, num=sample_count)
	fade_profile = ((fade_depth / 2) * sin(2*(pi/fade_period)*fade_time)) - (fade_depth / 2)

	faded_audio = input_audio * power(10,fade_profile / 20)

	# apply gain to noise audio
	#filtered_noise_audio = filtered_noise_audio * power(10,energy_error / 20)


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

	filename = f'output_{sys.argv[2]}_{sys.argv[3]}.wav'

	writewav(dirname+filename, input_sample_rate, faded_audio.astype(int16))


if __name__ == "__main__":
	main()
