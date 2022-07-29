import os

from mido import MidiFile

cv1 = MidiFile('VampireKillerCV1.mid', clip=True)

message_numbers = []
duplicates = []

for track in cv1.tracks:
    if len(track) in message_numbers:
        duplicates.append(track)
    else:
        message_numbers.append(len(track))

print(len(duplicates))
print(duplicates)

for track in duplicates:
    cv1.tracks.remove(track)

cv1.save('new_song.mid')