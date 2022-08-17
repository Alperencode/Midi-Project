# Importing modules
from tkinter import *
from music21 import *
from tkinter import ttk,messagebox
import mido,time,threading,math,json,os,mido.backends.rtmidi

# Global variables
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
PURE_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] 
OTHER_NOTES = ['C#', 'D#', 'F#', 'G#', 'A#']
MESSAGE_TYPES = ['note_on','note_off','pitchwheel','control_change']
OCTAVES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
global_button_list = []
global_pitch_list = []
json_data = []
current_pitch = 0
note_bool = True

# setting 8 default sets to values to 0
for _ in range(8):
    global_pitch_list.append([0,0,0,0,0,0,0,0,0,0,0,0])

def converter(value, control):
    """ 
    Range converter function to convert pitch value (-8192/8191) to cent value (-100/100)
    control: True -> convert to cent value, False -> convert to pitch value
    """
    if control:
        new_value = (((value - (-8192)) * 200) / 16383) + (-100)
    else:
        new_value = (((value - (-100)) * 16383) / 200) + (-8192)
    return int(new_value)

class NoteButton:
    """
    This is the main class of the program which is basically responsible for sending the midi messages to the midi output.
    Detailed explanation has been provided in each function.
    """
    global output,app

    # Static variables
    # counter is used to keep track of the number of buttons created
    # [label_counter and placement] are used to place the labels and entry boxes in the GUI
    # last_pressed_note is used to keep track of the last pressed note
    # pitch list is used to save values when pressed 'save values' button 
    # control change is used to send control_change message with static method rather than assigning it to every note
    counter = 0
    label_counter = 0
    last_pressed_note = None
    placement = [0,85,170,255,340,425,510,65,150,320,405,490]
    pitch = [0,0,0,0,0,0,0,0,0,0,0,0]
    control_change = mido.Message('control_change', control=1, value=0)

    def __init__(self,note_name,octave=5,velocity=64):
        """
        Initializing function of the class which takes 1 required argument and 2 optional arguments.
        note_name: name of the note
        octave: octave of the note
        velocity: velocity of the note
        What initiazlization do is basically making basic variable definitions, creating a pitch entry box and note button to GUI for each note, 
        and keeping track of how many button was created 
        """
        self.__note_name = note_name
        self.__octave = octave
        self.__velocity = velocity
        self.__pitch_value = 0
        self.__saved_pitch = 0
        self.__entry_box_number = NoteButton.counter
        self.__entry_box = None

        # buttons are used to trigger 3 basic events: send note_on, wait for 100 miliseconds and send note_off
        # so command argument is used with lambda to trigger more than one function
        if note_name in PURE_NOTES:
            # Making note button white if the note is a pure note
            button = Button(
            app,text=note_name,
            command = lambda: (self.set_pitch(self.get_saved_pitch()), self.send_note_on(), self.send_pitch_wheel() , time.sleep(0.1), self.send_note_off()),
            width=10,height=15,bg="white",fg="#241f1f",activebackground="white",activeforeground="#241f1f",font=("Arial", 10, "bold"))
        else:
            # Making note button black if the note is not a pure note
            button = Button(
            app,text=note_name,
            command = lambda: (self.set_pitch(self.get_saved_pitch()), self.send_note_on(), self.send_pitch_wheel() , time.sleep(0.1), self.send_note_off()),
            width=4,height=7,bg="#241f1f",fg="white",activebackground="#241f1f",activeforeground="white",font=("Arial", 10, "bold"))
        
        # Placing label (note text) and entry box in the GUI
        if note_name in PURE_NOTES:
            NoteButton.label_counter += 1.5

            label = Label(app, text=note_name)
            label.place(x=10, y= 10 + (NoteButton.label_counter * 20))

            self.__entry_box = Entry(app, width=5)
            self.__entry_box.place(x=50, y= 10 + (NoteButton.label_counter * 20))
            self.__entry_box.bind('<Return>', lambda event: self.set_saved_pitch(self.__entry_box.get()))
        else:
            NoteButton.label_counter += 1.5

            label = Label(app, text=note_name)
            label.place(x=100, y= 10 + (NoteButton.label_counter * 20))

            self.__entry_box = Entry(app, width=5)
            self.__entry_box.place(x=130, y= 10 + (NoteButton.label_counter * 20))
            self.__entry_box.bind('<Return>', lambda event: self.set_saved_pitch(self.__entry_box.get()))

        # Placing button in the GUI
        button.place(x=NoteButton.placement[NoteButton.counter], y=300)

        # Incrementing counter
        NoteButton.counter += 1

    def update_local_pitch(self):
        """Updating the local pitch list with the saved pitch value """
        NoteButton.pitch[self.__entry_box_number] = self.__saved_pitch
    
    def change_entry_box(self,*args):
        """
        If used with any argument, it will change the entry box value to the argument value 
        If not, it will change entry box to current pitch
        """
        if args:
            self.__entry_box.delete(0,END)
            self.__entry_box.insert(0,args[0])
        else:
            self.__entry_box.delete(0,END)
            self.__entry_box.insert(0,self.get_pitch())

    def get_saved_pitch(self):
        """Getter for saved pitch"""
        return self.__saved_pitch

    def set_saved_pitch(self,pitch):
        """Setter for saved pitch"""
        try:
            pitch = int(pitch)
            if pitch > 100 or pitch < -100:
                self.setting_pitch_error("Pitch out of range")
            else:
                self.__saved_pitch = int(pitch)
        except:
            self.setting_pitch_error("Pitch is not an int")

    def get_note_name(self):
        """Getter for note name"""
        return self.__note_name

    def get_octave(self):
        """Getter for octave"""
        return self.__octave

    def set_octave(self,octave):
        """Setter for octave"""
        self.__octave = octave

    def set_velocity(self,velocity):
        """Setter for velocity"""
        self.__velocity = velocity

    def get_velocity(self):
        """Getter for velocity"""
        return self.__velocity

    def set_pitch(self,pitch):
        """Setter for pitch"""
        try:
            pitch = int(pitch)
            if pitch > 100 or pitch < -100:
                self.setting_pitch_error("Pitch out of range")
            else:
                self.__pitch_value = int(pitch)
        except:
            self.setting_pitch_error("Pitch is not an int")

    def setting_pitch_error(self,error_message):
        """Printing passed error message and clearing entry box"""
        print(f"\a{error_message}")
        self.__entry_box.delete(0,END)
        self.__entry_box.insert(0,self.get_pitch())

    def get_pitch(self):
        """Getter for pitch"""
        return self.__pitch_value

    def send_note_on(self):
        """
        Core function to send note_on message to the midi device.
        It will send note_on message with the current pitch and velocity,
        Change the label under the info,
        Send control_change message (?)
        """

        NoteButton.last_pressed_note = self.get_note_name()
        output.send( NoteButton.control_change )

        # Label will put an extra space if note is a pure note
        if self.get_note_name() in PURE_NOTES:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()}  with \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)
        else:
            Label(app, text=f"Sending {self.get_note_name()} octave {self.get_octave()} with \n{self.__pitch_value} pitch and {self.get_velocity()} velocity",font=("Arial",12,"bold")).place(x=200, y=40)

        # Sending midi signal
        output.send( mido.Message('note_on', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
    
    def send_pitch_wheel(self):
        """Sending converted pitch value to the midi device"""
        sending_value = converter(self.get_pitch(), False)
        output.send( mido.Message('pitchwheel', pitch=sending_value) )

    def send_note_off(self):
        """Sending note_off message to the midi device"""
        output.send( mido.Message('note_off', note=note_to_number(self.get_note_name(), self.get_octave()), velocity=self.get_velocity()) )
        output.send( NoteButton.control_change )

    @staticmethod
    def change_control():
        """Sending control_change message to the midi device"""
        output.send(NoteButton.control_change)

class DefaultSetEntry:
    """
    This class allows to create and control values of set screen entry boxes.
    It checks if entered values are valid or not,
    has a pitch list to store the pitch values,
    """

    # Static variables
    # general_counter is used to keep track of the number of entries created
    # pitch list is used to store the pitch values for current screen
    # [place_counter1 and place_counter2] are used to place the labels and entry boxes in the GUI
    general_counter = 0
    pitch = [0,0,0,0,0,0,0,0,0,0,0,0]
    place_counter1 = 0
    place_counter2 = 0

    def __init__(self,note_name,set_screen):
        """
        Takes note_name and screen to display as arguments
        Creating entry box and label for the set screen,
        Setting entry index with the general counter,
        """
        self.__note_name = note_name
        self.__entry_box_number = DefaultSetEntry.general_counter
        self.__entry_box = Entry(set_screen, width=5)

        # This statement is used to place 2 entry boxes in a column
        if DefaultSetEntry.general_counter%2==0:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=40 + (DefaultSetEntry.place_counter1*100), y=50 )
            self.__entry_box.place(x=80 + (DefaultSetEntry.place_counter1*100), y=50)
            DefaultSetEntry.place_counter1 += 1
        else:
            Label(set_screen, text=f"{self.__note_name} :",font=("Arial",12,"bold")).place(x=40 + (DefaultSetEntry.place_counter2*100), y=100 )
            self.__entry_box.place(x=80 + (DefaultSetEntry.place_counter2*100), y=100)
            DefaultSetEntry.place_counter2 += 1
        
        # Binding enter key to entry 
        self.__entry_box.bind('<Return>', lambda event: self.set_pitch(self.__entry_box.get()))

        # Incrementing general_counter
        DefaultSetEntry.general_counter += 1

    def setting_pitch_error(self,error_message):
        """Printing passed error message and clearing entry box"""
        print(f"\a{error_message}")
        self.__entry_box.delete(0,END)
        self.__entry_box.insert(0,self.get_pitch())

    def set_pitch(self,pitch):
        """Setter for pitch"""
        try:
            pitch = int(pitch)
            if pitch > 100 or pitch < -100:
                self.setting_pitch_error("Pitch out of range")
            else:
                DefaultSetEntry.pitch[self.__entry_box_number] = pitch
        except:
            self.setting_pitch_error("Pitch is not an int")

    def get_pitch(self):
        """Getter for pitch"""
        return DefaultSetEntry.pitch[self.__entry_box_number]    

    @staticmethod
    def clear_values():
        """Reverting all class static variables to initial values"""
        DefaultSetEntry.general_counter = 0
        DefaultSetEntry.pitch = [0,0,0,0,0,0,0,0,0,0,0,0]
        DefaultSetEntry.place_counter1 = 0
        DefaultSetEntry.place_counter2 = 0

def update_pitch_list(index,pitch_list):
    """
    Updating global pitch list with passed argument,
    Updating json data with the new pitch list 
    """
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
                data_dict["Note-Value"][counter] = [item, pitch_list[counter]]
                counter += 1
            for item in OTHER_NOTES:
                data_dict["Note-Value"][counter] = [item, pitch_list[counter]]
                counter += 1
            json_data.append(data_dict)
            global_pitch_list[index] = pitch_list
            DefaultSetEntry.clear_values()
    except:
        print("\aIndex is not an int")
        try:
            init_set_screen.save_entry.delete(0,END)
            init_set_screen.save_entry.insert(0,'')
        except:
            pass

def init_set_screen():
    """Initializing set screen and its widgets"""
    set_screen = Tk()
    set_screen.title("Set Screen")
    set_screen.geometry("650x300")
    set_screen.resizable(False, False)
    set_screen.iconbitmap('icons/musical_score.ico')

    DefaultSetEntry.clear_values()
    for item in PURE_NOTES:
        DefaultSetEntry(item,set_screen)
    for item in OTHER_NOTES:
        DefaultSetEntry(item,set_screen)
    
    # Save to label
    save_label = Label(set_screen, text="Save to",font=("Arial",15,"bold"))
    save_label.place(x=275, y=175)
    
    # Save to entry
    init_set_screen.save_entry = Entry(set_screen, width=10)
    init_set_screen.save_entry.place(x=280, y=225)

    # Save button
    save_button = Button(set_screen, text="Save", command=lambda: update_pitch_list(init_set_screen.save_entry.get(),DefaultSetEntry.pitch)).place(x=355, y=225)

    set_screen.mainloop()

def set_default(set_number):
    """Setting default values according passed set number"""
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
    """
    Catching current pitch value coming from the midi device using global current_pitch value
    and updates text widget from default_labels function
    """
    global current_pitch

    text_widget = default_labels.pitch_text
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(END,current_pitch)
    text_widget.config(state=DISABLED)

def add_to_pitch(value):
    """adding/subtracting passed value to last pressed button's pitch value"""
    text_widget = default_labels.current_note
    for button in global_button_list:
        if button.get_note_name() == NoteButton.last_pressed_note:
            # Update text between -10/+10 buttons
            text_widget.config(state=NORMAL)
            text_widget.delete(1.0, END)
            text_widget.insert(END,f"    {NoteButton.last_pressed_note}")
            text_widget.config(state=DISABLED)
            
            # Update pitch value
            new_value = 0
            if button.get_saved_pitch() + value > 100:
                new_value = 100
            elif button.get_saved_pitch() + value < -100:
                new_value = -100
            else:
                new_value = button.get_saved_pitch() + value
            threading.Thread(target=lambda: button.set_saved_pitch(new_value)).start()
            threading.Thread(target=lambda: button.update_local_pitch() ).start()
            threading.Thread(target=lambda: button.change_entry_box(button.get_saved_pitch())).start()
            break

def default_labels():
    """Initializing default labels and their widgets and displaying to main app"""
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

    # Save values button 
    save_values = Button(app, text="Save Values", command=lambda: (update_pitch_list(1, NoteButton.pitch))).place(x=250, y=170)

    # Text between -10/+10 buttons
    default_labels.current_note = Text(app, width=5, height=1, font=("Arial",12,"bold"))
    default_labels.current_note.config(state=DISABLED)
    default_labels.current_note.place(x=260, y=213)

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

    # Setting menu
    app_menu = Menu(app)
    app.config(menu=app_menu)
    about_menu = Menu(app_menu)
    app_menu.add_cascade(label="About", menu=about_menu)
    about_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "This is an open-source software GUI program for sending and configuring Midi Signals.\n\nCreated by: Alperen Ağa\n\nVersion: 0.1.0"))
    
    # Information menu
    information_menu = Menu(app_menu)
    app_menu.add_cascade(label="Information", menu=information_menu)
    information_menu.add_command(label="Information", command=lambda: messagebox.showinfo("Information", "This program requires to send one more midi signal after closing the program because of reading inport method.\n\nIf you cannot send another midi signal after closing program this program keeps running in background.\n\nIf you dont have any tool connected to send midi signal after closing program you can stop the program in task manager which is named 'Midi-Project.exe'"))

    save_new_button = Button(app, text="Save New", command=init_set_screen, width=7, height=1).place(x=495, y=250)

def note_to_number(note: str, octave: int):
    """Converting passed note name and octave to Midi note number"""
    note = NOTES.index(note) + 4
    note += (12 * octave)

    return note-16

def number_to_note(number: int):
    """Converting passed Midi note number to note name and octave""" 
    note = NOTES[(number % 12)-4]
    octave = math.floor((number+8)/12)

    return [note, octave]

def coming_note(msg):
    """
    Core function for configuring incoming midi messages,
    processes the incoming midi message and takes action according to message type.
    Then it runs the necessary methods with threads depending on the message
    """
    global current_pitch,global_button_list

    if msg.type == 'note_on':
        if msg.note == 36:
            # If coming note is C3 (first note), save pitch value
            for button in global_button_list:
                if button.get_note_name() == NoteButton.last_pressed_note:
                    threading.Thread(target=lambda: button.set_saved_pitch(current_pitch) ).start()
                    threading.Thread(target=lambda: button.change_entry_box(current_pitch) ).start()
                    threading.Thread(target=lambda: button.update_local_pitch() ).start()
                    break
        else:
            for item in global_button_list:
                # this '-8' can change depending on the instrument
                note = number_to_note(msg.note - 8)
                if item.get_note_name() == note[0]:
                    threading.Thread(target=lambda: item.set_octave(note[1]) ).start()
                    if current_pitch == 0:
                        # if current_pitch is 0, use the saved pitch value
                        threading.Thread(target=lambda: item.set_pitch(item.get_saved_pitch())).start()
                    else:
                        # else use the current pitch value
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
    """
    Closes the program and saves json data if there is any.
    This function is also checking if there is any json file created to prevent overriding the old file.
    """
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
    """Reads incoming midi messages and sends them to coming_note function to configure the message"""
    global note_bool
    while note_bool:
        # receive function blocking the program until a message is received this is why program doesn't close without sending one more message
        # It can be used with block=False argument to receive messages without blocking the program but that is not recommended
        # Because it will keep reading inport non-stop and use a lot of CPU power
        msg = inport.receive()
        if note_bool:
            if msg.type in MESSAGE_TYPES:
                threading.Thread(target=lambda: coming_note(msg)).start()
        else:
            break

def connect_ports(_inport, _outport):
    """Connects the midi inport and outport"""
    global inport,output
    inport = mido.open_input(_inport)
    output = mido.open_output(_outport)

def port_select_screen():
    """Initializing the port selection screen"""
    global inport,output

    port_screen = Tk()
    port_screen.title("Select Port")
    port_screen.geometry("400x400+500+200")
    port_screen.configure(background='#2F4F4F')
    port_screen.iconbitmap('icons/connect.ico')
    port_screen.protocol("WM_DELETE_WINDOW", lambda: sys.exit())
    
    outports = mido.get_output_names()
    inports = mido.get_input_names()
    if (not outports) or (not inports):
        messagebox.showerror("Error", "No open ports found")
        sys.exit()

    Label(port_screen, text="Select Ports", font=("Arial",20,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)

    Label(port_screen, text="Input Port", font=("Arial",12,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)    
    inport_var = StringVar()
    inport_var.set(inports[-1])
    inport_dropdown = OptionMenu(port_screen, inport_var, *inports)
    inport_dropdown.pack(side=TOP, pady=10)    
    
    Label(port_screen, text="Output Port", font=("Arial",12,'bold'), bg='#2F4F4F', fg='white').pack(side=TOP, pady=10)
    outport_var = StringVar()
    outport_var.set(outports[-1])
    outport_dropdown = OptionMenu(port_screen, outport_var, *outports)
    outport_dropdown.pack(side=TOP, pady=10)

    Button(port_screen, text="Connect", command=lambda: (connect_ports(inport_var.get(), outport_var.get()), port_screen.destroy()), width=10, height=1).pack(side=TOP, pady=10)

    port_screen.mainloop()

def main():
    global app,global_button_list
    
    # Initializing the port selection window
    port_select_screen()

    # Initializing the main window
    app = Tk()
    app.title("Midi Project")
    app.geometry("600x500")
    app.resizable(False, False)
    app.iconbitmap('icons/piano.ico')
    app.protocol("WM_DELETE_WINDOW", close_program)

    # Creating the note buttons
    for item in PURE_NOTES:
        global_button_list.append(NoteButton(item))
    NoteButton.label_counter = 0
    for item in OTHER_NOTES:
        global_button_list.append(NoteButton(item))

    # Initializing the main window label and widgets
    default_labels()

    # Starting to read inport
    threading.Thread(target=lambda: read_inport()).start()

    app.mainloop()

if __name__ == "__main__":
    main()
