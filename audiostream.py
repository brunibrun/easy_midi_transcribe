import time
import numpy as np
from pyaudio import PyAudio, paContinue, paInt16

from app_setup import RING_BUFFER_SIZE, SAMPLE_RATE, WINDOW_SIZE, BPM
from midi import hz_to_midi, create_midi_file_with_notes
from spectral_analyzer import SpectralAnalyzer


class StreamProcessor(object):

    def __init__(self):
        """ Initialize StreamProcessor """
        self._spectral_analyzer = SpectralAnalyzer(
            window_size=WINDOW_SIZE,
            segments_buf=RING_BUFFER_SIZE)

        self.notes = [[0, 0, 0, 0]]

        self.search_offset = False
        
        self.search_frequency = False


    def run(self):
        """ Audio stream function using pyaudio """
        pya = PyAudio()
        self._stream = pya.open(
            format=paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=WINDOW_SIZE,
            stream_callback=self._process_frame,)

        self._stream.start_stream()

        while self._stream.is_active() and not input():
            time.sleep(0.1)

        self._stream.stop_stream()
        self._stream.close()
        pya.terminate()
        
        # save notes as midi after stream ended and print out notes
        create_midi_file_with_notes("midi_output/new_file", np.array(self.notes), BPM)
        print(np.array(self.notes))


    def _process_frame(self, data, frame_count, time_info, status_flag):
        """ Recognize events from data windows """

        # get data from current window and process data
        data_array = np.frombuffer(data, dtype=np.int16)
        self._spectral_analyzer.process_data(data_array)

        # look for events in current data window
        onset = self._spectral_analyzer.find_onset()
        frequency = self._spectral_analyzer.find_fundamental_freq(self.search_frequency)
        offset = self._spectral_analyzer.find_offset(self.search_offset, onset)

        if offset:
            offset_time_in_sec = round(time.time() - start_time, 3) - 0.001 
            self.notes[-1][3] = offset_time_in_sec # add offset time to recognized note
            self.search_offset = False # stop looking for offset

        if frequency:
            midi_note_value = int(hz_to_midi(frequency)[0])
            self.notes[-1][0] = midi_note_value # add frequency to recognized note
            self.search_frequency = False # stop looking for frequency

        if onset:
            position_in_sec = round(time.time() - start_time, 3)
            self.notes.append([0, 100, position_in_sec, (position_in_sec+0.002) ]) # add note
            self.search_offset = True # start looking for offset and frequency
            self.search_frequency = True

            print("Note detected - Position:", position_in_sec)

        return (data, paContinue)


def remote_start():
    """ Start Audio-Detection from other script """
    stream_proc = StreamProcessor()
    global start_time
    start_time = time.time()
    stream_proc.run()


if __name__ == '__main__':
    stream_proc = StreamProcessor()
    start_time = time.time()
    stream_proc.run()
