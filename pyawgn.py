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
from numpy import convolve, int16, int32, power, log10, shape
from numpy.random import normal
from os import mkdir
import string
# from matplotlib import pyplot as plot

def calc_energy(samples):
	energy = 0
	energy_history = []
	for sample in samples:
		inst_energy = sample * sample
		energy += inst_energy
		energy_history.append(inst_energy)
	# plot.figure()
	# plot.plot(10*log10(energy_history))
	# plot.show()
	return 10*log10(energy)

def find_silence(samples, sample_rate, avg_inst_energy, threshold_time):
	threshold_sample_count = int(round(threshold_time*sample_rate))
	hi_thresh_energy = power(10, (avg_inst_energy-3)/20)
	lo_thresh_energy = power(10, (avg_inst_energy-20)/20)
	index = 0
	start_silence = 0
	end_silence = 0
	state = 'silence'
	silence_markers = []
	for index in range(len(samples)):
		instantaneous_energy = power(samples[index], 2)
		if state=='silence':
			if instantaneous_energy > hi_thresh_energy:
				end_silence = index
				silence_duration = end_silence - start_silence
				if silence_duration >= threshold_sample_count:
					silence_markers.append([start_silence, end_silence, silence_duration])
					print(f'found silence from:{start_silence} to:{end_silence} length:{silence_duration}')
				state = 'no_silence'
		else:
			if instantaneous_energy < lo_thresh_energy:
				start_silence = index
				state = 'silence'
	if state=='silence':
		end_silence = index
		silence_duration = end_silence - start_silence
		if silence_duration >= threshold_sample_count:
			silence_markers.append([start_silence, end_silence, silence_duration])
			print(f'found silence from:{start_silence} to:{end_silence} length:{silence_duration}')
	return silence_markers

def rem_silence(samples, silence_markers):
	print(f'removing {len(silence_markers)} silent sections')
	trimmed_samples = []
	if len(silence_markers) > 0:
		input_index = 0
		silence_index = 0
		while silence_index < len(silence_markers):
			print(f'testing input index {input_index} silence index {silence_index}')
			if input_index <= silence_markers[silence_index][0]:
				if silence_markers[silence_index][0] > input_index:
					trimmed_samples.extend(samples[input_index:silence_markers[silence_index][0]-1])
				input_index = silence_markers[silence_index][1]
			silence_index += 1
		if silence_markers[silence_index-1][1] < (len(samples) - 1):
			trimmed_samples.extend(samples[input_index:])
	else:
		trimmed_samples.extend(samples)
	return trimmed_samples

def main():
	# check correct version of Python
	if sys.version_info < (3, 0):
		print("Python version should be 3.x, exiting")
		sys.exit(1)
	# check correct number of parameters were passed to command line
	if (len(sys.argv) > 5) or (len(sys.argv) < 4):
		print("Wrong argument count. Usage: python3 pyawgn.py <input sound file> <bandwidth> <SNR> <optional output sound file>")
		sys.exit(2)
	# try to open audio file
	try:
		input_sample_rate, input_audio = readwav(sys.argv[1])
	except:
		print('Unable to open audio file.')
		sys.exit(3)

	print(f'opened {sys.argv[1]}, sample rate {input_sample_rate}')

	# force mono
	if len(shape(input_audio)) > 1:
		input_audio = input_audio[0]

	# convert input audio to int32
	input_audio = input_audio.astype(int32)


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
	avg_inst_energy = filtered_audio_energy - (10*log10(len(filtered_audio)))
	print(f'energy in filtered input audio is {round(filtered_audio_energy,1)} dB')
	print(f'average instantaneous energy is {round(avg_inst_energy, 1)} dB')

	# find silence
	silence = find_silence(filtered_audio, input_sample_rate, avg_inst_energy, 0.01)

	# remove silence
	filtered_audio = rem_silence(filtered_audio, silence)

	# measure energy in filtered input
	filtered_audio_energy = calc_energy(filtered_audio)
	avg_inst_energy = filtered_audio_energy - (10*log10(len(filtered_audio)))
	print(f'energy in filtered and trimmed input audio is {round(filtered_audio_energy,1)} dB')
	print(f'average instantaneous energy is {round(avg_inst_energy, 1)} dB')

	# calculate energy required in noise audio
	required_noise_energy = filtered_audio_energy - float(sys.argv[3])
	print(f'energy required in noise audio is {round(required_noise_energy,1)} dB')

	# generate noise audio
	noise_audio = normal(0, 10000, len(filtered_audio)+len(bandwidth_filter) - 1)
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

	print(f'average signal to noise ratio is {round(filtered_audio_energy - filtered_noise_energy, 1)} dB')

	# generate signal + noise audio
	combined_audio = filtered_audio + filtered_noise_audio

	ratio = 32767 / max([-min(combined_audio), max(combined_audio)])
	combined_audio = ratio * combined_audio

	if len(sys.argv) == 5:
		filename = sys.argv[4]
	else:
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

		filename = dirname + f'output_awgn_{sys.argv[2]}Hz_{sys.argv[3]}dB.wav'

	writewav(filename, input_sample_rate, combined_audio.astype(int16))
	print(f'wrote file {filename}')


if __name__ == "__main__":
	main()
