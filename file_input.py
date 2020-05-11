import wave
import numpy as np

from app_setup import (RING_BUFFER_SIZE, WINDOW_SIZE, BPM, PATH_TO_FILE)
from midi import hz_to_midi, create_midi_file_with_notes
from spectral_analyzer import SpectralAnalyser



def FileInput(file, output_name):

    notes = [[0, 0, 0, 0]]
    search_offset = False
    search_frequency = False
    stop_everything = False

    wave_file = wave.open(file, mode="rb")
    sample_rate = wave_file.getframerate()
    num_cycles = wave_file.getnframes() // WINDOW_SIZE
    sec_per_cycle = WINDOW_SIZE / sample_rate

    _spectral_analyser = SpectralAnalyser(
        window_size=WINDOW_SIZE,
        segments_buf=RING_BUFFER_SIZE)

    # iterate over windows
    for i in range(num_cycles):

        time = i * sec_per_cycle

        data_array = np.frombuffer(wave_file.readframes(WINDOW_SIZE), np.int16, count = WINDOW_SIZE)

        onset = _spectral_analyser.process_data(data_array)
        frequency = _spectral_analyser.find_fundamental_freq(search_frequency, data_array)
        offset = _spectral_analyser.find_offset(search_offset, onset)

        if offset:
            offset_time_in_sec = round(time, 3) - 0.001 
            # add offset time to previous note
            notes[-1][3] = offset_time_in_sec
            # stop looking for offsets
            search_offset = False

        if frequency:
            midi_note_value = int(hz_to_midi(frequency)[0])
            # add frequency to previous note
            notes[-1][0] = midi_note_value
            # stop looking for frequency
            search_frequency = False

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
    FileInput(PATH_TO_FILE, "midi_output/new_fileoutput")
