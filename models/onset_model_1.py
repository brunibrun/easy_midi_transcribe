import wave
import numpy as np

from app_setup import (RING_BUFFER_SIZE, WINDOW_SIZE, BPM)
from midi import hz_to_midi, create_midi_file_with_notes
from spectral_analyzer import SpectralAnalyser
from metrics import onsetLossFunction


def onsetDetection(wave_file):

    notes = [[0]]
    stop_everything = False

    wave_file = wave.open(wave_file, mode="rb")
    sample_rate = wave_file.getframerate()
    num_cycles = wave_file.getnframes() // WINDOW_SIZE
    sec_per_cycle = WINDOW_SIZE / sample_rate

    _spectral_analyser = SpectralAnalyser(
        window_size=WINDOW_SIZE,
        segments_buf=RING_BUFFER_SIZE)

    # iterate over windows
    for i in range(num_cycles):

        time = i * sec_per_cycle

        # fix problem, that not every frame is used..
        #data_array = np.frombuffer(wave_file.readframes(WINDOW_SIZE), np.int16)
        data_array = np.frombuffer(wave_file.readframes(WINDOW_SIZE), np.int16, count = WINDOW_SIZE)
        #data_array = np.frombuffer(wave_file.readframes(WINDOW_SIZE), dtype='<i2')
        #print(WINDOW_SIZE, data_array.shape, data_array.dtype)

        onset = _spectral_analyser.process_data(data_array)


        if onset:
            position_in_sec = round(time, 3)
            # add note to list - midi value(=0); velocity; start-position; end-position
            notes.append([0, 100, position_in_sec, (position_in_sec+0.002) ])
            # start looking for offsets and frequency
            search_offset = True
            search_frequency = True

        if (i%20 == 0): print("Cycle", i, "of", num_cycles) 

    print(np.array(notes))
    # save notes as midi
    create_midi_file_with_notes(output_name, np.array(notes), BPM)





if __name__ == '__main__':
    FileInput("/Users/bruno/Desktop/Python-Test-Wave.wav", "new_fileoutput")
    #FileInput("/Users/bruno/Documents/guitar_detection/wavy.wav", "new_file_fileinput")
