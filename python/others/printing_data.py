import os

from mido import MidiFile

cv1 = MidiFile('MIDI_sample.mid', clip=True)

for track in cv1.tracks:
    for message in track:
        print(message)