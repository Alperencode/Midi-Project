import os

from mido import MidiFile

cv1 = MidiFile('VampireKillerCV1.mid', clip=True)
cv3 = MidiFile('MIDI_sample.mid', clip=True)

del cv1.tracks[4]
del cv1.tracks[4]

cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[4])
cv1.tracks.append(cv3.tracks[5])

cv1.save('mashup.mid')