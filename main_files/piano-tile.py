# This program was created for checking midi signals and trying their attributes to develop Midi-Project
from music21 import *
import pygame,mido,math

pygame.init()

# define colors
BLACK = [  0,   0,   0]
WHITE = [255, 255, 255]

# define note lists
note_list = []
note_list_off = []

# define midi ports
outports = mido.get_output_names()
inports = mido.get_input_names()

inport = mido.open_input(inports[-1])
output = mido.open_output(outports[-2])

print(f"input {inport}")
print(f"output {output}")

# setting up the screen
SIZE = [1000, 500]
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Python MIDI")

# tracking time
clock = pygame.time.Clock()

# Number - note converter functions
notes = ['G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(notes)

def number_to_note(number: int) -> tuple:
    octave = math.floor((number+8)/12)
    note = notes[number % 12]

    return [note, octave]

done = False
stream1 = stream.Stream()
while done == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
    
    def converter(value, control):
        # if control: pitch to cent
        # else: cent to pitch
        if control:
            NewValue = (((value - (-8192)) * 200) / 16383) + (-100)
        else:
            NewValue = (((value - (-100)) * 16383) / 200) + (-8192)
        return int(NewValue)

    for msg in inport.iter_pending():
        try:
            if msg.type == 'pitchwheel':
                cent = converter(msg.pitch, True)
                pitch = converter(cent, False)
                print(f"pitch {pitch}")
                print(f"cent {cent}")
        except:
            print(msg)
           
    # while note list is not empty
    for i in range(len(note_list)):
        # draw note to the screen
        # with white color 
        # note in center and 10 for radius
        pygame.draw.circle(screen, WHITE, note_list[i], 10)
        
        note_list[i][1] += 1
    
    # flipping screen so notes will come from top
    pygame.display.flip()
    
    # if note is ended, draw a black so it will disappear
    for i in range(len(note_list_off)):
        pygame.draw.circle(screen, BLACK, note_list_off[i], 10)
        note_list_off[i][1] += 1   
    
    # clock defines how fast the notes are going to fall
    # speed = 1000/clock miliseconds
    # so 1000/200 = 5
    clock.tick(200)

pygame.quit()
