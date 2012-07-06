import Tkinter, tkMessageBox, ComparisonInterface, sys, contextlib
from Tkinter import *
from contextlib import closing
from ComparisonInterface import ComparisonInterface
from tkFileDialog import askopenfilename

class MainInterface(Frame):
    """ corrects text plots exported from civil3d to be imported correctly by hecras.
        @author: Sean Johnson, maiome development <miyoko@maio.me>
        @license:   This program is free software: you can redistribute it and/or modify
                    it under the terms of the GNU General Public License as published by
                    the Free Software Foundation, either version 3 of the License, or
                    (at your option) any later version.

                    This program is distributed in the hope that it will be useful,
                    but WITHOUT ANY WARRANTY; without even the implied warranty of
                    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                    GNU General Public License for more details.

                    You should have received a copy of the GNU General Public License
                    along with this program.  If not, see <http://www.gnu.org/licenses/>. """
    
    def __init__(self, master = None):
        """ initialise the interface """
        
        Frame.__init__(self, master)
        # set window title
        self.master.title("Civil3D Export Corrector")
        # Tk variables
        self.conv_elev_d = IntVar()
        # draw window elements
        self.grid(padx = 10, pady = 10)
        self.createWindowElements()
    
    def report_callback_exception(self, exc, val, tb):
        """ report exceptions """

        self.bell()
        tkMessageBox.showwarning(
		    "Exception %s" % (exc),
                    "[%s] %s" % (exc, val)
        )
        return
        
    def createWindowElements(self):
        """ draw the window elements that we need """
            
        # instantiate widgets
        self.in_fieldLb = Label(self, text = "Source file:")
        self.inFile = Entry(self)
        self.showFD = Button(self, text = "Browse", command = self.openFD)
        self.process_B = Button(self, text = "Process File", command = self.process_f)
        self.conv_elev = Checkbutton(self, text = "Convert elevations from meters to feet?", variable = self.conv_elev_d)
        # draw the elements
        self.in_fieldLb.grid(row = 0, column = 0)
        self.inFile.grid(row = 0, column = 1)
        self.showFD.grid(row = 0, column = 2)
        self.process_B.grid(row = 0, column = 3)
        self.conv_elev.grid(row = 1, column = 1)
    
    def openFD(self):
        """ open the Tkinter file dialog box and retrieve the chose value """
            
        self.filename = askopenfilename()
        self.inFile.delete(1, END)
        self.inFile.insert(1, self.filename.encode('utf-8'))

    def process_f(self):
        """ process the given file """

        # remove input fields to prettify for the new interface
        self.in_fieldLb.grid_forget()
        self.inFile.grid_forget()
        self.showFD.grid_forget()
        self.process_B.grid_forget()
        self.conv_elev.grid_forget()
        # actually do the beginnings of processing
        try:
            with closing(open(self.filename, 'r')) as f:
                data = f.read()
                converted_d = self.process_data(data)
        except (AttributeError) as e: 
            self.report_callback_exception(e, e.message + "\n\n" + "Please pick a valid file.", None)
            self.createWindowElements()
            return
        c_i = ComparisonInterface(data, converted_d, self.filename, master = self)
        c_i.mainloop()
    
    def process_data(self, data):
        """ actually perform the processing of the data

            oh, and sorry dad, I'm not going to comment this up -_- """
        
        # original data
        data_r = data.split('\n')
        # storage array for corrected data
        data_conv = []
        # state variable
        reading = False
        btype = ""
        # array for flipping values
        s = []
        # line count
        lc = 0
        for slice in data_r:
            lc += 1
            if len(slice) == 0:
                print 'blank slice @ %d' % (lc)
                btype = ""
                if len(s) > 0:
                    print 'dumping corrected data before slice @ %d' % (lc)
                    s.reverse()
                    [data_conv.append(piece) for piece in s]
                    s = []
                data_conv.append(slice)
            elif slice.startswith("REACH:"):
                reading = False
                data_conv.append(slice)
            elif slice.startswith("Endpoint:"):
                reading = True
                print 'Read ENDPOINT @ %d' % (lc)
                slice = slice.split()
                # this trims the last value off of the slice
                del slice[-1]
                d = slice[-1] + ','
                slice[-1] = d
                slice = ' '.join(slice)
                # this will do conversion of elevations if necessary
                if self.conv_elev_d.get() == 1:
                    slice = slice.split(", ")
                    slice[2] = slice[2].strip(",")
                    slice[2] = str(round(float(slice[2]) * 3.281, 2)) + ",,"
                    slice = ", ".join(slice)
                s.append(slice)
            elif slice.startswith("CENTERLINE:"):
                reading = True
                btype = "CENTERLINE"
                print 'Found CENTERLINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("CUT LINE:"):
                reading = True
                btype = "CUTLINE"
                print 'Found CUT LINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("SURFACE LINE:"):
                reading = True
                btype = "SURFACELINE"
                print 'Found SURFACE LINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("BEGIN STREAM NETWORK:"):
                print 'Found BEGIN STREAM NETWORK @ %d' % (lc)
                btype = "BSN"
                data_conv.append(slice)
                pass
            elif slice == "END:" and reading is True:
                reading = False
                print 'Found END @ %d' % (lc)
                s.reverse()
                [data_conv.append(piece) for piece in s]
                s = []
                data_conv.append(slice)
            elif slice.startswith('BANK POSITIONS:'):
                print 'Found BANK POSITIONS @ %d, recalculating' % (lc)
                q = slice.split(':')[1].split(' ')[1:]
                q = [a.split(',')[0] for a in q]
                q = [str(1 - eval(a)) for a in q]
                slice = "BANK POSITIONS: %s, %s" % (q[0], q[1])
                print 'New BANK POSITIONS @ %d calculated to be (%s, %s)' % (lc, q[0], q[1])
                data_conv.append(slice)
            elif reading is True and btype is "CENTERLINE":
                if self.conv_elev_d.get() == 1:
                    slice = slice.split(", ")
                    slice[2] = str(round(float(slice[2]) * 3.281, 2))
                    slice = ", ".join(slice)
                data_conv.append(slice)
            elif reading is True:
                s.append(slice)
            else:
                data_conv.append(slice)
        self.bell()
        return '\n'.join(data_conv)
