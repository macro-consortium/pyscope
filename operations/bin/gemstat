#!/usr/bin/env python

try:
    from tkinter import *
    from tkinter.ttk import *
except ImportError:  # Python 3
    from tkinter import *
    from tkinter.ttk import *
import time

class App(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.CreateUI()
        self.LoadTable()
        parent.title("Gemini Scheduler Status")
        self.pack(expand=True,fill='y')
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_columnconfigure(0, weight = 1)

    def CreateUI(self):
        tv = Treeview(self,selectmode='browse')
        vsb = Scrollbar(orient="vertical",command=tv.yview)
        vsb.pack(side='right',fill='y',expand=True)
        tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = ('starttime', 'observer','duration','filter','status')
        tv.heading("#0", text='Object', anchor='w')
        tv.column("#0", anchor="w",width=200)
        tv.heading('starttime', text='Start Time')
        tv.column('starttime', anchor='center', width=150)
        tv.heading('observer', text='Observer')
        tv.column('observer', anchor='center', width=250)
        tv.heading('duration', text='Duration')
        tv.column('duration', anchor='center', width=75)
        tv.heading('filter', text='Filter')
        tv.column('filter', anchor='center', width=50)
        tv.heading('status', text='Status')
        tv.column('status', anchor='center', width=50)
        tv.pack(side='left',fill='y',expand=True)
        self.treeview = tv
        refresh = Button(self, text="Refresh", command= self.UpdateTable)
        refresh.pack(side='bottom',fill='y')

    def UpdateTable(self):
        for i in self.treeview.get_children():
           self.treeview.delete(i)
        self.LoadTable()
    def LoadTable(self):
        path = 'D:/IOTA3/schedules/telrun.sls'
        table = []
        with open(path,'r') as f:
             count = 0
             for line in f:
                 if count == 0:
                      status = line[22]
                 elif count == 1:
                      start = line[37:56]
                 elif count == 7:
                      source = line[22:]
                      source = source.split(',')[0]
                 elif count == 5:
                      obs = line[22:]
                 elif count == 13:
                      dur = line[22:]
                 elif count == 16:
                      fil = line[22]
                 count +=1
                 if count > 21:
                      count = 0
                      table.append([source,start,obs,dur,fil,status])
        for i in table:
             self.treeview.insert('','end', text=i[0], values=(i[1],i[2],i[3],i[4],i[5]),tags= (i[5],))
             self.treeview.tag_configure('D',foreground = 'green')
             self.treeview.tag_configure('F',foreground = 'red')
def main():
    root = Tk()
    App(root)
    root.mainloop()
if __name__ == '__main__':
    main()
