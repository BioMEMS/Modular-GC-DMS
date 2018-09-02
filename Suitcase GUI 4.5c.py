#Author: Ilya Anishchenko
#
#MR-GC-DMS GUI software is the proprietary property of The Regents of the University of California (“The Regents.”)
#
#Copyright © 2013-18 The Regents of the University of California, Davis campus. All Rights Reserved.  
#
#Redistribution and use in source and binary forms, with or without modification, are permitted by nonprofit, research institutions for research use only, provided that the following conditions are met:
#•	Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
#•	Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 
#•	The name of The Regents may not be used to endorse or promote products derived from this software without specific prior written permission. 
#The end-user understands that the program was developed for research purposes and is advised not to rely exclusively on the program for any reason.
#THE SOFTWARE PROVIDED IS ON AN "AS IS" BASIS, AND THE REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. THE REGENTS SPECIFICALLY DISCLAIMS ANY EXPRESS OR IMPLIED 
#WARRANTIES, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, 
#SPECIAL, INCIDENTAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES, INCLUDING BUT NOT LIMITED TO  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR PROFITS, OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND UNDER 
#ANY THEORY OF LIABILITY WHETHER IN CONTRACT, STRICT LIABILITY OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY 
#OF SUCH DAMAGE. 
#
#If you do not agree to these terms, do not download or use the software.  This license may be modified only in a writing signed by authorized signatory of both parties.
#For commercial license information please contact copyright@ucdavis.edu



import tkinter as tk
import gc as gc
import time
from tkinter import ttk
from tkinter import filedialog as tkf
import serial as Serial
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import numpy as np


class MainPage(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Prototype GUI for Suitcase")
        self.geometry("1015x690")

        self.cyclebut = False
        self.badinput = False
        
        self.comb = ComBox()
        self.comb.grid(row=0, column=0, padx=15, pady=15, sticky='N')

        self.eventb = EventsBox()
        self.eventb.grid(row=0, column=1, rowspan=5, padx=15, pady=23, sticky='n') #pady = 27 is old value
        
        self.statb = StatusBox()
        self.statb.grid(row=1, column=0, padx=5, pady=0, sticky='N')

        self.actb = ActiveBox()
        self.actb.grid(row=2, column=0, padx=5, pady=15, sticky='ns')

        self.trapb = TrapBox()
        self.trapb.grid(row=0, column=2, rowspan=2, padx=15, pady=15, sticky='n')
        
        self.gcb = TrapBox()
        self.gcb.config(text="GC Column Profile")
        self.gcb.grid(row=2, column=2, rowspan=2, padx=10, pady=8, sticky='n')

        self.plotb = PlotBox()
        self.plotb.grid(row=0, column=4, rowspan=5, padx=15, pady=23, sticky='N')

        self.supb = PlotSupport()
        self.supb.grid(row=4, column=4, padx=5, pady=15, sticky='ns')

        self.textb = tk.Label(self, relief=tk.RAISED)
        self.t1 = tk.Text(self.textb, height=9, width=59, bg='white', foreground='black')
        self.t1.insert(tk.END, "GUI initialized succesfully\nPlease select the correct COM port...\n")
        self.t1.pack()
        self.textb.grid(row=4, column=1, columnspan=2, padx=14, pady=0)

        self.pb_val = tk.IntVar()
        
        self.pb = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=986, maximum=100, mode='determinate')
        self.pb.grid(row=5, column=0, columnspan=6, padx=15, sticky='w')

        self.cpr = tk.Label(self, text="Copyright The Regents of the University of California, Davis campus, 2013-18. All rights reserved.")
        self.cpr.grid(row=6, column=1, columnspan=6, padx=60, sticky='w')

        self.conb = tk.LabelFrame(self, text='Control', relief=tk.GROOVE, padx=5, pady=10)
        self.b1 = tk.Button(self.conb, text='RUN', width=15, height=1, bg="#c2ff64", command=self.strun, font="Times 12 bold") #6af94a" #e6e751
        self.b1.grid(row=2, column=0, sticky='n',pady=3, padx=3, columnspan=2)
        self.b2 = tk.Button(self.conb, text='ACTIVE', width=15, height=1, bg='#2998e4', command=self.active, font="Times 12 bold") ##effb2d
        self.b2.grid(row=1, column=0, sticky='s', pady=3, columnspan=2)
        self.b3 = tk.Button(self.conb, text='IDLE', width=15, height=1, bg='#625b91', command=self.idle, font="Times 12 bold") #D780C7 #35759c
        self.b3.grid(row=0, column=0, sticky='s', pady=3, columnspan=2)
        self.b4 = tk.Button(self.conb, text='Repeat', width=5, command=self.cycle_press) #
        self.b4.grid(row=4, column=0, sticky='s', pady=0)
        self.sep = ttk.Separator(self.conb, orient=tk.HORIZONTAL)
        self.sep.grid(row=3, column=0, columnspan=2, sticky='we', pady=3)
        self.e1 = ttk.Entry(self.conb, width=15)
        self.e1.grid(row=4, column=1)
        self.conb.grid(row=3, column=0, rowspan=2, sticky='n', pady=8)

    def cycle_press(self):
        if self.cyclebut == False:
            self.b4.config(relief=tk.SUNKEN)
            self.cyclebut = True
            self.e1.config(state='normal')
        else:
            self.b4.config(relief=tk.RAISED)
            self.cyclebut = False
            self.e1.config(state='disable')
                
            
        
    def idle_state(self):
        self.gcb.idle_state()
        self.trapb.idle_state()
        self.eventb.idle_state()
        self.supb.idle_state()
        self.comb.idle_state()
        self.plotb.idle_state()
        self.statb.idle_state()
        self.actb.idle_state() 
        self.b1.config(relief=tk.RAISED, state='disable')
        self.b2.config(relief=tk.RAISED, state='normal')
        self.b3.config(relief=tk.SUNKEN, state='disable')
        self.b4.config(state='normal')
        if self.cyclebut:
            self.e1.config(state='normal')
        self.statb.led.config(bg="#00FF00")
        self.pb.configure(value=0)
        
    def active_state(self):
        self.gcb.idle_state()
        self.trapb.idle_state()
        self.eventb.idle_state()
        self.supb.idle_state()
        self.comb.run_state()
        self.plotb.idle_state()
        self.statb.idle_state()
        self.actb.run_state() 
        self.b1.config(relief=tk.RAISED, state='normal')
        self.b2.config(relief=tk.SUNKEN, state='disable')
        self.b3.config(relief=tk.RAISED, state='normal')
        self.b4.config(state='normal')
        if self.cyclebut:
            self.e1.config(state='normal')
        self.statb.led.config(bg="#00FF00")
        self.pb.configure(value=0)
        
    def run_state(self):
        self.gcb.run_state()
        self.trapb.run_state()
        self.eventb.run_state()
        self.supb.run_state()
        self.comb.run_state()
        self.plotb.run_state()
        self.statb.run_state()
        self.actb.run_state()
        self.b1.config(relief=tk.SUNKEN, state='disable')
        self.b2.config(relief=tk.RAISED, state='normal')
        self.b3.config(relief=tk.RAISED, state='normal')
        self.b4.config(state='disable')
        self.e1.config(state='disable')
        self.statb.led.config(bg="#00FF00")
        
    def disc_state(self):
        self.gcb.disc_state()
        self.trapb.disc_state()
        self.eventb.disc_state()
        self.supb.disc_state()
        self.comb.disc_state()
        self.plotb.disc_state()
        self.statb.disc_state()
        self.actb.disc_state()
        self.b1.config(relief=tk.RAISED, state='disable')
        self.b2.config(relief=tk.RAISED, state='disable')
        self.b3.config(relief=tk.RAISED, state='disable')
        self.b4.config(state='disable')  #for testing purposes only
        self.e1.config(state='disable')
        self.statb.led.config(bg="#FF4A4A")
        self.pb.configure(value=0)
        
    def strun(self):
        global mode
        global first_run
        first_run = True
        mode = 'run'
        
    def idle(self):
        global mode
        global first_idle
        first_idle = True
        mode = 'idle'

    def active(self):
        global mode
        global first_active
        first_active = True
        mode = 'active'

    def extract_usr_inputs(self):
        global trap_temp_str
        global trap_time_str
        global event_str
        global event_str2
        global event_time_str
        global gc_temp_str
        global gc_time_str
        global act_str
        global cycle_str
        global mode
        global evt_readlist

        try:
            
            event_str = ""
            for self.c_child in self.eventb.c_child_list:
                evt = self.c_child.get()
                event_str += evt+", "
            temp1 = event_str.split(', ')
            temp2 = []
            for j in temp1:
                temp2.append(int(evt_readlist.index(j)))
            event_str2 = str(temp2)
            event_str2 = event_str2.strip("[]")
            
            event_time_str = ""
            for self.e_child in self.eventb.e_child_list:
                evt = self.e_child.get()
                if evt.isdigit() or evt == "":
                    event_time_str += evt+", "
                else:
                    self.badinput = True
                    event_time_str = ""
                    return            
                
            trap_temp_str = ""
            for self.T1_child in self.trapb.T_child_list:
                evt = self.T1_child.get()            
                if evt.isdigit() or evt == "":
                    trap_temp_str += evt+", "
                else:
                    self.badinput = True
                    trap_temp_str = ""
                    return  
            trap_time_str = ""
            for self.t1_child in self.trapb.t_child_list:
                evt = self.t1_child.get()            
                if evt.isdigit() or evt == "":
                    trap_time_str += evt+", "
                else:
                    self.badinput = True
                    trap_time_str = ""
                    return

            gc_temp_str = ""
            for self.T2_child in self.gcb.T_child_list:
                evt = self.T2_child.get()            
                if evt.isdigit() or evt == "":
                    gc_temp_str += evt+", "
                else:
                    self.badinput = True
                    gc_temp_str = ""
                    return
            gc_time_str = ""
            for self.t2_child in self.gcb.t_child_list:
                evt = self.t2_child.get()
                if evt.isdigit() or evt == "":
                    gc_time_str += evt+", "
                else:
                    self.badinput = True
                    gc_time_str = ""
                    return
                
            cycle_str = ""
            if self.cyclebut:
                cycle_str = self.e1.get()
                if cycle_str.isdigit() or cycle_str == "":
                    if cycle_str == "":
                        cycle_str = "0"
                else:
                    self.badinput = True
                    cycle_str = ""
                    return
                    
            else:
                cycle_str = "0"

            
            if str(self.actb.e1.cget('state')) == 'normal':    #check to make sure this guy is active
                act_str = ""
                for self.e_child in self.actb.e_child_list:
                    evt = self.e_child.get()            
                    if evt.isdigit():# or evt == "":
                        act_str += evt+", "
                    else:
                        self.badinput = True
                        act_str = ""
                        return
        except:
            self.badinput = True
            trap_temp_str = ""
            trap_time_str = ""
            event_str = ""
            event_str2 = ""
            event_time_str = ""
            gc_temp_str = ""
            gc_time_str = ""
            act_str = ""
            cycle_str = ""
    
        
    def upload_usr_inputs(self):
        global trap_temp_str
        global trap_time_str
        global event_str
        global event_time_str
        global gc_temp_str
        global gc_time_str
        global act_str
        global cycle_str
        global mode

        try:
            
            esl = event_str.split(", ")
            i = 0
            for self.c_child in self.eventb.c_child_list:
                self.c_child.set(esl[i])
                i += 1

            etsl = event_time_str.split(", ")
            i = 0
            for self.e_child in self.eventb.e_child_list:
                self.e_child.delete(0, 'end')
                self.e_child.insert(0, etsl[i])
                i += 1

            tTsl = trap_temp_str.split(", ")
            i = 0
            for self.T_child in self.trapb.T_child_list:
                self.T_child.delete(0, 'end')
                self.T_child.insert(0, tTsl[i])
                i += 1

            ttsl = trap_time_str.split(", ")
            i = 0
            for self.t_child in self.trapb.t_child_list:
                self.t_child.delete(0, 'end')
                self.t_child.insert(0, ttsl[i])
                i += 1

            gcTl = gc_temp_str.split(", ")
            i = 0
            for self.T_child in self.gcb.T_child_list:
                self.T_child.delete(0, 'end')
                self.T_child.insert(0, gcTl[i])
                i += 1

            gctl = gc_time_str.split(", ")
            i = 0
            for self.t_child in self.gcb.t_child_list:
                self.t_child.delete(0, 'end')
                self.t_child.insert(0, gctl[i])
                i += 1
                
            tpv = int(cycle_str)
            if tpv > 0:
                self.cyclebut = True
                self.b4.config(state='normal', relief=tk.SUNKEN)
                self.e1.config(state='normal')
                self.e1.delete(0, 'end')
                self.e1.insert(0, str(tpv))
            else:
                self.cyclebut = False
                self.b4.config(state='normal', relief=tk.RAISED)
                self.e1.config(state='normal')
                self.e1.delete(0, 'end')
                self.e1.config(state='disable')

            if mode == 'idle':
                actl = act_str.split(", ")
                i = 0
                for self.e_child in self.actb.e_child_list:
                    self.e_child.delete(0, 'end')
                    self.e_child.insert(0, actl[i])
                    i += 1
        except:
            self.badinput = True
            trap_temp_str = ""
            trap_time_str = ""
            event_str = ""
            event_time_str = ""
            gc_temp_str = ""
            gc_time_str = ""
            act_str = ""
            cycle_str = "0"

            
            

class ActiveBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Active Initials", relief=tk.GROOVE, padx=8, pady=5)

        self.t1 = tk.Label(self, text="Trap (C):", relief=tk.SUNKEN, width=12)
        self.t1.grid(row=0, column=0, sticky='w', pady=3)        
        self.t2 = tk.Label(self, text="GC (C):", relief=tk.SUNKEN, width=12)
        self.t2.grid(row=1,column=0, sticky='w', pady=3)
        self.t3 = tk.Label(self, text="TF1 (C):", relief=tk.SUNKEN, width=12)
        self.t3.grid(row=2, column=0, sticky="w", pady=3)
        self.t4 = tk.Label(self, text="TF2 (C):", relief=tk.SUNKEN, width=12)
        self.t4.grid(row=3, column=0, sticky="w", pady=3)
        self.t5 = tk.Label(self, text="Guard (C):", relief=tk.SUNKEN, width=12)
        self.t5.grid(row=4, column=0, sticky="w", pady=3)

        self.e1 = ttk.Entry(self, width=8)
        self.e1.grid(row=0, column=1, sticky='w')
        self.e2 = ttk.Entry(self, width=8)
        self.e2.grid(row=1, column=1, sticky='w')
        self.e3 = ttk.Entry(self, width=8)
        self.e3.grid(row=2, column=1, sticky='w')
        self.e4 = ttk.Entry(self, width=8)
        self.e4.grid(row=3, column=1, sticky='w')
        self.e5 = ttk.Entry(self, width=8)
        self.e5.grid(row=4, column=1, sticky='w')

        self.m_child_list = [self.t1, self.t2, self.t3, self.t4, self.t5]
        self.e_child_list = [self.e1, self.e2, self.e3, self.e4, self.e5]
        self.child_list = self.e_child_list + self.m_child_list
        
    def idle_state(self):
        for self.child in self.child_list:
            self.child.config(state='normal')
    def run_state(self):
        for self.child in self.child_list:
            self.child.config(state='disable')
    def disc_state(self):
        for self.child in self.child_list:
            self.child.config(state='disable')
        
            
        
        
class PlotSupport(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(relief=tk.GROOVE, text='Plot Control', padx=5, pady=7)

        self.b1 = tk.Button(self, text="Trap:", width=17, command=self.trapon, bg='#625b91')    #089cd4     #1f1663
        self.b1.grid(row=0, column=0, pady=1)
        self.b2 = tk.Button(self, text="GC:", width=17, command=self.gcon, bg='#2998e4')    #94bf7e
        self.b2.grid(row=1, column=0, pady=1)
        self.b3 = tk.Button(self, text="TF1:", width=17, command=self.tf1on, bg='#c2ff64')  #e6e751
        self.b3.grid(row=2, column=0, pady=1)
        self.b4 = tk.Button(self, text="TF2:", width=17, command=self.tf2on, bg='#ffa200')  #ff8551
        self.b4.grid(row=3, column=0, pady=1)
        self.b5 = tk.Button(self, text="Guard:", width=17, command=self.guardon, bg='#af4e4e')  #ee5b42     #8e0303
        self.b5.grid(row=4, column=0, pady=1)

        lin = ttk.Separator(self, orient=tk.VERTICAL)
        lin.grid(row=0, rowspan=5, column=1, padx=5, sticky='n, s')

        self.d1 = tk.Label(self, text="GC Fan:", width=18, relief=tk.SUNKEN)
        self.d1.grid(row=0, column=2, pady=2)
        self.d2 = tk.Label(self, text="2-Way Valve:", width=18, relief=tk.SUNKEN)
        self.d2.grid(row=1, column=2, pady=2)
        self.d3 = tk.Label(self, text="3-Way Valve:", width=18, relief=tk.SUNKEN)
        self.d3.grid(row=2, column=2, pady=2)
        self.d4 = tk.Label(self, text="Sample Pump:", width=18, relief=tk.SUNKEN)
        self.d4.grid(row=3, column=2, pady=2)
        self.d5 = tk.Label(self, text="Circulation Pump: ON", width=18, relief=tk.SUNKEN)
        self.d5.grid(row=4, column=2, pady=2)

        self.child_list = [self.b1, self.b2, self.b3, self.b4, self.b5, self.d1, self.d2, self.d3, self.d4, self.d5]

    def trapon(self):
        global DM
        if DM.trap_bool == False:
            DM.trap_bool = True
            self.b1.config(relief=tk.SUNKEN)
        else:
            DM.trap_bool = False
            self.b1.config(relief=tk.RAISED)

    def gcon(self):
        global DM
        if DM.gc_bool == False:
            DM.gc_bool = True
            self.b2.config(relief=tk.SUNKEN)
        else:
            DM.gc_bool = False
            self.b2.config(relief=tk.RAISED)

    def tf1on(self):
        global DM
        if DM.TF1_bool == False:
            DM.TF1_bool = True
            self.b3.config(relief=tk.SUNKEN)
        else:
            DM.TF1_bool = False
            self.b3.config(relief=tk.RAISED)

    def tf2on(self):
        global DM
        if DM.TF2_bool == False:
            DM.TF2_bool = True
            self.b4.config(relief=tk.SUNKEN)
        else:
            DM.TF2_bool = False
            self.b4.config(relief=tk.RAISED)

    def guardon(self):
        global DM
        if DM.guard_bool == False:
            DM.guard_bool = True
            self.b5.config(relief=tk.SUNKEN)
        else:
            DM.guard_bool = False
            self.b5.config(relief=tk.RAISED)
        
    def idle_state(self):
        for self.child in self.child_list:
            self.child.config(state='normal')
    def run_state(self):
        for self.child in self.child_list:
            self.child.config(state='normal')
    def disc_state(self):
        for self.child in self.child_list:
            self.child.config(state='disable')
            

        
class PlotBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Live Temperature Plot", relief=tk.GROOVE, padx=5, pady=10)
    def idle_state(self):
        pass
    def run_state(self):
        pass
    def disc_state(self):
        pass


class TrapBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Trap Profile", relief=tk.GROOVE, padx=5, pady=5)
        self.t1 = tk.Label(self, text="Temp. (C)")
        self.t1.grid(row=0, column=0)
        self.t2 = tk.Label(self, text="Time (ms)")
        self.t2.grid(row=0, column=1)

        self.e1 = ttk.Entry(self, width=9)
        self.e1.grid(row=1, column=0)
        self.e2 = ttk.Entry(self, width=9)
        self.e2.grid(row=2, column=0)
        self.e3 = ttk.Entry(self, width=9)
        self.e3.grid(row=3, column=0)
        self.e4 = ttk.Entry(self, width=9)
        self.e4.grid(row=4, column=0)
        self.e5 = ttk.Entry(self, width=9)
        self.e5.grid(row=5, column=0)
        self.e6 = ttk.Entry(self, width=9)
        self.e6.grid(row=6, column=0)
        self.e7 = ttk.Entry(self, width=9)
        self.e7.grid(row=7, column=0)

        self.T_child_list = [self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7]
        
        self.e8 = ttk.Entry(self, width=14)
        self.e8.grid(row=1, column=1)
        self.e9 = ttk.Entry(self, width=14)
        self.e9.grid(row=2, column=1)
        self.e10 = ttk.Entry(self, width=14)
        self.e10.grid(row=3, column=1)
        self.e11 = ttk.Entry(self, width=14)
        self.e11.grid(row=4, column=1)
        self.e12 = ttk.Entry(self, width=14)
        self.e12.grid(row=5, column=1)
        self.e13 = ttk.Entry(self, width=14)
        self.e13.grid(row=6, column=1)
        self.e14 = ttk.Entry(self, width=14)
        self.e14.grid(row=7, column=1)

        self.t_child_list = [self.e8, self.e9, self.e10, self.e11, self.e12, self.e13, self.e14]
        self.m_child_list = [self.t1, self.t2]
        self.child_list = self.T_child_list + self.t_child_list + self.m_child_list
        
    def idle_state(self):
        for self.child in self.child_list:
            self.child.config(state='normal')
    def run_state(self):
        for self.child in self.child_list:
            self.child.config(state='disable')
    def disc_state(self):
        self.run_state()


class EventsBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Boolean Events", relief=tk.GROOVE, padx=5, pady=5)
        self.t1 = tk.Label(self, text="Event")
        self.t1.grid(row=0, column=0, sticky='W')
        self.t2 = tk.Label(self, text="Time (ms)")
        self.t2.grid(row=0, column=1, sticky='W')
        self.b1 = ttk.Button(self, text="Load Profile", width=22, command=self.load_profile)
        self.b1.grid(row=17, column=0, pady=10, sticky='S')
        self.b2 = ttk.Button(self, text="Save Profile", width=19, command=self.save_profile)
        self.b2.grid(row=17, column=1, pady=10, sticky='S')

        
        self.c1 = ttk.Combobox(self, values=tup2)
        self.c1.grid(row=1, column=0)
        self.c1.current(0)
        self.c2 = ttk.Combobox(self, values=tup2)
        self.c2.grid(row=2, column=0)
        self.c2.current(0)
        self.c3 = ttk.Combobox(self, values=tup2)
        self.c3.grid(row=3, column=0)
        self.c3.current(0)
        self.c4 = ttk.Combobox(self, values=tup2)
        self.c4.grid(row=4, column=0)
        self.c4.current(0)
        self.c5 = ttk.Combobox(self, values=tup2)
        self.c5.grid(row=5, column=0)
        self.c5.current(0)
        self.c6 = ttk.Combobox(self, values=tup2)
        self.c6.grid(row=6, column=0)
        self.c6.current(0)
        self.c7 = ttk.Combobox(self, values=tup2)
        self.c7.grid(row=7, column=0)
        self.c7.current(0)
        self.c8 = ttk.Combobox(self, values=tup2)
        self.c8.grid(row=8, column=0)
        self.c8.current(0)
        self.c9 = ttk.Combobox(self, values=tup2)
        self.c9.grid(row=9, column=0)
        self.c9.current(0)
        self.c10 = ttk.Combobox(self, values=tup2)
        self.c10.grid(row=10, column=0)
        self.c10.current(0)
        self.c11 = ttk.Combobox(self, values=tup2)
        self.c11.grid(row=11, column=0)
        self.c11.current(0)
        self.c12 = ttk.Combobox(self, values=tup2)
        self.c12.grid(row=12, column=0)
        self.c12.current(0)
        self.c13 = ttk.Combobox(self, values=tup2)
        self.c13.grid(row=13, column=0)
        self.c13.current(0)
        self.c14 = ttk.Combobox(self, values=tup2)
        self.c14.grid(row=14, column=0)
        self.c14.current(0)
        self.c15 = ttk.Combobox(self, values=tup2)
        self.c15.grid(row=15, column=0)
        self.c15.current(0)

        self.c_child_list = [self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, self.c9, self.c10, self.c11, self.c12, self.c13, self.c14, self.c15]

        self.e1 = ttk.Entry(self)
        self.e1.grid(row=1, column=1)
        self.e2 = ttk.Entry(self)
        self.e2.grid(row=2, column=1)
        self.e3 = ttk.Entry(self)
        self.e3.grid(row=3, column=1)
        self.e4 = ttk.Entry(self)
        self.e4.grid(row=4, column=1)
        self.e5 = ttk.Entry(self)
        self.e5.grid(row=5, column=1)
        self.e6 = ttk.Entry(self)
        self.e6.grid(row=6, column=1)
        self.e7 = ttk.Entry(self)
        self.e7.grid(row=7, column=1)
        self.e8 = ttk.Entry(self)
        self.e8.grid(row=8, column=1)
        self.e9 = ttk.Entry(self)
        self.e9.grid(row=9, column=1)
        self.e10 = ttk.Entry(self)
        self.e10.grid(row=10, column=1)
        self.e11 = ttk.Entry(self)
        self.e11.grid(row=11, column=1)
        self.e12 = ttk.Entry(self)
        self.e12.grid(row=12, column=1)
        self.e13 = ttk.Entry(self)
        self.e13.grid(row=13, column=1)
        self.e14 = ttk.Entry(self)
        self.e14.grid(row=14, column=1)
        self.e15 = ttk.Entry(self)
        self.e15.grid(row=15, column=1)

        self.e_child_list = [self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7, self.e8, self.e9, self.e10, self.e11, self.e12, self.e13, self.e14, self.e15]
        self.m_child_list = [self.t1, self.t2, self.b1, self.b2]
        self.child_list = self.e_child_list + self.c_child_list + self.m_child_list
        
    def idle_state(self):
        for self.child in self.child_list:
            self.child.config(state='normal')
    def run_state(self):
        for self.child in self.child_list:
            self.child.config(state='disable')
    def disc_state(self):
        self.run_state()

    def save_profile(self):
        global mymain
        global trap_temp_str
        global trap_time_str
        global event_str
        global event_time_str
        global gc_temp_str
        global gc_time_str
        global act_str
        global cycle_str
        fil = tkf.asksaveasfile(mode='w', defaultextension='.spr')
        if fil is None:
            mymain.t1.insert(tk.END, "Save profile canceled"+'\n')
            mymain.t1.see(tk.END)
            return
        mymain.extract_usr_inputs()
        if mymain.badinput:
            mymain.t1.insert(tk.END, "An non-digit input has been entered\n")
            mymain.t1.see(tk.END)
            mymain.t1.insert(tk.END, "Run profile not saved"+'\n')
            mymain.t1.see(tk.END)
            fil.close()
            mymain.badinput = False
            return
        fil.write(trap_temp_str+'\n')
        fil.write(trap_time_str+'\n')
        fil.write(event_str+'\n')
        fil.write(event_time_str+'\n')
        fil.write(gc_temp_str+'\n')
        fil.write(gc_time_str+'\n')
        fil.write(act_str+'\n')
        fil.write(cycle_str+'\n')
        mymain.t1.insert(tk.END, "Run profile was saved as: "+os.path.basename(fil.name)+'\n')
        mymain.t1.see(tk.END)
        fil.close()


    def load_profile(self):
        global mymain
        global trap_temp_str
        global trap_time_str
        global event_str
        global event_time_str
        global gc_temp_str
        global gc_time_str
        global act_str
        global cycle_str
        fil2 = tkf.askopenfile(mode='r')
        if fil2 is None:
            mymain.t1.insert(tk.END, "Load profile canceled"+'\n')
            mymain.t1.see(tk.END)
            return
        temp01 = str(os.path.basename(fil2.name))
        if temp01[-3:] != "spr":
            mymain.t1.insert(tk.END, "   Wrong file extension"+'\n')
            mymain.t1.see(tk.END)
            return            
        trap_temp_str = fil2.readline()
        trap_time_str = fil2.readline()
        event_str = fil2.readline()
        event_time_str = fil2.readline()
        gc_temp_str = fil2.readline()
        gc_time_str = fil2.readline()
        act_str = fil2.readline()
        cycle_str = fil2.readline()
        mymain.upload_usr_inputs()

        if mymain.badinput:
            mymain.t1.insert(tk.END, "Profile from file "+os.path.basename(fil2.name)+" is corrupt"+'\n')
            mymain.t1.insert(tk.END, "  Please check all user input settings!"'\n')
            mymain.t1.see(tk.END)
            mymain.badinput = False
        else:
            mymain.t1.insert(tk.END, "Successfully loaded profile from: "+os.path.basename(fil2.name)+'\n')
            mymain.t1.see(tk.END)
        fil2.close()
                

class ComBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Communication", relief=tk.GROOVE, padx=8, pady=0)
        self.c1 = ttk.Combobox(self, values=tup, width=20)
        self.c1.current(0)
        self.c1.grid(row=0, column=0, columnspan=2)
        self.b1 = ttk.Button(self, text="Connect", width=10, command=self.connect_to_arduino)
        self.b1.grid(row=1, column=0, pady=7)
        self.b2 = ttk.Button(self, text="Quit", width=10, command=self.dest)
        self.b2.grid(row=1, column=1,pady=7)

    def run_state(self):
        self.c1.config(state='disable')
        self.b1.config(state='disable')
        self.b2.config(state='disable')
    def idle_state(self):
        self.c1.config(state='disable')
        self.b1.config(state='disable')
        self.b2.config(state='normal')
    def disc_state(self):
        self.c1.config(state='normal')
        self.b1.config(state='normal')
        self.b2.config(state='normal')
    def connect_to_arduino(self):
        global port
        port = self.c1.get()
    def dest(self):
        global loop
        loop = False

class StatusBox(tk.LabelFrame):
    def __init__(self):
        tk.LabelFrame.__init__(self)
        self.config(text="Status", relief=tk.GROOVE, padx=7, pady=5)

        self.t1 = tk.Label(self, relief=tk.SUNKEN)
        self.t1.grid(row=0, column=1, sticky="w")
        self.led = tk.Frame(self.t1, height=15, width=15, bg="#FF4A4A", relief=tk.GROOVE)
        self.led.pack()

        self.t2 = tk.Label(self, relief=tk.FLAT, text='Connection  ')
        self.t2.grid(row=0,column=0, sticky='e')

        self.t3 = tk.Label(self, text="Cycle: ", relief=tk.SUNKEN, width=20)
        self.t3.grid(row=1, column=0, columnspan=2, sticky="w", pady=4)
        self.t4 = tk.Label(self, text="Run Time (s): ", relief=tk.SUNKEN, width=20)
        self.t4.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)

    def run_state(self):
        self.t3.config(state='normal')
        self.t4.config(state='normal')
    def idle_state(self):
        self.t3.config(state='disable')
        self.t4.config(state='disable')
    def disc_state(self):
        self.t3.config(state='disable')
        self.t4.config(state='disable')


def logdata():
    global fname
    global mymain
    global mode
    filn = tkf.asksaveasfile(mode='w', defaultextension='.txt')
    if filn is None:
        mymain.t1.insert(tk.END, "No log file created... active mode aborted\n")
        mymain.t1.see(tk.END)
        mode = 'idle'
        return False
    fname = os.path.basename(filn.name)
    mymain.t1.insert(tk.END, "Run log created: "+fname+'\n')
    mymain.t1.see(tk.END)
    filn.close()
    return True

class DataManager():
    def __init__(self):

        self.cycle_num = 1
        self.cycle_num_loc = 1
        self.ard_time = 0
        self.ard_mode = 3
        self.ard_mode_mes1 = True
        self.ard_mode_mes2 = True

        self.pbo = 0
        self.missed_7 = 0

        self.goodtogo = False
        self.k = 0

        self.locmax = 0
        self.locmin = 0
        
        self.trap_temp = [0] * 200
        self.gc_temp = [0] * 200
        self.TF1_temp = [0] * 200
        self.TF2_temp = [0] * 200       
        self.guard_temp = [0] * 200
        self.act_time = np.arange(-200, 0)
        self.temp_list = [self.trap_temp, self.gc_temp, self.TF1_temp, self.TF2_temp, self.guard_temp]

        self.fan_str = ["OFF"]
        self.two_way_str = ["OFF"]
        self.three_way_str = ["OFF"]
        self.spump_str = ["OFF"]        

        self.bool_list = [self.fan_str, self.two_way_str, self.three_way_str, self.spump_str]

        self.run_trap_temp = [0]
        self.run_gc_temp = [0]
        self.run_TF1_temp = [0]
        self.run_TF2_temp = [0]        
        self.run_guard_temp = [0]
        self.run_time = [0]
        self.run_temp_list = [self.run_trap_temp, self.run_gc_temp, self.run_TF1_temp, self.run_TF2_temp, self.run_guard_temp]

        self.trap_bool = False
        self.gc_bool = False        
        self.TF1_bool = False
        self.TF2_bool = False
        self.guard_bool = False

       
    def distribute_data(self):
        global indata
        global mode
        global mymain
        global fname
        global cycle_str
        global first_active

        self.goodtogo = False
        self.mystr = str(indata)
        self.mystr = self.mystr.strip("b'")
        if (len(self.mystr) > 10):
            if (self.mystr[0] == "$") and (self.mystr[len(self.mystr)-1] == "%"):
                self.goodtogo = True
        self.mystr = self.mystr.strip("$%")
        self.mydlist = self.mystr.split(',')
        if (len(self.mydlist) == 13) and self.goodtogo:
            try:
                #print(str(self.mydlist))
                self.listnum = [int(i) for i in self.mydlist]
                mymain.supb.b1.config(text="Trap: "+str(self.listnum[0])+" (C)")
                mymain.supb.b2.config(text="GC: "+str(self.listnum[1])+" (C)")
                mymain.supb.b3.config(text="TF1: "+str(self.listnum[2])+" (C)")
                mymain.supb.b4.config(text="TF2: "+str(self.listnum[3])+" (C)")
                mymain.supb.b5.config(text="Guard: "+str(self.listnum[4])+" (C)")

                self.i = 0

                if (self.pbo > self.listnum[10]):
                    self.pbo = 0
                    self.ard_mode = 6 #this is to reset graphic for consecutive runs
                    mymain.pb_val.set(mymain.pb_val.get()+1)
                mymain.pb_val.set(mymain.pb_val.get() + self.listnum[10] - self.pbo)
                self.pbo = self.listnum[10]
                
                if ((mode == 'run') and (self.cycle_num_loc == self.cycle_num)) and (self.ard_mode != 6):  #potential bug be careful (might reset graphic if cycle number doesnt match all of a sudden)
                    for self.s1 in self.run_temp_list:
                        self.s1.append(self.listnum[self.i])
                        self.i += 1
                    mymain.statb.t4.config(text="Run Time (s): "+str(self.listnum[10]))
                    self.run_time.append(self.listnum[10])
                else:
                    if self.cycle_num_loc < self.cycle_num:
                        self.cycle_num_loc += 1
                    for self.i2 in self.run_temp_list:
                        self.i2[:] = []
                        self.i2.append(self.listnum[self.i])
                        self.i += 1
                    self.run_time[:] = []
                    self.run_time.append(self.listnum[10])
                    mymain.statb.t4.config(text="Run Time (s): ")

                self.i = 0                
                
                for self.i1 in self.temp_list:
                    k = 1
                    for j in self.i1:
                        self.i1[k-1] = self.i1[k]
                        k += 1
                        if k == 200:
                            break
                    self.i1[199] = self.listnum[self.i]
                    self.i += 1
                self.k += 1
                
                for self.i3 in self.bool_list:
                    if self.listnum[self.i] == 0:
                        self.i3[0] = "OFF"
                    else:
                        self.i3[0] = "ON"
                    self.i += 1
                    
                mymain.supb.d1.config(text="GC Fan: "+self.fan_str[0])
                mymain.supb.d2.config(text="2-Way Valve: "+self.two_way_str[0])
                mymain.supb.d3.config(text="3-Way Valve: "+self.three_way_str[0])
                mymain.supb.d4.config(text="Sample Pump: "+self.spump_str[0])

                self.cycle_num = self.listnum[self.i]
                if self.cycle_num_loc < self.cycle_num:
                    self.cycle_num_loc += 1
                self.i += 1

                self.ard_time = self.listnum[self.i]
                self.i += 1

                if mode == 'run':
                    mymain.statb.t3.config(text="Cycle: "+str(self.cycle_num)+"/"+str(int(cycle_str)+1))
                else:
                    self.ard_mode_mes1 = True
                    mymain.statb.t3.config(text="Cycle: ")
                    self.cycle_num_loc = 1
                    mymain.pb_val.set(0)
                
                self.ard_mode = self.listnum[self.i]
                #if ((self.ard_mode == 7) or (self.ard_mode == 2)) and (mode != 'active'):
                if ((self.ard_mode == 2) and (mode != 'active')):
                    self.missed_7 += 1
                    if self.missed_7 > 4:
                        first_active = True
                        mode = 'active'
                        self.cycle_num_loc = 1
                        self.missed_7 = 0
                    
                    
                if ((self.ard_mode == 7) and (mode != 'active')):
                    first_active = True
                    mode = 'active'
                    self.cycle_num_loc = 1
                      
                    
                if mode != 'idle' and ((first_active == False) or (first_run == False)):
                    try:
                        self.fi = open(fname, 'a')
                        self.fi.write(str(time.strftime("%H:%M:%S"))+', '+str(self.listnum).strip('[]')+'\n')
                        self.fi.close()
                    except:
                        mymain.t1.insert(tk.END, "  *Exception error 001\n")
                        mymain.t1.see(tk.END)
                        pass
                if self.listnum[12] != 0:
                    mymain.t1.insert(tk.END, "FATAL ERROR... \nLET PERIPHERALS COOL DOWN BEFORE UNPLUGGING SUITCASE\n")
                    mymain.t1.see(tk.END)
                        
            except:
                mymain.t1.insert(tk.END, "  *Exception error 002\n")
                mymain.t1.see(tk.END)
                return False
                pass
            return True            
        else:
            return False            

    def plot_data(self):
        global mode
        global mymain
        global fname
        global myp
        global can
        global myf

        

        myp.clear()
        gc.collect()
        if ((mode == 'run') and (len(self.run_time) > 4)) and (self.ard_mode != 6):
            if self.ard_mode != 6:
                mymain.pb.configure(variable=mymain.pb_val)
                if self.ard_mode_mes2:
                    mymain.t1.insert(tk.END, "Reached initial run temperature successfully\n")
                    mymain.t1.see(tk.END)
                    self.ard_mode_mes2 = False
                    self.ard_mode_mes1 = True
            self.locmax = 1
            self.locmin = 1000            
            if self.trap_bool:
                myp.plot(self.run_time[2:], self.run_trap_temp[2:], color='purple')
                if max(self.run_trap_temp) > self.locmax:
                    self.locmax = max(self.run_trap_temp)
                if min(self.run_trap_temp) < self.locmin:
                    self.locmin = min(self.run_trap_temp)
            if self.gc_bool:
                myp.plot(self.run_time[2:], self.run_gc_temp[2:], color='blue')
                if max(self.run_gc_temp) > self.locmax:
                    self.locmax = max(self.run_gc_temp)
                if min(self.run_gc_temp) < self.locmin:
                    self.locmin = min(self.run_gc_temp)
            if self.TF1_bool:                    
                myp.plot(self.run_time[2:], self.run_TF1_temp[2:], color='green')
                if max(self.run_TF1_temp) > self.locmax:
                    self.locmax = max(self.run_TF1_temp)
                if min(self.run_TF1_temp) < self.locmin:
                    self.locmin = min(self.run_TF1_temp)
            if self.TF2_bool: 
                myp.plot(self.run_time[2:], self.run_TF2_temp[2:], color='orange')
                if max(self.run_TF2_temp) > self.locmax:
                    self.locmax = max(self.run_TF2_temp)
                if min(self.run_TF2_temp) < self.locmin:
                    self.locmin = min(self.run_TF2_temp)
            if self.guard_bool: 
                myp.plot(self.run_time[2:], self.run_guard_temp[2:], color='red')
                if max(self.run_guard_temp) > self.locmax:
                    self.locmax = max(self.run_guard_temp)
                if min(self.run_guard_temp) < self.locmin:
                    self.locmin = min(self.run_guard_temp)
            if self.locmin == 1000:
                self.locmin = 0
            myp.set_ylim([self.locmin-5, self.locmax+5])
        else:
            if ((mode == 'run') and (self.ard_mode == 6)):
                if self.ard_mode_mes1:
                    mymain.t1.insert(tk.END, "Initial run temperature not reached\n  Please wait...\n")
                    mymain.t1.see(tk.END)
                    self.ard_mode_mes1 = False
                    self.ard_mode_mes2 = True
            self.locmax = 1
            self.locmin = 1000
            if self.trap_bool:                    
                myp.plot(self.act_time, self.trap_temp, color='purple')                
                if max(self.trap_temp) > self.locmax:
                    self.locmax = max(self.trap_temp)
                if min(self.trap_temp) < self.locmin:
                    self.locmin = min(self.trap_temp)
            if self.gc_bool:
                myp.plot(self.act_time, self.gc_temp, color='blue')
                if max(self.gc_temp) > self.locmax:
                    self.locmax = max(self.gc_temp)
                if min(self.gc_temp) < self.locmin:
                    self.locmin = min(self.gc_temp)
            if self.TF1_bool:                    
                myp.plot(self.act_time, self.TF1_temp, color='green')
                if max(self.TF1_temp) > self.locmax:
                    self.locmax = max(self.TF1_temp)
                if min(self.TF1_temp) < self.locmin:
                    self.locmin = min(self.TF1_temp)
            if self.TF2_bool: 
                myp.plot(self.act_time, self.TF2_temp, color='orange')
                if max(self.TF2_temp) > self.locmax:
                    self.locmax = max(self.TF2_temp)
                if min(self.TF2_temp) < self.locmin:
                    self.locmin = min(self.TF2_temp)
            if self.guard_bool: 
                myp.plot(self.act_time, self.guard_temp, color='red')
                if max(self.guard_temp) > self.locmax:
                    self.locmax = max(self.guard_temp)
                if min(self.guard_temp) < self.locmin:
                    self.locmin = min(self.guard_temp)
            if self.locmin == 1000:
                self.locmin = 0
            myp.set_ylim([self.locmin-5, self.locmax+5])
        myp.grid(True)
        can.show()
    

def write_to_suitcase(mystring):
    global Serial1

    fb = False
    time.sleep(0.05)
    temp1 = mystring.split(', ')
    temp2 = []
    for j in temp1:
        if j.isdigit():
            temp2.append(int(j))
        else:
            break
    temp3 = str(temp2)
    og_len = len(temp3)
    i = 0
    i_len = og_len - i;
    while i_len > 50:
        Serial1.write(temp3[i:(i+50)].encode())
        i += 50
        i_len -= 50
        time.sleep(0.05)
    Serial1.write(temp3[i:og_len].encode())
    time.sleep(0.5)
    indata = Serial1.readline()
    if indata == temp3.encode():
        fb = True
    return fb

def load_progress(mystring, mystring2):
    global mymain
    global cycle_str

    fb = False
    temp1 = mystring.split(', ')
    temp2 = mystring2.split(', ')
    temp3 = 10
    try:   
        for j in temp1:
            if j.isdigit():
                if int(j) == 9:
                    index_1 = temp1.index(j)
                    fb = True
                    temp3 = (int(temp2[index_1])/1000)*(int(cycle_str)+1)
                    break        
        mymain.pb.configure(maximum=temp3)
    except:
        mymain.t1.insert(tk.END, "End not found!... \n")
        mymain.t1.see(tk.END)
        mymain.badinput = True

    if fb == False:
        mymain.t1.insert(tk.END, "End not found!... \n")
        mymain.t1.see(tk.END)
        mymain.badinput = True
    

#global variables go here

DM = DataManager()
gc.enable()
loop = True
counter = 0
tup = "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14", "COM15", "COM16" 
tup2 = " ", "GC Fan ON", "2-Way Valve ON", "3-Way Valve ON",  "Sample Pump ON", "GC Fan OFF", "2-Way Valve OFF", "3-Way Valve OFF","Sample Pump OFF", "End"
evt_readlist = [" ", "GC Fan ON", "2-Way Valve ON", "3-Way Valve ON",  "Sample Pump ON", "GC Fan OFF", "2-Way Valve OFF", "3-Way Valve OFF","Sample Pump OFF", "End", ""]
lastmode = "disc"
mode = "disc"
port = "null"
first_run = True
first_idle = True
first_active = True
fname = ""
trap_temp_str = ""
trap_time_str = ""
event_str = ""
event_str2 = "" #events string that got converted to indexes brought from the event_str
event_time_str = ""
gc_temp_str = ""
gc_time_str = ""
act_str = ""
cycle_str = "0"
c_act_init = "5".encode('UTF-8','strict')
c_run_init = "4".encode()
c_act = "2".encode()
c_idl = "3".encode()
c_run = "1".encode()
c_green = "g".encode()

#Run all the setup commands here (they (should) run once
mymain = MainPage()
#mymain.resizable(width=tk.FALSE, height=tk.FALSE)
def removemain():
    global mymain
    mymain.t1.insert(tk.END, "Press 'Quit' to exit (Must be in 'Idle' mode)\n")
    mymain.t1.see(tk.END)
    
mymain.protocol('WM_DELETE_WINDOW', removemain)
time.sleep(0.05)

#setup for the figure that I will be using to plot temperature
myf = Figure(figsize=(3.42,4.63), dpi=80)
myp = myf.add_subplot(111)
myp.plot([0,0,0.0,0,0,10],[0,0,0,0,0,0])
myf.patch.set_facecolor("white")
myf.patch.set_visible(False)
myp.spines['left'].set_visible(False)
myp.spines['right'].set_visible(False)
myp.spines['top'].set_visible(False)
myp.spines['bottom'].set_visible(False)
listy = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 18]
list2 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 23]

can = FigureCanvasTkAgg(myf, mymain.plotb)
can.show()
can.get_tk_widget().pack(expand=True)

#main loop equivalent in arduino c  S     
while loop:
    mymain.update()
    if mode=='run':
        ################## Setup for run mode #####################################        
        if first_run:
            mymain.extract_usr_inputs()
            load_progress(event_str2, event_time_str)
            mymain.pb.configure(value = 0)
            if mymain.badinput:
                mymain.badinput = False
                mymain.t1.insert(tk.END, "User input error... Returning to active...\n")
                mymain.t1.see(tk.END)
                mode = 'active'
            else:                
                mymain.run_state()
                mymain.t1.insert(tk.END, "Entering run mode... \n")
                mymain.t1.see(tk.END)
                first_run=False
                lastmode = 'run'

                garbage2 = [0]
                while len(garbage2) != 13: #dummy read in order to clear serial buffer
                    time.sleep(0.05)
                    indata = Serial1.readline() 
                    garbage1 = str(indata)
                    garbage1 = garbage1.strip("b'")
                    garbage2 = garbage1.split(',')
                try:
                    time.sleep(0.05)
                    indata = Serial1.readline() #dummy read in order to clear serial buffer
                    time.sleep(0.05)
                    Serial1.write(c_run_init)    #send command to suitcase
                    time.sleep(0.15)
                    indata = Serial1.readline() #put arduino into receiving mode
                    if indata != c_run_init:
                        mymain.t1.insert(tk.END, "Communications error 1... Returning to active...\n")
                        mymain.t1.see(tk.END)
                        mymain.update()
                        time.sleep(5)
                        mode = 'active'
                    else:
                        mymain.t1.insert(tk.END, "Uploading run parameters...\n")
                        mymain.t1.see(tk.END)
                        mymain.update()
                        if write_to_suitcase(event_str2) != True: #indata != str(temp2).encode():
                            mymain.t1.insert(tk.END, "Communications error 2... Returning to active...\n")
                            mymain.t1.see(tk.END)
                            mymain.update()
                            time.sleep(5)
                            mode = 'active'
                        else:
                            if write_to_suitcase(event_time_str) != True:
                                mymain.t1.insert(tk.END, "Communications error 3... Returning to active...\n")
                                mymain.t1.see(tk.END)
                                mymain.update()
                                time.sleep(5)
                                mode = 'active'
                            else:                            
                                if write_to_suitcase(trap_temp_str) != True:
                                    mymain.t1.insert(tk.END, "Communications error 4... Returning to active...\n")
                                    mymain.t1.see(tk.END)
                                    mymain.update()
                                    time.sleep(5)
                                    mode = 'active'
                                else:                               
                                    if write_to_suitcase(trap_time_str) != True:
                                        mymain.t1.insert(tk.END, "Communications error 5... Returning to active...\n")
                                        mymain.t1.see(tk.END)
                                        mymain.update()
                                        time.sleep(5)
                                        mode = 'active'
                                    else:    
                                        if write_to_suitcase(gc_temp_str) != True:
                                            mymain.t1.insert(tk.END, "Communications error 6... Returning to active...\n")
                                            mymain.t1.see(tk.END)
                                            mymain.update()
                                            time.sleep(5)
                                            mode = 'active'
                                        else:
                                            if write_to_suitcase(gc_time_str) != True:
                                                mymain.t1.insert(tk.END, "Communications error 7... Returning to active...\n")
                                                mymain.t1.see(tk.END)
                                                mymain.update()
                                                time.sleep(5)
                                                mode = 'active'
                                            else:
                                                time.sleep(0.05)
                                                temp2 = int(cycle_str)                                             
                                                Serial1.write(str(temp2).encode()) #write cycle time
                                                time.sleep(0.4)
                                                indata = Serial1.readline()
                                                if indata != str(temp2).encode():
                                                    mymain.t1.insert(tk.END, "Communications error 8... Returning to active...\n")
                                                    mymain.t1.see(tk.END)
                                                    mymain.update()
                                                    time.sleep(5)
                                                    mode = 'active'
                                                else:
                                                    time.sleep(0.05)
                                                    Serial1.write(c_green)
                                                    time.sleep(0.05)
                                                    indata = Serial1.readline()
                                                    if indata != c_green:
                                                        mymain.t1.insert(tk.END, "  Upload failed\nReturning to active...\n")
                                                        mymain.t1.see(tk.END)
                                                        time.sleep(5)
                                                        mode = 'idle'
                                                    else:
                                                        mymain.t1.insert(tk.END, "  Success\n")
                                                        mymain.t1.see(tk.END)
                                                        mymain.t1.insert(tk.END, "Run mode initialized\n")
                                                        mymain.t1.see(tk.END)
                                                
                except:
                    mymain.t1.insert(tk.END, "Run mode failed\n")
                    mymain.t1.see(tk.END)
                    mode = 'idle'
             
        ################## Main starts here  for run mode #####################################
                
        try:
            time.sleep(0.03) #has to be here to avoid the program running too fast
            indata = Serial1.readline()            
            if DM.distribute_data():
                DM.plot_data()
        except:
            mymain.t1.insert(tk.END, "  *Exception error 003\n")
            mymain.t1.see(tk.END)
            mode = 'disc'
            
        if mode != 'run':
            first_active = True
            first_idle = True
            pass

    elif mode=='idle':
        #mymain.idle_state()
        if first_idle:
            mymain.idle_state()
            mymain.t1.insert(tk.END, "Idle mode initialized\n")
            mymain.t1.see(tk.END)
            first_idle=False
            lastmode = 'idle'

        try:
            time.sleep(0.03) #has to be here to avoid the program running too fast
            indata = Serial1.readline()            
            if DM.distribute_data():
                DM.plot_data()
                time.sleep(0.05)
                Serial1.write(c_idl)
                time.sleep(0.05)
                indata = Serial1.readline()
        except:
            mymain.t1.insert(tk.END, "  *Exception error 004\n")
            mymain.t1.see(tk.END)
            mode = 'disc'                   
            
            
    elif mode=='active':
        ######################## Setup starts here for active mode ###############################################
        if first_active:
            mymain.extract_usr_inputs()
            if mymain.badinput:
                mymain.badinput = False
                mymain.t1.insert(tk.END, "User input error... Returning to idle...\n")
                mymain.t1.see(tk.END)
                mode = 'idle'
            else:
                mymain.active_state()
                mymain.t1.insert(tk.END, "Entering Active mode...\n")
                mymain.t1.see(tk.END)
                mymain.update()
                first_active=False            

                if lastmode == 'idle':
                    if logdata():
                        garbage2 = [0]
                        while len(garbage2) != 13: #dummy read in order to clear serial buffer
                            time.sleep(0.05)
                            indata = Serial1.readline() 
                            garbage1 = str(indata)
                            garbage1 = garbage1.strip("b'")
                            garbage2 = garbage1.split(',')
                        try:
                            time.sleep(0.05)
                            indata = Serial1.readline() #dummy read in order to clear serial buffer
                            time.sleep(0.05)
                            #print(c_act_init)
                            #print('5')
                            Serial1.write(c_act_init)    #send command to suitcase
                            time.sleep(0.2)
                            indata = Serial1.readline()
                            #print(indata)
                            if indata != c_act_init:
                                mymain.t1.insert(tk.END, "Communications error 1... Returning to Idle...\n")
                                mymain.t1.see(tk.END)
                                mymain.update()
                                time.sleep(2)
                                mode = 'idle'
                            else:
                                mymain.t1.insert(tk.END, "Uploading initial conditions...\n")
                                mymain.t1.see(tk.END)
                                mymain.update()
                                if write_to_suitcase(act_str) != True:
                                    mymain.t1.insert(tk.END, "Communications error 2... Returning to Idle...\n")
                                    mymain.t1.see(tk.END)
                                    mymain.update()
                                    time.sleep(2)
                                    mode = 'idle'
                                else:
                                    time.sleep(0.05)
                                    Serial1.write(c_green)
                                    time.sleep(0.05)
                                    indata = Serial1.readline()
                                    if indata != c_green:
                                        mymain.t1.insert(tk.END, "  Upload failed\nReturning to Idle...\n")
                                        mymain.t1.see(tk.END)
                                        time.sleep(2)
                                        mode = 'idle'
                                    else:
                                        mymain.t1.insert(tk.END, "  Success\n")
                                        mymain.t1.see(tk.END)
                                        mymain.update()
                                
                        except:
                            mymain.t1.insert(tk.END, "Active mode failed\n")
                            mymain.t1.see(tk.END)
                            mode = 'idle'
                lastmode = 'active'
                mymain.t1.insert(tk.END, "Active mode initialized\n")
                mymain.t1.see(tk.END)

        ####################### Setup ends here and loop begins for active mode ###########################################              

        try:
            time.sleep(0.03) #has to be here to avoid the program running too fast
            indata = Serial1.readline()            
            if DM.distribute_data():
                DM.plot_data()
                time.sleep(0.05)
                Serial1.write(c_act)
                time.sleep(0.05)
                indata = Serial1.readline()
        except:
            mymain.t1.insert(tk.END, "  *Exception error 005\n")
            mymain.t1.see(tk.END)
            mode = 'disc'

        if mode != 'active':
            first_run = True
            first_idle = True
            pass

    elif mode=='disc':
        mymain.disc_state()
        first_idle = True
        time.sleep(0.05)        
        if port != 'null':
            try:
                Serial1 = Serial.Serial(port, 115200, timeout=0, writeTimeout=50)
                time.sleep(0.100)
                mymain.t1.insert(tk.END, "Connection Successful... "+port+" is online\n")
                mymain.t1.see(tk.END)
                mode = 'idle'
            except:
                mymain.t1.insert(tk.END, port+" is offline\n")
                mymain.t1.see(tk.END)
                port = 'null'
        if loop==False:
            mymain.destroy()
        lastmode = 'disc'

#exit the gui and end program
try:
    mymain.destroy()
except:
    pass
