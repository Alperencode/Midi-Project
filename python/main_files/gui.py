from tkinter import *
from music21 import *
from tkinter import ttk
import mido,random,time,threading,math

# Global variables
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)
PURE_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] 
note_bool = True
button_list = []
current_pitch = 0
global_pitch_list = []

for _ in range(8):
    global_pitch_list.append([0,0,0,0,0,0,0])

outports = mido.get_output_names()
inports = mido.get_input_names()

print(f"outputs: {outports}")
print(f"inputs: {inports}")
inport = mido.open_input(inports[-1])
output = mido.open_output(outports[-2])

print(f"output: {output}")
print(f"inport: {inport}")

class NoteButton:
    global output,app,PURE_NOTES

    last_pressed_note = None
    counter = 0
    label_counter = 0
    
    def __init__(self,note_name,octave=5,velocity=64):
        self.__note_name = note_name
        self.__pitch_value = 0
        self.__octave = octave
        self.__velocity = velocity
        self.__entry_box = None

        button = Button(
        app,
        text=note_name,
        command = lambda: (self.send_note_on(), time.sleep(0.15), self.send_note_off()) ,
        width=5,
        height=15,
        bg="white",
        fg="black",
        font=("Arial", 10, "bold"),
        )

        if note_name in PURE_NOTES:
            NoteButton.label_counter += 1.5

            label = Label(app, text=note_name)
            label.place(x=10, y= 10 + (NoteButton.label_counter * 20))

            self.__entry_box = Entry(app, width=5)

            self.__entry_box.place(x=50, y= 10 + (NoteButton.label_counter * 20))
            self.__entry_box.bind('<Return>', lambda event: self.set_pitch(int(self.__entry_box.get())))

        button.place(x=NoteButton.counter*50, y=300)

        NoteButton.counter += 1

    def change_entry_box(self):
        if self.__entry_box != None:
            self.__entry_box.delete(0,END)
            self.__entry_box.insert(0,self.get_pitch())

    def get_note_name(self):
        return self.__note_name

    def get_octave(self):
        return self.__octave

    def set_octave(self,octave):
        self.__octave = octave

    def set_velocity(self,velocity):
        self.__velocity = velocity

    def get_velocity(self):
        return self.__velocity

    def set_pitch(self,pitch):
        if pitch > 8191 or pitch < -8192:
            print("Incorrect pitch value")
        else:
            self.__pitch_value = int(pitch)

    def get_pitch(self):
        return self.__pitch_value

    def send_note_on(self):
        NoteButton.last_pressed_note = self.get_note_name()
        output.send( mido.Message("pitchwheel", pitch=self.get_pitch()) )

        if len(self.get_note_name()) == 1:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with  \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)
        else:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)
        output.send( mido.Message('note_on', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
    
    def send_note_off(self):
        output.send( mido.Message('note_off', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )

class DefaultSetEntry:
    pitch = [0,0,0,0,0,0,0]
    general_counter = 0

    place_counter1 = 0
    place_counter2 = 0
    def __init__(self,note_name,set_screen):
        self.__entry_box = None
        self.__note_name = note_name
        self.__entry_box_number = DefaultSetEntry.general_counter

        self.__entry_box = Entry(set_screen, width=5)
        if DefaultSetEntry.general_counter%2==0:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=50 + (DefaultSetEntry.place_counter1*100), y=50 )
            self.__entry_box.place(x=80 + (DefaultSetEntry.place_counter1*100), y=50)
            DefaultSetEntry.place_counter1 += 1
        else:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=50 + (DefaultSetEntry.place_counter2*100), y=100 )
            self.__entry_box.place(x=80 + (DefaultSetEntry.place_counter2*100), y=100)
            DefaultSetEntry.place_counter2 += 1
        
        self.__entry_box.bind('<Return>', lambda event: self.set_pitch(int(self.__entry_box.get())))

        DefaultSetEntry.general_counter += 1

    def set_pitch(self,pitch):
        DefaultSetEntry.pitch[self.__entry_box_number] = pitch
    
    @staticmethod
    def clear_values():
        DefaultSetEntry.general_counter = 0
        DefaultSetEntry.pitch = [0,0,0,0,0,0,0]
        DefaultSetEntry.place_counter1 = 0
        DefaultSetEntry.place_counter2 = 0

def update_pitch_list(index,pitch_values):
    global global_pitch_list
    global_pitch_list[index-1] = pitch_values

def init_set_screen():
    global PURE_NOTES

    set_screen = Tk()
    set_screen.title("Set Screen")
    set_screen.geometry("500x300")
    set_screen.resizable(False, False)

    DefaultSetEntry.clear_values()
    for item in PURE_NOTES:
        DefaultSetEntry(item,set_screen)
    
    save_label = Label(set_screen, text="Save to",font=("Arial",15,"bold"))
    save_label.place(x=220, y=175)
    save_entry = Entry(set_screen, width=10)
    save_entry.place(x=220, y=225)
    save_button = Button(set_screen, text="Save", command=lambda: update_pitch_list(int(save_entry.get()), DefaultSetEntry.pitch))
    save_button.place(x=295, y=225)

    exit_button = Button(set_screen, text="Exit", command=set_screen.destroy, width=7, height=1).pack(side=BOTTOM)

def set_default(button_list,set_number):
    global PURE_NOTES,global_pitch_list

    counter = 0
    for button in button_list:
        if button.get_note_name() in PURE_NOTES:
            button.set_pitch(global_pitch_list[set_number][counter]) 
            button.change_entry_box()
            counter += 1

def catch_pitch_value(text_widget):
    global current_pitch
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(END,current_pitch)
    text_widget.config(state=DISABLED)

def default_labels(button_list):
    global app
    info = Label(app, text="Info", font=("Arial", 15, "bold")).pack()
    sets = Label(app, text="Default Sets",font=("Arial",15,"bold")).place(x=450, y=5)
    pitch_label = Label(app, text="Saved Pitch: ",font=("Arial",15,"bold")).place(x=150, y=250)
    pitch_text = Text(app, width=5, height=1, font=("Arial",15,"bold"))
    pitch_text.place(x=275, y=250)
    pitch_text.config(state=DISABLED)
    pitch_catch = Button(app, text="Pitch Catch", command= lambda: catch_pitch_value(pitch_text)).place(x=250, y=200)

    counter = 0
    
    for i in range(8):
        if i >= 4:
            button = Button(app, text=f"{(counter+4)+1}", command= lambda set_number=(counter+4): set_default(button_list, set_number),width=3, height=2).place(x=520, y=40+counter*50)
            counter += 1
        else:
            button = Button(app, text=f"{i+1}", command= lambda set_number=(i): set_default(button_list, set_number) , width=3, height=2).place(x=460, y=40+i*50)

    save_new_button = Button(app, text="Save New", command=lambda : init_set_screen(), width=7, height=1).place(x=475, y=250)

def note_to_number(note: str, octave: int):
    note = NOTES.index(note) + 4
    note += (NOTES_IN_OCTAVE * octave)

    return note-16

def number_to_note(number: int):
    
    note = NOTES[(number % 12)-4]
    octave = math.floor((number+8)/12)

    return [note, octave]

def coming_note(msg,button_list):
    global current_pitch

    if msg.type == 'note_on':
        for item in button_list:
            # this '-8' can change depending on the instrument
            note = number_to_note(msg.note - 8)
            if item.get_note_name() == note[0]:
                item.set_octave(note[1])
                item.set_velocity(msg.velocity)
                item.send_note_on()
                break
    elif msg.type == 'note_off':
        for item in button_list:
            note = number_to_note(msg.note - 8)
            if item.get_note_name() == note[0]:
                item.set_octave(note[1])
                item.set_velocity(msg.velocity)
                item.send_note_off()
                break
    elif msg.type == 'pitchwheel':
        for item in button_list:
            if item.get_note_name() == NoteButton.last_pressed_note:
                item.set_pitch(msg.pitch)
                item.change_entry_box()
                current_pitch = msg.pitch

def read_inport(button_list):
    global note_bool
    while note_bool:
        msg = inport.receive()
        if msg.type == 'note_on' or msg.type == 'note_off' or msg.type == 'pitchwheel':
            threading.Thread(target=lambda : coming_note(msg,button_list)).start()

def main():
    global app,button_list
    app = Tk()
    app.title("GUI")
    app.geometry("600x500")
    app.resizable(False, False)


    for index,item in enumerate(NOTES):
        button_list.append(NoteButton(item))

    default_labels(button_list) 
    threading.Thread(target=lambda: read_inport(button_list)).start()

    app.mainloop()

if __name__ == "__main__":
    main()
