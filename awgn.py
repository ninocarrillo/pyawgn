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
from numpy import convolve, int16, power, log10
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
		print("Not enough arguments. Usage: python3 awgn.py <sound file> <bandwidth> <SNR>")
		sys.exit(2)
	# try to open audio file
	try:
		input_sample_rate, input_audio = readwav(sys.argv[1])
	except:
		print('Unable to open audio file.')
		sys.exit(3)

	print(f'opened {sys.argv[1]}, sample rate {input_sample_rate}')

	# Generate filter for specified bandwidth
	try:
		bandwidth_filter = firwin(
			250, # tap count
			[ float(sys.argv[2]) ], # bandwidth
			pass_zero='lowpass',
			fs=input_sample_rate,
			scale=True
		)
	except:
		print(f'unable to generate filter at requested bandwidth {sys.argv[2]}')
		sys.exit(4)

	# ensure gain of 0dB
	bandwidth_filter = bandwidth_filter / sum(bandwidth_filter)

	# filter input audio to specified bandwidth
	filtered_audio = convolve(input_audio, bandwidth_filter, 'valid')

	# measure energy in filtered input
	filtered_audio_energy = calc_energy(filtered_audio)
	print(f'energy in filtered input audio is {round(filtered_audio_energy,1)} dB')

	# calculate energy required in noise audio
	required_noise_energy = filtered_audio_energy - float(sys.argv[3])
	print(f'energy required in noise audio is {round(required_noise_energy,1)} dB')

	# generate noise audio
	noise_audio = normal(0, 10000, len(input_audio))
	filtered_noise_audio = convolve(noise_audio, bandwidth_filter, 'valid')
	filtered_noise_energy = calc_energy(filtered_noise_audio)
	print(f'filtered noise energy is {round(filtered_noise_energy, 1)} dB')

	# determined gain required
	energy_error = required_noise_energy - filtered_noise_energy
	print(f'energy error is {round(energy_error, 1)} dB')

	print('adjusting noise energy')

	# apply gain to noise audio
	filtered_noise_audio = filtered_noise_audio * power(10,energy_error / 20)

	filtered_noise_energy = calc_energy(filtered_noise_audio)
	print(f'filtered noise energy is now {round(filtered_noise_energy,1)} dB')

	print(f'signal to noise ratio is {round(filtered_audio_energy - filtered_noise_energy, 1)} dB')

	# generate signal + noise audio
	combined_audio = filtered_audio + filtered_noise_audio

	# Make 16 bit compatible

	combined_audio = combined_audio * 32767 / max([abs(min(combined_audio)), max(combined_audio)])

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

	writewav(dirname+filename, input_sample_rate, combined_audio.astype(int16))


if __name__ == "__main__":
	main()
