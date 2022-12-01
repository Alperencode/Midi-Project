from tkinter import *
from music21 import *
from tkinter import ttk,messagebox
import mido,time,threading,json,math,os,mido.backends.rtmidi

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
PURE_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] 
OTHER_NOTES = ['C#', 'D#', 'F#', 'G#', 'A#']
MESSAGE_TYPES = ['note_on','note_off','pitchwheel','control_change']
OCTAVES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

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

def save_json(json_data):
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
