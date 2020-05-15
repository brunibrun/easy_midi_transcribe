# Easy audio to midi transcription

Small project for note recognition in mono audio-streams or in wave files and the subsequent transcription of the detected notes to a midi file.
The note recognition part still needs major improvements and is not really working yet :)

- To transcribe monophonic audio streams execute audiostream.py.

- To transcribe wave files set the path to your wave file in app_setup.py and execute file_input.py



Required packages are: 
-	mido == 1.2.9
-	numpy == 1.18.1
-	PyAudio == 0.2.11


This project is based on code from Ania Wsz's [rtmonoaudio2midi]

[rtmonoaudio2midi]: <https://github.com/aniawsz/rtmonoaudio2midi>
   
