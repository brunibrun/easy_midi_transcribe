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


class SpectralAnalyzer(object):

    # initialize frequency range
    FREQUENCY_RANGE = FREQUENCY_RANGE


    def __init__(self, window_size, segments_buf=None):
        """ initialize spectral analyzer """

        # initialize window sizes
        self._window_size = window_size
        if segments_buf is None:
            segments_buf = int(SAMPLE_RATE / window_size)
        self._segments_buf = segments_buf

        self._thresholding_window_size = THRESHOLD_WINDOW_SIZE
        assert self._thresholding_window_size <= segments_buf

        # initialize data windows with zeros
        self._last_spectrum = np.zeros(window_size, dtype=np.int16)
        self._second_last_spectrum = np.zeros(window_size, dtype=np.int16)
        self._last_data = np.zeros(window_size, dtype=np.int16)

        self._last_flux = deque(
            np.zeros(segments_buf, dtype=np.int16), segments_buf)
        self._last_prunned_flux = 0

        # initialize window smoothing function
        self._hanning_window = np.hanning(window_size)
        
        self._inner_pad = np.zeros(window_size) # zeros to double each segment size

        self._first_peak = True # ignore first peak after starting application



    def _get_flux_for_thresholding(self):
        """ return last fluxes from previous windows """
        return list(itertools.islice(
            self._last_flux,
            self._segments_buf - self._thresholding_window_size,
            self._segments_buf))


    def find_onset(self, spectrum):
        """ 
        calculate difference between current and last spectrum
        and apply thresholding function to check if peak occurred
        """

        # get last spectrum and flux
        last_spectrum = self._last_spectrum
        flux = sum([max(spectrum[n] - last_spectrum[n], 0)
            for n in range(self._window_size)])
        self._last_flux.append(flux)

        # compute difference and threshold it
        thresholded = np.mean(
            self._get_flux_for_thresholding()) * THRESHOLD_MULTIPLIER
        prunned = flux - thresholded if thresholded <= flux else 0
        
        # check if peak occured
        peak = prunned if prunned > self._last_prunned_flux else 0
        self._last_prunned_flux  = prunned
        return peak


    def find_offset(self, search_offset, onset):
        """ 
        find if offset occured. returns offset if new onset is detected 
        or if volume is sufficiently quiet
        """

        if search_offset: # only look for offset if note is active

            # if new onset is detected return offset for previous note
            if onset: 
                return True
            
            # compare loudness of last frames with current frame
            spectrum = self._last_spectrum
            last_spectrum = self._second_last_spectrum
            loud_tresh = AVERAGE_QUIET_NOISE * LOUDNESS_TRESHHOLD

            # if current window sufficiently quiet return offset
            if np.sum(spectrum)<loud_tresh and np.sum(last_spectrum)<loud_tresh:
                return True


    def find_fundamental_freq(self, search_frequency, samples):
        """ find fundamental frequency of window by analyzing cepstrum """

        if search_frequency: # only look for frequency if note is active

            min_freq, max_freq = self.FREQUENCY_RANGE # get frequency range

            # convert frequency range to 1/seconds (e.g 500Hz = 1/ 2ms)
            start = int(SAMPLE_RATE / max_freq)
            end = int(SAMPLE_RATE / min_freq)

            # get last sample
            samples = self._last_data

            # get cepstrum and cut off  unwanted frequencies 
            cepstrum = self.cepstrum(samples)
            narrowed_cepstrum = cepstrum[start:end]

            # look for maximum frequency in cepstrum and return it
            peak_ix = narrowed_cepstrum.argmax()
            freq0 = SAMPLE_RATE / (start + peak_ix)
            
            # ignore irrelevant frequencies
            if freq0 < min_freq or freq0 > max_freq: 
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
