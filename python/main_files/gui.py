from tkinter import *
from music21 import *
from tkinter import ttk,messagebox
import mido,random,time,threading,math,json,os

# Global variables
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
PURE_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] 
OTHER_NOTES = ['C#', 'D#', 'F#', 'G#', 'A#']
MESSAGE_TYPES = ['note_on','note_off','pitchwheel','control_change']
OCTAVES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
global_button_list = []
global_pitch_list = []
current_pitch = 0
note_bool = True
json_data = []

# setting 8 default sets to values to 0
for _ in range(8):
    global_pitch_list.append([0,0,0,0,0,0,0,0,0,0,0,0])


def converter(value, control):
    # if control: pitch to cent
    # else: cent to pitch
    if control:
        new_value = (((value - (-8192)) * 200) / 16383) + (-100)
    else:
        new_value = (((value - (-100)) * 16383) / 200) + (-8192)
    return int(new_value)

class NoteButton:
    global output,app

    last_pressed_note = None
    control_change = mido.Message('control_change', control=1, value=0)
    counter = 0
    label_counter1 = 0
    label_counter2 = 0
    placement = [0,85,170,255,340,425,510,65,150,320,405,490]

    def __init__(self,note_name,octave=5,velocity=64):
        self.__note_name = note_name
        self.__pitch_value = 0
        self.__octave = octave
        self.__velocity = velocity
        self.__entry_box = None
        self.__saved_pitch = 0

        if note_name in PURE_NOTES:
            button = Button(
            app,text=note_name,
            command = lambda: (self.set_pitch(self.get_saved_pitch()), self.send_note_on(), self.send_pitch_wheel() , time.sleep(0.1), self.send_note_off()),
            width=10,height=15,bg="white",fg="#241f1f",activebackground="white",activeforeground="#241f1f",font=("Arial", 10, "bold"))
        else:
            button = Button(
            app,text=note_name,
            command = lambda: (self.set_pitch(self.get_saved_pitch()), self.send_note_on(), self.send_pitch_wheel() , time.sleep(0.1), self.send_note_off()),
            width=4,height=7,bg="#241f1f",fg="white",activebackground="#241f1f",activeforeground="white",font=("Arial", 10, "bold"))
        
        if note_name in PURE_NOTES:
            NoteButton.label_counter1 += 1.5

            label = Label(app, text=note_name)
            label.place(x=10, y= 10 + (NoteButton.label_counter1 * 20))

            self.__entry_box = Entry(app, width=5)

            self.__entry_box.place(x=50, y= 10 + (NoteButton.label_counter1 * 20))
            self.__entry_box.bind('<Return>', lambda event: self.set_saved_pitch(self.__entry_box.get()))
        else:
            NoteButton.label_counter2 += 1.5
            label = Label(app, text=note_name)
            label.place(x=100, y= 10 + (NoteButton.label_counter2 * 20))

            self.__entry_box = Entry(app, width=5)

            self.__entry_box.place(x=130, y= 10 + (NoteButton.label_counter2 * 20))
            self.__entry_box.bind('<Return>', lambda event: self.set_saved_pitch(self.__entry_box.get()))

        button.place(x=NoteButton.placement[NoteButton.counter], y=300)

        NoteButton.counter += 1

    def change_entry_box(self,*args):
        if self.__entry_box != None:
            if args:
                self.__entry_box.delete(0,END)
                self.__entry_box.insert(0,args[0])
            else:
                self.__entry_box.delete(0,END)
                self.__entry_box.insert(0,self.get_pitch())

    def get_saved_pitch(self):
        return self.__saved_pitch

    def set_saved_pitch(self,pitch):
        try:
            pitch = int(pitch)
            if pitch > 100 or pitch < -100:
                self.setting_pitch_error("Pitch out of range")
            else:
                self.__saved_pitch = int(pitch)
        except:
            self.setting_pitch_error("Pitch is not an int")

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
            if pitch > 100 or pitch < -100:
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
        output.send( NoteButton.control_change )

        if len(self.get_note_name()) == 1:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with  \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)
        else:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)

        output.send( mido.Message('note_on', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
    
    def send_pitch_wheel(self):
        sending_value = converter(self.get_pitch(), False)
        output.send( mido.Message('pitchwheel', pitch=sending_value) )

    def send_note_off(self):
        output.send( mido.Message('note_off', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
        output.send( NoteButton.control_change )

    @staticmethod
    def change_control():
        output.send(NoteButton.control_change)

class DefaultSetEntry:
    pitch = [0,0,0,0,0,0,0,0,0,0,0,0]
    general_counter = 0

    place_counter1 = 0
    place_counter2 = 0
    def __init__(self,note_name,set_screen):
        self.__entry_box = None
        self.__note_name = note_name
        self.__entry_box_number = DefaultSetEntry.general_counter

        self.__entry_box = Entry(set_screen, width=5)
        if DefaultSetEntry.general_counter%2==0:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=40 + (DefaultSetEntry.place_counter1*100), y=50 )
            self.__entry_box.place(x=80 + (DefaultSetEntry.place_counter1*100), y=50)
            DefaultSetEntry.place_counter1 += 1
        else:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=40 + (DefaultSetEntry.place_counter2*100), y=100 )
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
            if pitch > 100 or pitch < -100:
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
        DefaultSetEntry.pitch = [0,0,0,0,0,0,0,0,0,0,0,0]
        DefaultSetEntry.place_counter1 = 0
        DefaultSetEntry.place_counter2 = 0

def update_pitch_list(index):
    global global_pitch_list,json_data
    try:
        index = int(index) - 1
        if index > 7 or index < 0:
            print("\aIndex out of range")
            init_set_screen.save_entry.delete(0,END)
            init_set_screen.save_entry.insert(0,'')
        else:
            data_dict = {}
            data_dict["Set-Number"] = index + 1
            data_dict["Note-Value"] = [_ for _ in range(12)]
            counter = 0
            for item in PURE_NOTES:
                data_dict["Note-Value"][counter] = [item, DefaultSetEntry.pitch[counter]]
                counter += 1
            for item in OTHER_NOTES:
                data_dict["Note-Value"][counter] = [item, DefaultSetEntry.pitch[counter]]
                counter += 1
            json_data.append(data_dict)
            global_pitch_list[index] = DefaultSetEntry.pitch
            DefaultSetEntry.clear_values()
    except:
        print("\aIndex is not an int")
        init_set_screen.save_entry.delete(0,END)
        init_set_screen.save_entry.insert(0,'')

def init_set_screen():
    set_screen = Tk()
    set_screen.title("Set Screen")
    set_screen.geometry("650x300")
    set_screen.resizable(False, False)
    set_screen.iconbitmap('musical_score.ico')

    DefaultSetEntry.clear_values()
    for item in PURE_NOTES:
        DefaultSetEntry(item,set_screen)
    for item in OTHER_NOTES:
        DefaultSetEntry(item,set_screen)
    
    # Save to label
    save_label = Label(set_screen, text="Save to",font=("Arial",15,"bold"))
    save_label.place(x=220, y=175)
    
    # Save to entry
    init_set_screen.save_entry = Entry(set_screen, width=10)
    init_set_screen.save_entry.place(x=220, y=225)

    # Save button
    save_button = Button(set_screen, text="Save", command=lambda: update_pitch_list(init_set_screen.save_entry.get())).place(x=295, y=225)

    set_screen.mainloop()

def set_default(set_number):
    global global_pitch_list,global_button_list

    counter = 0
    for button in global_button_list:
        if button.get_note_name() in PURE_NOTES:
            button.set_saved_pitch(global_pitch_list[set_number][counter]) 
            button.change_entry_box(global_pitch_list[set_number][counter])
            counter += 1
    for button in global_button_list:
        if button.get_note_name() in OTHER_NOTES:
            button.set_saved_pitch(global_pitch_list[set_number][counter]) 
            button.change_entry_box(global_pitch_list[set_number][counter])
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
            if button.get_saved_pitch() + value > 100:
                threading.Thread(target=lambda: button.set_saved_pitch(100)).start()
                button.change_entry_box(button.get_saved_pitch())
                break
            elif button.get_saved_pitch() + value < -100:
                threading.Thread(target=lambda: button.set_saved_pitch(-100)).start()
                button.change_entry_box(button.get_saved_pitch())
                break
            else:
                threading.Thread(target=lambda: button.set_saved_pitch(button.get_saved_pitch() + value)).start()
                threading.Thread(target=lambda: button.change_entry_box(button.get_saved_pitch())).start()
                break

def default_labels():
    global app,global_button_list
    
    # Info label
    info = Label(app, text="Info", font=("Arial", 15, "bold")).pack()
    
    # Default Sets label
    sets = Label(app, text="Default Sets",font=("Arial",15,"bold")).place(x=470, y=5)
    
    # Current Pitch label
    pitch_label = Label(app, text="Current Pitch: ",font=("Arial",15,"bold")).place(x=150, y=260)
    
    # Current pitch text
    default_labels.pitch_text = Text(app, width=5, height=1, font=("Arial",15,"bold"))
    default_labels.pitch_text.place(x=290, y=260)
    default_labels.pitch_text.config(state=DISABLED)

    # Pitch catch button    
    # pitch_catch = Button(app, text="Pitch Catch", command=lambda: catch_pitch_value()).place(x=250, y=200)

    # Text between -10/+10 buttons
    default_labels.current_note = Text(app, width=5, height=1, font=("Arial",12,"bold"))
    default_labels.current_note.config(state=DISABLED)
    default_labels.current_note.place(x=265, y=213)

    # Adding buttons
    Button(app, text="-1", command=lambda: add_to_pitch(-1)).place(x=230, y=210)
    Button(app, text="-10", command=lambda: add_to_pitch(-10)).place(x=185, y=210)
    Button(app, text="-100", command=lambda: add_to_pitch(-100)).place(x=135, y=210)
    Button(app, text="+1", command=lambda: add_to_pitch(1)).place(x=320, y=210)
    Button(app, text="+10", command=lambda: add_to_pitch(10)).place(x=360, y=210)
    Button(app, text="+100", command=lambda: add_to_pitch(100)).place(x=405, y=210)

    # 1-8 Default set buttons
    counter = 0
    for i in range(8):
        if i >= 4:
            button = Button(app, text=f"{(counter+4)+1}", command=lambda set_number=(counter+4): set_default(set_number),width=3, height=2).place(x=540, y=40+counter*50)
            counter += 1
        else:
            button = Button(app, text=f"{i+1}", command=lambda set_number=(i): set_default(set_number) , width=3, height=2).place(x=480, y=40+i*50)

    save_new_button = Button(app, text="Save New", command=init_set_screen, width=7, height=1).place(x=495, y=250)

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
                    threading.Thread(target=lambda: button.set_saved_pitch(current_pitch) ).start()
                    threading.Thread(target=lambda: button.change_entry_box(current_pitch) ).start()
                    break
        else:
            for item in global_button_list:
                # this '-8' can change depending on the instrument
                note = number_to_note(msg.note - 8)
                if item.get_note_name() == note[0]:
                    threading.Thread(target=lambda: item.set_octave(note[1]) ).start()
                    if current_pitch == 0:
                        threading.Thread(target=lambda: item.set_pitch(item.get_saved_pitch())).start()
                    else:
                        threading.Thread(target=lambda: item.set_pitch(current_pitch)).start()
                    threading.Thread(target=lambda: item.set_octave(note[1]) ).start()
                    threading.Thread(target=lambda: item.send_pitch_wheel()).start()
                    threading.Thread(target=lambda: item.set_velocity(msg.velocity) ).start()
                    threading.Thread(target=lambda: item.send_note_on()).start()
                    break
    elif msg.type == 'note_off':
        for item in global_button_list:
            note = number_to_note(msg.note - 8)
            if item.get_note_name() == note[0]:
                if current_pitch == 0:
                    threading.Thread(target=lambda: item.set_pitch(item.get_saved_pitch())).start()
                else:
                    threading.Thread(target=lambda: item.set_pitch(current_pitch)).start()
                threading.Thread(target=lambda: item.send_pitch_wheel()).start()
                threading.Thread(target=lambda: item.set_velocity(msg.velocity) ).start()
                threading.Thread(target=lambda: item.set_octave(note[1]) ).start()
                threading.Thread(target=lambda: item.send_note_off()).start()
                break
    elif msg.type == 'pitchwheel':
        for item in global_button_list:
            if item.get_note_name() == NoteButton.last_pressed_note:
                current_pitch = converter(msg.pitch, True)
                threading.Thread(target=lambda: item.set_pitch(current_pitch)).start()
                threading.Thread(target=lambda: item.send_pitch_wheel()).start()
                threading.Thread(target=lambda: catch_pitch_value()).start() 
                break
    elif msg.type == 'control_change':
        NoteButton.control_change = msg
        threading.Thread(target=lambda: NoteButton.change_control()).start()

def close_program():
    global app,note_bool,json_data
    if json_data:
        files = os.listdir()
        json_files = [f for f in files if f.endswith('.json')]
        if json_files:
            last_number = int((json_files[-1].split(".")[0])[-1])
            with open(f"pitch_data{last_number+1}.json", "w") as fp:
                json.dump(json_data, fp, indent=4)
        else:
            with open(f"pitch_data1.json", "w") as fp:
                json.dump(json_data, fp, indent=4)
    app.destroy()
    note_bool = False

def read_inport():
    global note_bool
    while note_bool:
        msg = inport.receive()
        if note_bool:
            if msg.type in MESSAGE_TYPES:
                threading.Thread(target=lambda: coming_note(msg)).start()
        else:
            break

def connect_ports(port1, port2):
    global inport,output
    inport = mido.open_input(port1)
    output = mido.open_output(port2)

def port_select_screen():
    global inport,output

    port_screen = Tk()
    port_screen.title("Select Port")
    port_screen.geometry("400x400+500+200")
    port_screen.configure(background='#2F4F4F')
    port_screen.iconbitmap('connect.ico')
    port_screen.protocol("WM_DELETE_WINDOW", lambda: exit())
    
    outports = mido.get_output_names()
    inports = mido.get_input_names()
    if (not outports) or (not inports):
        messagebox.showerror("Error", "No open ports found")
        exit()

    Label(port_screen, text="Select Ports", font=("Arial",20,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)

    Label(port_screen, text="Input Port", font=("Arial",12,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)    
    inport_var = StringVar()
    inport_var.set(inports[-1])
    inport_dropdown = OptionMenu(port_screen, inport_var, *inports)
    inport_dropdown.pack(side=TOP, pady=10)    
    
    Label(port_screen, text="Output Port", font=("Arial",12,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)
    outport_var = StringVar()
    outport_var.set(outports[-2])
    outport_dropdown = OptionMenu(port_screen, outport_var, *outports)
    outport_dropdown.pack(side=TOP, pady=10)

    Button(port_screen, text="Connect", command=lambda: (connect_ports(inport_var.get(), outport_var.get()), port_screen.destroy()), width=10, height=1).pack(side=TOP, pady=10)

    port_screen.mainloop()

def main():
    global app,global_button_list
    
    port_select_screen()

    app = Tk()
    app.title("GUI")
    app.geometry("600x500")
    app.resizable(False, False)
    app.iconbitmap('piano.ico')
    app.protocol("WM_DELETE_WINDOW", close_program)

    for item in PURE_NOTES:
        global_button_list.append(NoteButton(item))
    for item in OTHER_NOTES:
        global_button_list.append(NoteButton(item))

    default_labels()
    threading.Thread(target=lambda: read_inport()).start()

    app.mainloop()

if __name__ == "__main__":
    main()
