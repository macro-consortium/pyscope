# Built-in Python imports
from tkinter import *
import tkinter.ttk
import tkinter.filedialog as filedialog
from tkinter.scrolledtext import ScrolledText

import sys
import _thread
import time

# iota imports
from . import convert
from . import logutil
from . import telrun_status

def main():
    show_gui()

def start_gui_in_thread():
    _thread.start_new_thread(show_gui, ())

def show_gui():
    root = Tk()
    root.title("Telrun")
    frame = TelrunFrame(root)
    frame.grid(column=0, row=0, sticky=(N, S, E, W))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()

class TelrunFrame(tkinter.ttk.Frame):
    def __init__(self, parent):
        tkinter.ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build_gui()
        
        self.update()

    def build_gui(self):
        header_font = "sans 12 bold"

        tkinter.ttk.Label(self, text="System Status", font=header_font).grid(column=0, row=0)
        self.system_status_widget = SystemStatusWidget(self)
        self.system_status_widget.grid(column=0, row=1, sticky=N)

        tkinter.ttk.Label(self, text="Current scan", font=header_font).grid(column=1, row=0)
        self.current_scan_widget = ScanWidget(self)
        self.current_scan_widget.grid(column=1, row=1)

        tkinter.ttk.Label(self, text="Next scan", font=header_font).grid(column=2, row=0)
        self.next_scan_widget = ScanWidget(self)
        self.next_scan_widget.grid(column=2, row=1)

        self.log_text = ScrolledText(self, width=40, height=10)
        self.log_text.grid(column=0, row=2, columnspan=4, sticky=(N, S, E, W))
        self.rowconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def update(self):
        while logutil.log_message_queue.qsize() > 0:
            log_message = logutil.log_message_queue.get()
            self.log_text.insert(END, log_message + "\n")
            self.log_text.see(END)

        self.system_status_widget.update_display()
        self.current_scan_widget.display_scan(telrun_status.current_scan)
        self.next_scan_widget.display_scan(telrun_status.next_scan)

        self.after(200, self.update)

class SystemStatusWidget(tkinter.ttk.Frame):
    def __init__(self, parent):
        tkinter.ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build_widget()

    def build_widget(self):
        rowadder = RowAdder(self)

        self.sun_elevation = rowadder.add_row("Sun elevation:")
        self.mount_state = rowadder.add_row("Mount:")
        self.camera_state = rowadder.add_row("Camera:")
        self.autofocus_state = rowadder.add_row("Autofocus:")
        self.current_scan_number = rowadder.add_row("Scan number:")
        self.total_scan_count = rowadder.add_row("Total scans:")
        self.skipped_scan_count = rowadder.add_row("Skipped scans:")
        self.seconds_until_autofocus = rowadder.add_row("Sec until autofocus:")
        self.pressure = rowadder.add_row("WX pressure (mB):")
        self.temperature = rowadder.add_row("WX temperature (C):")
        self.windspeed = rowadder.add_row("WX windspeed (kph):")
        self.winddir = rowadder.add_row("WX wind dir (degs):")
        self.humid = rowadder.add_row("WX humidity %:")
        self.wxage = rowadder.add_row("WX age (sec):")

    def update_display(self):
        if telrun_status.sun_elevation_func is not None:
            self.sun_elevation.set("%.3f" % telrun_status.sun_elevation_func())
        else:
            self.sun_elevation.set("Unknown")

        self.mount_state.set(telrun_status.mount_state)
        self.camera_state.set(telrun_status.camera_state)
        self.autofocus_state.set(telrun_status.autofocus_state)
        self.current_scan_number.set(telrun_status.current_scan_number)
        self.total_scan_count.set(telrun_status.total_scan_count)
        self.skipped_scan_count.set(telrun_status.skipped_scan_count)

        autofocus_delay = telrun_status.next_autofocus_time - time.time()
        if autofocus_delay < 0:
            self.seconds_until_autofocus.set("Immediately")
        else:
            self.seconds_until_autofocus.set("%d" % autofocus_delay)

        if telrun_status.get_weather_func is not None:
            latest_weather = telrun_status.get_weather_func()
            self.pressure.set(latest_weather.pressure_millibars)
            self.temperature.set(latest_weather.temperature_celsius)
            self.windspeed.set(latest_weather.wind_speed_kph)
            self.winddir.set(latest_weather.wind_direction_degs_east_of_north)
            self.humid.set(latest_weather.humidity_percent)
            self.wxage.set(latest_weather.age_seconds())

class ScanWidget(tkinter.ttk.Frame):
    def __init__(self, parent):
        tkinter.ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build_widget()

    def build_widget(self):
        rowadder = RowAdder(self)

        self.target_name = rowadder.add_row("Target:")
        self.target_ra = rowadder.add_row("Target RA:")
        self.target_dec = rowadder.add_row("Target Dec:")
        self.ra_offset = rowadder.add_row("RA Offset:")
        self.dec_offset = rowadder.add_row("Dec Offset:")
        self.filter = rowadder.add_row("Filter:")
        self.exp_length = rowadder.add_row("Exposure (sec):")
        self.binning = rowadder.add_row("Binning:")
        self.subframe = rowadder.add_row("Subframe:")
        self.shutter = rowadder.add_row("Shutter:")
        self.sched_file = rowadder.add_row("Sched file:")
        self.image_file = rowadder.add_row("Image file:")
        self.comment = rowadder.add_row("Comment:")
        self.title = rowadder.add_row("Title:")
        self.observer = rowadder.add_row("Observer:")
        self.ext_cmd = rowadder.add_row("ExtCmd:")
        self.ccd_calib = rowadder.add_row("CCDCalib:")
        self.priority = rowadder.add_row("Priority:")
        self.start_time = rowadder.add_row("Start time:")

    def display_scan(self, scan):
        if scan is None:
            self.sched_file.set("None")
            # TODO: Clear out other fields
            return

        #self.target_ra.set(
        #        convert.to_dms(convert.rads_to_hours(scan.obj.ra)))

        #self.target_dec.set(
        #        convert.to_dms(convert.rads_to_degs(scan.obj.dec)))

        self.sched_file.set(scan.schedfn)
        self.image_file.set(scan.imagefn)
        self.comment.set(scan.comment)
        self.title.set(scan.title)
        self.observer.set(scan.observer)
        self.target_name.set(scan.obj.name)
        self.ra_offset.set(scan.rao)
        self.dec_offset.set(scan.deco)
        self.ext_cmd.set(scan.extcmd)
        self.ccd_calib.set(scan.ccdcalib)
        self.subframe.set("%dx%d+%d+%d" % (
            scan.sw,
            scan.sh,
            scan.sx,
            scan.sy
            ))
        self.binning.set("%dx%d" % (
            scan.binx,
            scan.biny
            ))
        self.exp_length.set(scan.dur)
        self.shutter.set(scan.shutter)
        self.filter.set(scan.filter)
        self.priority.set(scan.priority)
        self.start_time.set(scan.starttm)

class RowAdder:
    def __init__(self, container):
        self.container = container
        self.next_row = 0

    def add_row(self, label_text):
        label = tkinter.ttk.Label(self.container, text=label_text)
        label.grid(column=0, row=self.next_row, sticky=(E))

        string_var = StringVar()
        entry = tkinter.ttk.Entry(self.container, textvariable=string_var)
        entry.grid(column=1, row=self.next_row, sticky=(E,W))

        self.next_row += 1

        return string_var



if __name__ == "__main__":
    main()
