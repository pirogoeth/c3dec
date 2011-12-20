import Tkinter, ComparisonInterface
from Tkinter import *
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
        # draw window elements
        self.grid(padx = 10, pady = 10)
        self.createWindowElements()
            
    def createWindowElements(self):
        """ draw the window elements that we need """
            
        # instantiate widgets
        self.in_fieldLb = Label(self, text = "Source file:")
        self.inFile = Entry(self)
        self.showFD = Button(self, text = "Browse", command = self.openFD)
        self.process_B = Button(self, text = "Process File", command = self.process_f)
        # draw the elements
        self.in_fieldLb.grid(row = 0, column = 0)
        self.inFile.grid(row = 0, column = 1)
        self.showFD.grid(row = 0, column = 2)
        self.process_B.grid(row = 0, column = 3)
    
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
        # actually do the beginnings of processing
        f = open(self.filename, 'r')
        data = f.read()
        converted_d = self.process_data(data)
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
        # array for flipping values
        s = []
        # line count
        lc = 0
        for slice in data_r:
            lc += 1
            if len(slice) == 0:
                print 'blank slice @ %d' % (lc)
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
                del slice[-1]
                d = slice[-1] + ','
                slice[-1] = d
                s.append(' '.join(slice))
            elif slice.startswith("CENTERLINE:"):
                reading = True
                print 'Found CENTERLINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("CUT LINE:"):
                reading = True
                print 'Found CUT LINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("SURFACE LINE:"):
                reading = True
                print 'Found SURFACE LINE block @ %d' % (lc)
                data_conv.append(slice)
            elif slice.startswith("BEGIN STREAM NETWORK:"):
                print 'Found BEGIN STREAM NETWORK @ %d' % (lc)
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
            elif reading is True:
                s.append(slice)
            else:
                data_conv.append(slice)
        self.bell()
        return '\n'.join(data_conv)
