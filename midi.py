import numpy as np
from collections import namedtuple

from mido import Message, MetaMessage, MidiFile, bpm2tempo
from mido.midifiles import MidiTrack


Note = namedtuple('Note', ['value', 'velocity', 'position_in_sec', 'duration'])
RTNote = namedtuple('RTNote', ['value', 'velocity', 'duration'])


def hz_to_midi(frequencies):
    return 12 * (np.log2(np.atleast_1d(frequencies)) - np.log2(440.0)) + 69


def add_notes(track, notes, sec_per_tick):
    
    # translate second to midi-ticks
    times_in_ticks = [n[2] / sec_per_tick for n in notes]
    offsets_in_ticks = [n[3] / sec_per_tick for n in notes]

    for ix, note in enumerate(notes):

        note_int = note.astype(int) # fix seconds-integer-float problem
        
        # get duration of notes in ticks
        offset_dur_in_ticks = int(offsets_in_ticks[ix] - times_in_ticks[ix]) 
        old_offset_dur_in_ticks = int(offsets_in_ticks[ix-1] - times_in_ticks[ix-1] if ix > 0 else 0) 

        # calculate time since last midi event
        time_delta_in_ticks = int(times_in_ticks[ix] - 
            ((times_in_ticks[ix-1] if ix > 0 else 0) + old_offset_dur_in_ticks ))


        track.append(
            Message(
                'note_on',
                note=note_int[0],
                velocity=note_int[1],
                time=time_delta_in_ticks
            )
        )

        #track.append(
        #    Message(
        #        'pitchwheel',
        #        pitch=note_int[0]*50,
        #        time=10
        #    )
        #)

        track.append(
            Message(
                'note_off',
                note=note_int[0],
                velocity=note_int[1],
                time=offset_dur_in_ticks
            )
        )

def create_midi_file_with_notes(filename, notes, bpm):
    with MidiFile() as midifile:
        track = MidiTrack()
        midifile.tracks.append(track)

        track.append(Message('program_change', program=12, time=0))

        tempo = bpm2tempo(bpm)
        #tempo = int((60.0 / bpm) * 1000000) # old and not needed anymore
        track.append(MetaMessage('set_tempo', tempo=tempo))

        sec_per_tick = tempo / 1000000.0 / midifile.ticks_per_beat
        add_notes(track, notes, sec_per_tick)

        midifile.save('{}.mid'.format(filename))
