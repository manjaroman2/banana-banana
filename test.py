import tkinter
from tkinter.constants import *

def create_window():
    tk = tkinter.Tk()
    f = tkinter.Frame(tk, relief=RIDGE, borderwidth=2)
    f.pack(fill=BOTH,expand=1)
    l = tkinter.Label(f, text="Hello, World")
    l.pack(fill=X, expand=1)
    btn = tkinter.Button(f,text="Exit",command=tk.destroy)
    btn.pack(side=BOTTOM)
    tk.mainloop()
# tkinter
# help(tkinter.Canvas().grid_configure())
help(tkinter)