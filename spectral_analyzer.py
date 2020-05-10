import itertools
from collections import deque
import numpy as np

from app_setup import (
    SAMPLE_RATE,
    THRESHOLD_MULTIPLIER,
    THRESHOLD_WINDOW_SIZE,
    FREQUENCY_RANGE,
    AVERAGE_QUIET_NOISE,
    LOUDNESS_TRESHHOLD)


class SpectralAnalyser(object):

    FREQUENCY_RANGE = FREQUENCY_RANGE

    def __init__(self, window_size, segments_buf=None):
        self._window_size = window_size
        if segments_buf is None:
            segments_buf = int(SAMPLE_RATE / window_size)
        self._segments_buf = segments_buf

        self._thresholding_window_size = THRESHOLD_WINDOW_SIZE
        assert self._thresholding_window_size <= segments_buf

        self._last_spectrum = np.zeros(window_size, dtype=np.int16)
        self._second_last_spectrum = np.zeros(window_size, dtype=np.int16)
        self._last_data = np.zeros(window_size, dtype=np.int16)

        self._last_flux = deque(
            np.zeros(segments_buf, dtype=np.int16), segments_buf)
        self._last_prunned_flux = 0

        self._hanning_window = np.hanning(window_size)
        # The zeros which will be used to double each segment size
        self._inner_pad = np.zeros(window_size)

        # ignore first peak after starting application
        self._first_peak = True


    def _get_flux_for_thresholding(self):
        return list(itertools.islice(
            self._last_flux,
            self._segments_buf - self._thresholding_window_size,
            self._segments_buf))


    def find_onset(self, spectrum):
        """
        Calculate difference between current and last spectrum
        then apply thresholding function and check if peak occurred
        """
        last_spectrum = self._last_spectrum
        flux = sum([max(spectrum[n] - last_spectrum[n], 0)
            for n in range(self._window_size)])
        self._last_flux.append(flux)

        thresholded = np.mean(
            self._get_flux_for_thresholding()) * THRESHOLD_MULTIPLIER
        prunned = flux - thresholded if thresholded <= flux else 0
        peak = prunned if prunned > self._last_prunned_flux else 0
        self._last_prunned_flux  = prunned
        return peak


    def find_offset(self, search_offset, freq0):
        if search_offset:

            # if new onset return offset
            if freq0:
                return True
            
            spectrum = self._last_spectrum
            last_spectrum = self._second_last_spectrum
            loud_tresh = AVERAGE_QUIET_NOISE * LOUDNESS_TRESHHOLD

            # if very quiet return offset
            if np.sum(spectrum)<loud_tresh and np.sum(last_spectrum)<loud_tresh:
                return True


    def find_fundamental_freq(self, search_frequency, samples):
        if search_frequency:

            # search for maximum between 0.08ms (=1200Hz) and 2ms (=500Hz)
            min_freq, max_freq = self.FREQUENCY_RANGE
            start = int(SAMPLE_RATE / max_freq)
            end = int(SAMPLE_RATE / min_freq)

            samples = self._last_data

            cepstrum = self.cepstrum(samples)
            narrowed_cepstrum = cepstrum[start:end]

            peak_ix = narrowed_cepstrum.argmax()
            freq0 = SAMPLE_RATE / (start + peak_ix)
            if freq0 < min_freq or freq0 > max_freq:
                # Ignore the note out of the desired frequency range
                return
            return freq0


    def process_data(self, data):
        
        spectrum = self.autopower_spectrum(data)
        onset = self.find_onset(spectrum)

        self._second_last_spectrum = self._last_spectrum
        self._last_spectrum = spectrum
        self._last_data = data

        # ignore first peak
        if self._first_peak:
            self._first_peak = False
            return

        if onset:
            return True

    def autopower_spectrum(self, samples):
        """
        Calculates a power spectrum of the given data using the Hamming window.
        """
        # TODO: check the length of given samples; treat differently if not
        # equal to the window size
        windowed = samples * self._hanning_window
        # Add 0s to double the length of the data
        padded = np.append(windowed, self._inner_pad)
        # Take the Fourier Transform and scale by the number of samples
        spectrum = np.fft.fft(padded) / self._window_size
        autopower = np.abs(spectrum * np.conj(spectrum))
        return autopower[:self._window_size]

    def cepstrum(self, samples):
        """
        Calculates the complex cepstrum of a real sequence.
        """
        spectrum = np.fft.fft(samples)
        log_spectrum = np.log(np.abs(spectrum))
        cepstrum = np.fft.ifft(log_spectrum).real
        return cepstrum
