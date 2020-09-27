import file_input
import audiostream

from app_setup import RING_BUFFER_SIZE, WINDOW_SIZE, BPM, PATH_TO_FILE

# Choose Detection Mode # ToDo replace by GUI
while True:
    try:
        mode = int(input("Enter 1 for File-Input mode and 2 for Live-Detection mode: "))
    except ValueError:
        print("Only type in numbers..")
    if mode != 1 and mode != 2:
        print("Choose from 1 or 2 pls")
        continue
    else:
        break

if mode == 1: 
    print("File-Input Mode")
    file_input.FileInput(PATH_TO_FILE, "midi_output/new_fileoutput")

else:
    print("Live-Detection Mode - Press q to stop the recording")
    audiostream.remote_start()