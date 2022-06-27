from tkinter import *
from tkinter import ttk
from music21 import *
import mido,random,time

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

output = mido.open_output('loopMIDI Port 1')
# inport=mido.open_input()

app = Tk()
app.title("GUI Basics")
app.geometry("600x500")
app.resizable(False, False)

# print(output)

slider = ttk.Scale(
    app,
    from_=-8192,
    to=8191,
    orient='horizontal'
)

slider.set(64)
slider.bind("<ButtonRelease-1>", lambda event: output.send( mido.Message("pitchwheel", pitch=int(slider.get()))))
slider.pack()

def note_to_number(note: str, octave: int) -> int:
    # handling errors
    assert note in NOTES, errors['notes']
    assert octave in OCTAVES, errors['notes']

    # converting note to number
    note = NOTES.index(note)
    note += (NOTES_IN_OCTAVE * octave)

    assert 0 <= note <= 127, errors['notes']

    return note


def note_pressed(note_name):
    print(f"{note_name} pressed")

    # Default messeage format: output.send(mido.Message('note_on', note=60, velocity=64))
    
    # sending midi message
    random_int = random.randint(0, 9)
    output.send( mido.Message('note_on', note=note_to_number(note_name, 5), velocity=64) )
    time.sleep(0.2)
    output.send( mido.Message('note_off', note=note_to_number(note_name, 5), velocity=64) )


def create_note_button(note_name):
    
    button = Button(
    app,
    text=note_name,
    command = lambda : note_pressed(note_name),
    width=5,
    height=15,
    bg="white",
    fg="black",
    font=("Arial", 10, "bold"),
    )
    
    button.pack()
    return button


for index,item in enumerate(NOTES):
    button = create_note_button(item)
    button.place(x=index*50, y=300)
    # button.pack(side=BOTTOM)
    # button.grid(row=0, column=i)

app.mainloop()