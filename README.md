# Easy audio to midi transcription

Small project for note recognition in mono audio-streams or in wave files and the subsequent transcription to a midi file.
- The note recognition still needs major improvements

**- To transcribe monophonic audio streams, execute audiostream.py.**

**- To transcribe wave files, set the path to your wave file in app_setup.py and execute file_input.py**



Required packages are: 
-	mido == 1.2.9
-	numpy == 1.18.1
-	PyAudio == 0.2.11


This project is based upon code from Ania Wsz's [rtmonoaudio2midi] 
and was created in python 3.7.

[rtmonoaudio2midi]: <https://github.com/aniawsz/rtmonoaudio2midi>
   
