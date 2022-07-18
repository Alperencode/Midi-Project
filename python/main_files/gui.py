from tkinter import *
from music21 import *
from tkinter import ttk
import mido,random,time,threading,math

# Global variables
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
PURE_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] 
MESSAGE_TYPES = ['note_on','note_off','pitchwheel','control_change']
OCTAVES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
global_button_list = []
global_pitch_list = []
current_pitch = 0
note_bool = True

# setting 8 default sets to values to 0
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
    global output,app

    last_pressed_note = None
    control_change = mido.Message('control_change', control=1, value=0)
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
        command = lambda: (self.send_note_on(), self.send_pitch_wheel() , time.sleep(0.15), self.send_note_off()),
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
            self.__entry_box.bind('<Return>', lambda event: self.set_pitch(self.__entry_box.get()))

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
        try:
            pitch = int(pitch)
            if pitch > 8191 or pitch < -8192:
                self.setting_pitch_error("Pitch out of range")
            else:
                self.__pitch_value = int(pitch)
        except:
            self.setting_pitch_error("Pitch is not an int")

    def setting_pitch_error(self,error_message):
            print(f"\a{error_message}")
            self.__entry_box.delete(0,END)
            self.__entry_box.insert(0,self.get_pitch())

    def get_pitch(self):
        return self.__pitch_value

    def send_note_on(self):
        NoteButton.last_pressed_note = self.get_note_name()
        # output.send( mido.Message("pitchwheel", pitch=self.get_pitch()))
        output.send( NoteButton.control_change )

        if len(self.get_note_name()) == 1:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with  \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)
        else:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)

        output.send( mido.Message('note_on', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
    
    def send_pitch_wheel(self,*args):
        if args:
            output.send( mido.Message('pitchwheel', pitch=args[0]) )
        else:
            output.send( mido.Message('pitchwheel', pitch=self.get_pitch()) )

    def send_note_off(self):
        output.send( mido.Message('note_off', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
        output.send( NoteButton.control_change )

    @staticmethod
    def change_control():
        output.send(NoteButton.control_change)

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
        
        self.__entry_box.bind('<Return>', lambda event: self.set_pitch(self.__entry_box.get()))

        DefaultSetEntry.general_counter += 1

    def setting_pitch_error(self,error_message):
            print(f"\a{error_message}")
            self.__entry_box.delete(0,END)
            self.__entry_box.insert(0,self.get_pitch())

    def set_pitch(self,pitch):
        try:
            pitch = int(pitch)
            if pitch > 8191 or pitch < -8192:
                self.setting_pitch_error("Pitch out of range")
            else:
                DefaultSetEntry.pitch[self.__entry_box_number] = pitch
        except:
            self.setting_pitch_error("Pitch is not an int")

    def get_pitch(self):
        return DefaultSetEntry.pitch[self.__entry_box_number]    

    @staticmethod
    def clear_values():
        DefaultSetEntry.general_counter = 0
        DefaultSetEntry.pitch = [0,0,0,0,0,0,0]
        DefaultSetEntry.place_counter1 = 0
        DefaultSetEntry.place_counter2 = 0

def update_pitch_list(index,pitch_values):
    global global_pitch_list
    try:
        index = int(index)
        if index > 7 or index < 0:
            print("\aIndex out of range")
            init_set_screen.save_entry.delete(0,END)
            init_set_screen.save_entry.insert(0,'')
        else:
            global_pitch_list[index-1] = pitch_values
    except:
        print("\aIndex is not an int")
        init_set_screen.save_entry.delete(0,END)
        init_set_screen.save_entry.insert(0,'')

def init_set_screen():
    set_screen = Tk()
    set_screen.title("Set Screen")
    set_screen.geometry("500x300")
    set_screen.resizable(False, False)

    DefaultSetEntry.clear_values()
    for item in PURE_NOTES:
        DefaultSetEntry(item,set_screen)
    
    # Save to label
    save_label = Label(set_screen, text="Save to",font=("Arial",15,"bold"))
    save_label.place(x=220, y=175)
    
    # Save to entry
    init_set_screen.save_entry = Entry(set_screen, width=10)
    init_set_screen.save_entry.place(x=220, y=225)

    # Save button
    save_button = Button(set_screen, text="Save", command=lambda: update_pitch_list(init_set_screen.save_entry.get(), DefaultSetEntry.pitch))
    save_button.place(x=295, y=225)

    # exit button
    exit_button = Button(set_screen, text="Exit", command=set_screen.destroy, width=7, height=1).pack(side=BOTTOM)

    set_screen.mainloop()

def set_default(set_number):
    global global_pitch_list,global_button_list

    counter = 0
    for button in global_button_list:
        if button.get_note_name() in PURE_NOTES:
            button.set_pitch(global_pitch_list[set_number][counter]) 
            button.change_entry_box()
            counter += 1

def catch_pitch_value():
    global current_pitch

    # Update current pitch text
    text_widget = default_labels.pitch_text
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(END,current_pitch)
    text_widget.config(state=DISABLED)

def add_to_pitch(value):
    text_widget = default_labels.current_note
    for button in global_button_list:
        if button.get_note_name() == NoteButton.last_pressed_note:
            # Update text between -10/+10 buttons
            text_widget.config(state=NORMAL)
            text_widget.delete(1.0, END)
            text_widget.insert(END,f"    {NoteButton.last_pressed_note}")
            text_widget.config(state=DISABLED)
            
            # Update pitch value
            button.set_pitch(button.get_pitch() + value)
            button.change_entry_box()
            break

def default_labels():
    global app,global_button_list
    
    # Info label
    info = Label(app, text="Info", font=("Arial", 15, "bold")).pack()
    
    # Default Sets label
    sets = Label(app, text="Default Sets",font=("Arial",15,"bold")).place(x=470, y=5)
    
    # Pitch catch text
    pitch_label = Label(app, text="Current Pitch: ",font=("Arial",15,"bold")).place(x=150, y=250)
    
    # Current pitch text
    default_labels.pitch_text = Text(app, width=5, height=1, font=("Arial",15,"bold"))
    default_labels.pitch_text.place(x=290, y=250)
    default_labels.pitch_text.config(state=DISABLED)

    # Pitch catch button    
    pitch_catch = Button(app, text="Pitch Catch", command= lambda: catch_pitch_value()).place(x=250, y=200)

    # Text between -10/+10 buttons
    default_labels.current_note = Text(app, width=5, height=1, font=("Arial",12,"bold"))
    default_labels.current_note.config(state=DISABLED)
    default_labels.current_note.place(x=265, y=153)

    # Adding buttons
    Button(app, text="-10", command=lambda: add_to_pitch(-10)).place(x=230, y=150)
    Button(app, text="-100", command=lambda: add_to_pitch(-100)).place(x=185, y=150)
    Button(app, text="-1000", command=lambda: add_to_pitch(-1000)).place(x=135, y=150)
    Button(app, text="+10", command=lambda: add_to_pitch(10)).place(x=320, y=150)
    Button(app, text="+100", command=lambda: add_to_pitch(100)).place(x=360, y=150)
    Button(app, text="+1000", command=lambda: add_to_pitch(1000)).place(x=405, y=150)

    # 1-8 Default set buttons
    counter = 0
    for i in range(8):
        if i >= 4:
            button = Button(app, text=f"{(counter+4)+1}", command= lambda set_number=(counter+4): set_default(set_number),width=3, height=2).place(x=540, y=40+counter*50)
            counter += 1
        else:
            button = Button(app, text=f"{i+1}", command= lambda set_number=(i): set_default(set_number) , width=3, height=2).place(x=480, y=40+i*50)

    save_new_button = Button(app, text="Save New", command=init_set_screen, width=7, height=1).place(x=495, y=250)

    # Exit button
    exit_button = Button(app, text="Exit", command=close_program, width=7, height=1).place(x=0, y=0)

def note_to_number(note: str, octave: int):
    note = NOTES.index(note) + 4
    note += (12 * octave)

    return note-16

def number_to_note(number: int):
    
    note = NOTES[(number % 12)-4]
    octave = math.floor((number+8)/12)

    return [note, octave]

def coming_note(msg):
    global current_pitch,global_button_list

    if msg.type == 'note_on':
        if msg.note == 36:
            for button in global_button_list:
                if button.get_note_name() == NoteButton.last_pressed_note:
                    button.set_pitch(current_pitch)
                    button.change_entry_box()
                    break
        else:
            for item in global_button_list:
                # this '-8' can change depending on the instrument
                note = number_to_note(msg.note - 8)
                if item.get_note_name() == note[0]:
                    item.set_octave(note[1])
                    item.send_pitch_wheel()
                    item.set_velocity(msg.velocity)
                    item.send_note_on()
                    break
    elif msg.type == 'note_off':
        for item in global_button_list:
            note = number_to_note(msg.note - 8)
            if item.get_note_name() == note[0]:
                item.set_octave(note[1])
                item.set_velocity(msg.velocity)
                item.send_pitch_wheel()
                item.send_note_off()
                break
    elif msg.type == 'pitchwheel':
        for item in global_button_list:
            if item.get_note_name() == NoteButton.last_pressed_note:
                item.send_pitch_wheel(msg.pitch)
                current_pitch = msg.pitch
                catch_pitch_value()
                break
    elif msg.type == 'control_change':
        NoteButton.control_change = msg
        NoteButton.change_control()

def close_program():
    global app,note_bool
    app.destroy()
    note_bool = False

def read_inport():
    global note_bool
    while True:
        if note_bool:
            msg = inport.receive()
            if msg.type in MESSAGE_TYPES:
                threading.Thread(target=lambda : coming_note(msg)).start()
        else:
            break

def main():
    global app,global_button_list
    app = Tk()
    app.title("GUI")
    app.geometry("600x500")
    app.resizable(False, False)


    for item in NOTES:
        global_button_list.append(NoteButton(item))

    default_labels() 
    threading.Thread(target=lambda: read_inport()).start()

    app.mainloop()

if __name__ == "__main__":
    main()
