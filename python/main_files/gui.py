from tkinter import *
from tkinter import ttk
from music21 import *
import mido,random,time

pure_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

# output = mido.open_output('MIDIOUT2 (USB2.0-MIDI)')
outports = mido.get_output_names()
inports = mido.get_input_names()

inport = mido.open_input(inports[-1])
# output = mido.open_output(outports[-1])
output = mido.open_output('loopMIDI Port 1')
# output = mido.open_output()

print(outports)
print(output)
print(inport)

class NoteButton:
    global output,app,pure_notes

    counter = 0
    label_counter = 0

    def __init__(self,note_name,octave=5):
        self.__note_name = note_name
        self.__pitch_value = 0
        self.__octave = octave

        button = Button(
        app,
        text=note_name,
        command = lambda : self.send_midi(),
        width=5,
        height=15,
        bg="white",
        fg="black",
        font=("Arial", 10, "bold"),
        )

        if note_name in pure_notes:
            NoteButton.label_counter += 1.5

            label = Label(app, text=note_name)
            label.place(x=10, y= 10 + (NoteButton.label_counter * 20))

            entry = Entry(app, width=5)

            entry.place(x=50, y= 10 + (NoteButton.label_counter * 20))
            entry.bind('<Return>', lambda event: self.set_pitch(int(entry.get())))

        button.place(x=NoteButton.counter*50, y=300)

        NoteButton.counter += 1

    def get_note_name(self):
        return self.__note_name

    def get_octave(self):
        return self.__octave

    def set_octave(self,octave):
        self.__octave = octave

    def set_pitch(self,pitch):
        if pitch > 8191 or pitch < -8192:
            print("Incorrect pitch value")
        else:
            self.__pitch_value = int(pitch)

    def get_pitch(self):
        return self.__pitch_value

    def send_midi(self):
        print("Sending pitch signal:", self.__pitch_value)
        output.send( mido.Message("pitchwheel", pitch=self.get_pitch()) )

        print("Sending note signal:", self.__note_name)
        output.send( mido.Message('note_on', note=note_to_number(self.__note_name, self.__octave), velocity=64) )
        time.sleep(0.2)
        output.send( mido.Message('note_off', note=note_to_number(self.__note_name, self.__octave), velocity=64) )


def create_slider():
    slider = ttk.Scale(
        app,
        from_=0,
        to=100,
        orient='horizontal'
    )

    slider.set(50)
    # slider.bind("<ButtonRelease-1>", lambda event: output.send( mido.Message("pitchwheel", pitch=int(slider.get()))))
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

def number_to_note(number: int) -> tuple:
    octave = number // NOTES_IN_OCTAVE
    assert octave in OCTAVES, errors['notes']
    assert 0 <= number <= 127, errors['notes']
    note = NOTES[(number % NOTES_IN_OCTAVE) - 4]

    return [note, octave]

def main():
    global app
    app = Tk()
    app.title("GUI")
    app.geometry("600x500")
    app.resizable(False, False)

    create_slider()
    button_list = []

    for index,item in enumerate(NOTES):
        button_list.append(NoteButton(item))

    while True:
        for msg in inport.iter_pending():
            try:
                for item in button_list:
                    note = number_to_note(msg.note)
                    print(note)
                    if item.get_note_name() == note[0]:
                        item.set_octave(note[1])
                        item.send_midi()
            except:
                pass
        app.mainloop()


if __name__ == "__main__":
    main()