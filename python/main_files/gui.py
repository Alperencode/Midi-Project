from tkinter import *
from music21 import *
from tkinter import ttk
import mido,random,time,threading,math

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)

outports = mido.get_output_names()
inports = mido.get_input_names()

print(f"outputs: {outports}")
print(f"inputs: {inports}")
inport = mido.open_input(inports[-1])
output = mido.open_output(outports[-2])

print(f"output: {output}")
print(f"inport: {inport}")

class NoteButton:
    global output,app

    pure_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    counter = 0
    label_counter = 0
    
    def __init__(self,note_name,octave=5):
        self.__note_name = note_name
        self.__pitch_value = 0
        self.__octave = octave

        button = Button(
        app,
        text=note_name,
        command = self.send_midi,
        width=5,
        height=15,
        bg="white",
        fg="black",
        font=("Arial", 10, "bold"),
        )

        if note_name in NoteButton.pure_notes:
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
        # print("Sending pitch signal:", self.__pitch_value)
        output.send( mido.Message("pitchwheel", pitch=self.get_pitch()) )

        # print("Sending note signal:", self.__note_name)
        if len(self.__note_name) == 1:
            Label(app, text=f"Sending {self.__note_name} octave {self.__octave} with  {self.__pitch_value} pitch",font=("Arial",15,"bold")).place(x=170, y=45)
        else:
            Label(app, text=f"Sending {self.__note_name} octave {self.__octave} with {self.__pitch_value} pitch",font=("Arial",15,"bold")).place(x=170, y=45)
        output.send( mido.Message('note_on', note=note_to_number(self.__note_name, self.__octave), velocity=64) )
        time.sleep(0.2)
        output.send( mido.Message('note_off', note=note_to_number(self.__note_name, self.__octave), velocity=64) )


def create_slider():
    # Currently slider has no function
    slider = ttk.Scale(
        app,
        from_=0,
        to=100,
        orient='horizontal'
    )

    slider.set(50)
    # slider.bind("<ButtonRelease-1>", lambda event: output.send( mido.Message("pitchwheel", pitch=int(slider.get()))))
    slider.pack()

def note_to_number(note: str, octave: int):
    note = NOTES.index(note) + 4
    note += (NOTES_IN_OCTAVE * octave)

    return note-16

def number_to_note(number: int):
    
    note = NOTES[(number % 12)-4]
    octave = math.floor((number+8)/12)

    return [note, octave]

def coming_note(msg,button_list):
    if msg.type == 'note_on':
        for item in button_list:
            # this '-8' can change depending on the instrument
            note = number_to_note(msg.note - 8)
            if item.get_note_name() == note[0]:
                item.set_octave(note[1])
                item.send_midi()
                break

def read_inport(button_list):
    while True:
        msg = inport.receive()
        if msg.type == 'note_on':
            threading.Thread(target=lambda : coming_note(msg,button_list)).start()

def main():
    global app
    app = Tk()
    app.title("GUI")
    app.geometry("600x500")
    app.resizable(False, False)
    
    label = Label(app, text="Info", font=("Arial", 15, "bold"))
    label.pack()
    
    # create_slider()
    button_list = []

    for index,item in enumerate(NOTES):
        button_list.append(NoteButton(item))

    threading.Thread(target=lambda: read_inport(button_list)).start()

    app.mainloop()
    exit()


if __name__ == "__main__":
    main()
