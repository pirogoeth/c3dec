import Tkinter, tkMessageBox, contextlib
from contextlib import closing
from Tkinter import *

class ComparisonInterface(Frame):
    """ interface for the comparison dialog """
	
    def __init__(self, source_data, conversion_data, filename, master = None):
        """ initialise the comparison interface
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
            
        Frame.__init__(self, master)
        # store data
        self.source = source_data
        self.convert = conversion_data
        # window data
        self.master = master
        self.filename = filename
    	# draw window
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
	
    def updateTBPos(self, *args):
        try:
            self.source_t.yview(args[0], args[1], args[2])
            self.conv_t.yview(args[0], args[1], args[2])
        except (IndexError):
            self.source_t.yview(args[0], args[1])
            self.conv_t.yview(args[0], args[1])
        
    def createWindowElements(self):
        """ draw window elements """
            
        self.scrollbar = Scrollbar(self)    
        self.source_t = Text(self, yscrollcommand = self.scrollbar.set)
        self.conv_t = Text(self, yscrollcommand = self.scrollbar.set)
        self.source_bL = Label(self, text = "Source file:")
        self.conv_bL = Label(self, text = "Converted file:")
        self.accept_B = Button(self, text = "Accept", command = self.acceptData)
        self.cancel_B = Button(self, text = "Cancel", command = self.closeInterface)
        # scrollbar config
        self.scrollbar.config(command = self.updateTBPos)
        self.scrollbar.activate("arrow1")
        self.scrollbar.activate("arrow2")
        self.scrollbar.activate("slider")
        # add text to boxes
        self.source_t.insert(END, self.source)
        self.conv_t.insert(END, self.convert)
        # set grid positions
        self.scrollbar.grid(row = 1, column = 2, columnspan = 1, rowspan = 1, sticky = E+S+N)
        self.source_bL.grid(row = 0, column = 0)
        self.source_t.grid(row = 1, column = 0)
        self.conv_bL.grid(row = 0, column = 1)
        self.conv_t.grid(row = 1, column = 1)
        self.accept_B.grid(row = 2, column = 0)
        self.cancel_B.grid(row = 2, column = 1)

    def acceptData(self):
        """ save the data. """

        try:
            # write the converted data
            with closing(open(self.filename, 'w+')) as source:
                source.write(self.convert)
                source.close()
            # write the original data to a backup file
            with closing(open(self.filename + ".bak", "w+")) as backup:
                backup.write(self.source)
                backup.close()                    
        except IOError as (errno, strerr):
            tkMessageBox.showwarning(
                title = "IOError",
                message = "[%d] %s" % (errno, strerr)
            )
            self.closeInterface()
            return
        tkMessageBox.showinfo(
            title = "c3dec",
            message = "corrected file [%s] has been saved, backup file [%s] has been created." % (self.filename, self.filename + ".bak")
        )
        self.closeInterface()

    def closeInterface(self):
        """ close the interface without touching the data """
        
        self.destroy()
        self.master.quit()
        self.master.destroy()