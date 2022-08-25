from tkinter import *

app = Tk()

app.title("Basics")
app.geometry("600x500")

def button_pressed():
    label = Label(app,text="Pressed")
    label.grid(row=1)

def create_note_button():
    button = Button(app, text="Button", command = button_pressed, width=5,height=10)

    return button

for i in range(0,9):
    create_note_button().grid(row=0,column=i)

app.mainloop()