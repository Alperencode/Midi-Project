import pygame
import mido

pygame.init()

# define colors
BLACK = [  0,   0,   0]
WHITE = [255, 255, 255]

# define note lists
note_list = []
note_list_off = []

# define midi ports
outport=mido.open_output()
inport=mido.open_input()

# setting up the screen
SIZE = [1000, 500]
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Python MIDI")

# tracking time
clock = pygame.time.Clock()

done = False
while done == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
    
    # while notes are coming in
    for msg in inport.iter_pending():
        try:
            print(msg)
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
            print(msg)
           
    
    # while note list is not empty
    for i in range(len(note_list)):
        # draw note to the screen
        # with white color 
        # note in center and 10 for radius
        pygame.draw.circle(screen, WHITE, note_list[i], 10)
        
        # note_list is matrix?
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