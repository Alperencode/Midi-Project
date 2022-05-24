from mido import MidiFile

mid = MidiFile('VampireKillerCV1.mid', clip=True)

for track in mid.tracks:
    for msg in track:
        print(msg)