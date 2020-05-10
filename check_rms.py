import pyaudio
import wave
import audioop
import time
from app_setup import SAMPLE_RATE, FFT_SIZE


CHUNK = FFT_SIZE
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = SAMPLE_RATE
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
p = pyaudio.PyAudio()
quiet_loudness = 0
active_loudness = 0


### Measure Quiet Part ###

print("--- Be quiet for 5 seconds in ---")
for i in range(4):
	print(4-i)
	time.sleep(1)


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)    # here's where you calculate the volume
    quiet_loudness += rms

average_quiet_loudness = quiet_loudness/ (CHUNK * RECORD_SECONDS)
print(round(average_quiet_loudness,3), "is the average noise in quiet situation")

stream.stop_stream()
stream.close()
p.terminate()
time.sleep(2)



### Measure Loud Part ###
p = pyaudio.PyAudio()

print("--- Now play your instrument for 5 seconds in ---")
for i in range(4):
	print(4-i)
	time.sleep(1)


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)    # here's where you calculate the volume
    active_loudness += rms

average_active_loudness = active_loudness/ (CHUNK * RECORD_SECONDS)
print(round(average_active_loudness,3), "is the average noise in active situation")

stream.stop_stream()
stream.close()
p.terminate()






