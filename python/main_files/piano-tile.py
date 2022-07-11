# This program created for checking midi signals and trying their attributes to develop gui.py
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
    
    # while notes are coming in
    for msg in inport.iter_pending():
        try:
            # print(number_to_note(msg.note))
            print(msg.velocity)
            
            converted_note = number_to_note(msg.note)

            # print(type(msg.note))
            
            n = note.Note(str(converted_note[0]) + str(converted_note[1]))

            # print(type(n))
            stream1.append(n)
            
            n = msg.note
            x=(n-47)*10 

            # if note is on
            if msg.velocity>0:
                # add note to list
                note_list.append([x, 0])
            else:
                # add note to off list
                note_list_off.append([x, 0])
        except:
            print(msg.velocity)
            print(number_to_note(msg.note-8))
            print(msg.note-8)
           
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
