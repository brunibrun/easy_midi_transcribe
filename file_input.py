import wave
import numpy as np

from app_setup import RING_BUFFER_SIZE, WINDOW_SIZE, BPM, PATH_TO_FILE
from midi import hz_to_midi, create_midi_file_with_notes
from spectral_analyzer import SpectralAnalyzer



def FileInput(file, output_name):
    """
    Function to transcribe audio from .wav files to .mid files.

    Parameters:
        file: wave file to be transcribed
        output_name: name (and location) of resulting midi file
    """

    # initialize variables and methods
    notes = [[0, 0, 0, 0]]
    search_offset = False
    search_frequency = False
    _spectral_analyzer = SpectralAnalyzer(
        window_size=WINDOW_SIZE,
        segments_buf=RING_BUFFER_SIZE)

    # open and prepare wave file
    wave_file = wave.open(file, mode="rb")
    sample_rate = wave_file.getframerate()
    num_cycles = wave_file.getnframes() // WINDOW_SIZE
    sec_per_cycle = WINDOW_SIZE / sample_rate


    for i in range(num_cycles): # iterate over windows in wave file
        time = i * sec_per_cycle # current time of wave window in sec

        # get data from current wave window
        data_array = np.frombuffer(wave_file.readframes(WINDOW_SIZE), np.int16, count = WINDOW_SIZE)
        
        # look for events in current data window
        onset = _spectral_analyzer.process_data(data_array)
        frequency = _spectral_analyzer.find_fundamental_freq(search_frequency, data_array)
        offset = _spectral_analyzer.find_offset(search_offset, onset)

        if offset:
            offset_time_in_sec = round(time, 3) - 0.001
            notes[-1][3] = offset_time_in_sec # add offset time to recognized note
            search_offset = False # stop looking for offset

        if frequency:
            midi_note_value = int(hz_to_midi(frequency)[0])
            notes[-1][0] = midi_note_value # add frequency to recognized note
            search_frequency = False # stop looking for frequency

        if onset:
            position_in_sec = round(time, 3)
            notes.append([0, 100, position_in_sec, (position_in_sec+0.002) ]) # add note
            search_offset = True # start looking for offset and frequency
            search_frequency = True

        if (i%42 == 0): print("Cycle", i, "of", num_cycles) # print progress update


    # save notes as midi and print recognized notes
    create_midi_file_with_notes(output_name, np.array(notes), BPM)
    print(np.array(notes))



if __name__ == '__main__':
    FileInput(PATH_TO_FILE, "midi_output/new_fileoutput")
