FFT_SIZE = 1024
WINDOW_SIZE = 2048
THRESHOLD_WINDOW_SIZE = 11 #20 # was 11
THRESHOLD_MULTIPLIER = 10 # was 10 by default - 9 now more notes
FREQUENCY_RANGE = (80, 1200)

DEFAULT_BPM = 120
DEFAULT_PITCH = 64
DEFAULT_VELOCITY = 64

BPM = 110

RING_BUFFER_SIZE = 40
FRAMES_PER_BUFFER = 4096
SAMPLE_RATE = 44100

AVERAGE_ACTIVE_NOISE = 2 
AVERAGE_QUIET_NOISE = 40 # works great with microphone
LOUDNESS_TRESHHOLD = 4