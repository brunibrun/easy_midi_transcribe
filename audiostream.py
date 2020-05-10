import time
import numpy as np
from pyaudio import PyAudio, paContinue, paInt16

from app_setup import (RING_BUFFER_SIZE, SAMPLE_RATE, WINDOW_SIZE, BPM)
from midi import hz_to_midi, create_midi_file_with_notes
from spectral_analyzer import SpectralAnalyser

notes = [[0, 0, 0, 0]]
search_offset = False
search_frequency = False


class StreamProcessor(object):

    FREQS_BUF_SIZE = 11

    def __init__(self):
        # initialize self
        self._spectral_analyser = SpectralAnalyser(
            window_size=WINDOW_SIZE,
            segments_buf=RING_BUFFER_SIZE)

    def run(self):
        # start audio input 
        pya = PyAudio()
        self._stream = pya.open(
            format=paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=WINDOW_SIZE,
            stream_callback=self._process_frame,
        )

        self._stream.start_stream()

        while self._stream.is_active() and not input():
            time.sleep(0.1)

        self._stream.stop_stream()
        self._stream.close()
        pya.terminate()
        
        print(np.array(notes))
        # save notes as midi
        create_midi_file_with_notes("new_file", np.array(notes), BPM)


    def _process_frame(self, data, frame_count, time_info, status_flag):
        
        global search_offset, search_frequency, notes

        data_array = np.frombuffer(data, dtype=np.int16)

        onset = self._spectral_analyser.process_data(data_array)
        frequency = self._spectral_analyser.find_fundamental_freq(search_frequency, data_array)
        offset = self._spectral_analyser.find_offset(search_offset, onset)

        if offset:
            offset_time_in_sec = round(time.time() - start_time, 3) - 0.001 
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
            position_in_sec = round(time.time() - start_time, 3)
            # add note to list - midi value(=0); velocity; start-position; end-position
            notes.append([0, 100, position_in_sec, (position_in_sec+0.002) ])
            # start looking for offsets and frequency
            search_offset = True
            search_frequency = True

            print("Note detected - Position:", position_in_sec)

        return (data, paContinue)





if __name__ == '__main__':
    stream_proc = StreamProcessor()
    start_time = time.time()
    stream_proc.run()
