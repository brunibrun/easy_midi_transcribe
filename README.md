# Easy audio to midi transcription

a small project to detect notes in mono audio-streams or in wave files and the subsequent transcription of the notes to a midi file. the note recognition part still needs major improvements and is not really functional yet :)

- to transcribe monophonic audio streams execute audiostream.py

- to transcribe wave files update the path to your wave file in app_setup.py and execute file_input.py


required packages are: 
-	mido == 1.2.9
-	numpy == 1.18.1
-	PyAudio == 0.2.11 (only needed for the audio-stream)


this project is based on code from Ania Wsz's [rtmonoaudio2midi]

[rtmonoaudio2midi]: <https://github.com/aniawsz/rtmonoaudio2midi>
   
