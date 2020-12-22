# -*- coding: utf-8 -*-
"""
Tkinter wrapper for things2takspaper.

Note: When building a native app with pyinstaller, the working directory of
the app (and of the export script) will be system root ("/"), which is NOT writable, at
least on MacOS. When the app is invoked from the terminal via "open", or
app.py is run with  "python app.py", the working directory is the shell's
current directory.

"""

from argparse import Namespace
import logging
import os
from pathlib import Path
import queue
from textwrap import dedent
from tkinter import filedialog
from tkinter import Tk
from tkinter import Button
from tkinter import Entry
from tkinter import Frame
from tkinter import Label
from tkinter import LabelFrame
from tkinter import StringVar
from tkinter import SUNKEN
from tkinter import Text
from tkinter import Radiobutton
from tkinter import N, NW, NE, S, E, W
from tkinter import X, LEFT, RIGHT, BOTH, END
from tkinter.scrolledtext import ScrolledText

import traceback

import export_things

# from setup import VERSION
VERSION = '1.0.1'

logger = logging.getLogger("t2tp")


class App:

    FMT_PROJECT = ("one file per project", "project")
    FMT_AREA = ("one file per area", "area")
    FMT_ALL = ("all in one", "all")

    FORMATS = (FMT_AREA, FMT_PROJECT, FMT_ALL)

    TARGET_FORMAT_FRAME_LABEL = "Output as:"

    EXPLANATION = dedent("""\
        Export your data from the Things 3 database to TaskPaper files.
    """)
    EXPORT_EXPLANATION = dedent("""\
        You will find all exported data in your Downloads folder.
    """)
    SELECT_FILE_EXPLANATION = dedent("""\
        (Note: When you click "Select File" the App will locate your default database automatically.
        Just click "Open" in the popup to select it.  If the text on the buttons is missing, reseize the window a little bit.)
    """)

    def __init__(self, master):

        self.source_type = None
        self.build_gui(master)

    def build_gui(self, master):
        master.title("Export Things 3 to Taskpaper v%s" % VERSION)

        file_frame = Frame(master)
        file_frame.pack(anchor=NW, fill=X)

        self.make_file_frame(file_frame)

        # buttons: convert
        buttons_frame = Frame(master)
        buttons_frame.pack(anchor=NW, fill=X)
        self.button_convert = Button(buttons_frame, text="Export", command=self.cmd_things2tp)
        self.button_convert.pack(anchor=NW, side=LEFT)

        T = Text(buttons_frame, height=2, width=90, font=("Helvetica", 13, "normal"))
        T.pack(anchor=NW, padx=10, pady=5)
        T.insert(END, self.EXPORT_EXPLANATION)

        logger_frame = LabelFrame(master, text="Exporter Output:", padx=5, pady=5)
        logger_frame.pack(anchor=NW, fill=X, padx=10, pady=10)
        self.console = ConsoleUi(logger_frame, master)

    def make_file_frame(self, frame):
        # source file
        self.filename = StringVar()

        T = Text(frame, height=1, width=90, font=("Helvetica", 14, "normal"))
        T.pack(anchor=NW, padx=10, pady=10)
        T.insert(END, self.EXPLANATION)

        # separator
        Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        source_frame = Frame(frame)
        source_frame.pack(anchor=NW, padx=10, pady=10)

        Label(source_frame, text="Things 3 database to export:").pack(side=LEFT)
        Entry(source_frame, text="foobar", textvariable=self.filename).pack(side=LEFT)
        Button(source_frame, text="Select File", command=self.cb_select_file).pack(side=LEFT)

        T = Text(frame, height=2, width=90, font=("Helvetica", 13, "normal"))
        T.pack(anchor=NW, padx=10, pady=5)
        T.insert(END, self.SELECT_FILE_EXPLANATION)

        # file format
        self.format = StringVar()
        self.format_frame = Frame(frame)
        self.format_frame.pack(anchor=NW, padx=10, pady=10)
        self._make_format_frame(self.format_frame, self.TARGET_FORMAT_FRAME_LABEL, self.format, self.FMT_AREA[1], self.FORMATS)

        # output file
        self.output_file = StringVar()
        output_frame = Frame(frame)
        output_frame.pack(anchor=NW, padx=10, pady=10)
        Label(output_frame, text="Output file ('export_data' if empty):").pack(side=LEFT)
        self.entry_target_file = Entry(output_frame, text="foobar", textvariable=self.output_file)
        self.entry_target_file.pack(side=LEFT, padx=10, pady=10)

    def _make_format_frame(self, frame, label, variable, default, available_formats):
        """Set available output formats."""
        variable.set(default)
        Label(frame, text=label).pack(side=LEFT)
        for text, mode in available_formats:
            Radiobutton(frame, text=text, variable=variable, value=mode).pack(side=LEFT)

    def clean_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def cb_select_file(self):
        filename = filedialog.askopenfilename(initialdir="~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/",
                                              title="Select file",
                                              defaultextension='*.sqlite3',
                                              filetypes=(("SQLite3 Files", "*.sqlite3"),
                                                         ("SQLite Files", "*.sqlite")))
        self.filename.set(filename)

    def cmd_things2tp(self):
        """Export the database. This is called when pressing the Export button"""
        logger.setLevel('INFO')
        # logger.setLevel('DEBUG')
        logger.info("starting conversion...")

        database = self.filename.get()
        if not database:
            logger.error("No database file set!!")
            return
        elif not os.path.exists(database):
            logger.error("database '%s' does not exist!" % database)
            return
        logger.info("database: %s" % database)

        output_format = self.format.get()
        logger.info("target format: %s" % output_format)
        if output_format not in [self.FMT_ALL[1], self.FMT_PROJECT[1], self.FMT_AREA[1]]:
            logger.error("unknown output format: %s" % output_format)
            return

        target = self.output_file.get()
        if not target:
            target = 'Things 3 export'
        # capture stdout if all-in-one
        if output_format == self.FMT_ALL[1]:
            target = export_things.RowObject.FILE_TMPL % target
        target = os.path.join(Path.home(), "Downloads", target)
        logger.info("target: %s" % target)

        args = Namespace(database=database,
                         target=target,
                         format=output_format,
                         stdout=False,
                         called_from_gui=True)
        try:
            export_things.export(args)
        except Exception:
            tb = traceback.format_exc()
            logger.error(tb)
        else:
            logger.info("export finished")

        logger.info("ready")


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """
    def __init__(self, log_queue):
        super(QueueHandler, self).__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame, master):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)
        self.scrolled_text.pack(fill=BOTH, expand=1)
        self.button_quit = Button(self.frame, text="Quit", fg="red", command=master.quit)
        self.button_quit.pack(anchor=NE, side=RIGHT)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


def main():
    root = Tk()
    App(root)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
