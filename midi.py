import numpy as np
from collections import namedtuple

from mido import Message, MetaMessage, MidiFile, bpm2tempo
from mido.midifiles import MidiTrack


def hz_to_midi(frequencies):
    """ Turn hertz frequency into midi note """
    return 12 * (np.log2(np.atleast_1d(frequencies)) - np.log2(440.0)) + 69


def add_notes(track, notes, sec_per_tick):
    """ Add notes to a midi track """
    
    # translate second to midi-ticks
    times_in_ticks = [n[2] / sec_per_tick for n in notes]
    offsets_in_ticks = [n[3] / sec_per_tick for n in notes]


    for ix, note in enumerate(notes): # iterate over detected notes

        note_int = note.astype(int) # fix seconds-integer-float problem with array
        
        # get duration of notes in ticks
        offset_dur_in_ticks = int(offsets_in_ticks[ix] - times_in_ticks[ix]) 
        old_offset_dur_in_ticks = int(offsets_in_ticks[ix-1] - times_in_ticks[ix-1] if ix > 0 else 0) 

        # calculate time since last midi event
        time_delta_in_ticks = int(times_in_ticks[ix] - 
            ((times_in_ticks[ix-1] if ix > 0 else 0) + old_offset_dur_in_ticks ))

        # adds note to midi track
        track.append(Message(
                'note_on',
                note=note_int[0],
                velocity=note_int[1],
                time=time_delta_in_ticks)
        )
        track.append(Message(
                'note_off',
                note=note_int[0],
                velocity=note_int[1],
                time=offset_dur_in_ticks)
        )

def create_midi_file_with_notes(filename, notes, bpm):
    """ Write notes from array to a midi file """

    # initialize midi track
    with MidiFile() as midifile:
        track = MidiTrack()
        midifile.tracks.append(track)

        # prepare midi track for appending notes
        track.append(Message('program_change', program=12, time=0))
        track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

        # compute time in midi ticks
        sec_per_tick = bpm2tempo(bpm) / 1000000.0 / midifile.ticks_per_beat

        # write notes to track
        add_notes(track, notes, sec_per_tick)

        # save as .mid file
        midifile.save('{}.mid'.format(filename))
