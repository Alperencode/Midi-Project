from tkinter import *

app = Tk()

app.title("Baics")
app.geometry("600x500")

def button_pressed():
    label = Label(app,text="Basildi")
    label.grid(row=1)

def create_note_button():
    button = Button(app, text="Kaydet", command = button_pressed, width=5,height=10)

    return button

for i in range(0,9):
    create_note_button().grid(row=0,column=i)

app.mainloop()