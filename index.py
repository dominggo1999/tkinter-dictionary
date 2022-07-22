from tkinter import *
from tkinter import ttk
from scrape import *
from gtts import gTTS
import os
from datetime import datetime
from uuid import uuid4
from pygame import mixer
import glob


window = Tk()
window.title("Dictionary")
window.geometry("400x300")

# Audio player
mixer.init()


temp_dir = "temp_tts"
# Create temporary folder for google tts
is_exist = os.path.exists(temp_dir)
if(not is_exist):
    os.makedirs(temp_dir)
else:
    filelist = glob.glob(os.path.join(temp_dir, "*"))
    for f in filelist:
        os.remove(f)


class dictionary():
    def __init__(self):
        self.word = ""
        self.word_sv = StringVar()
        self.word_sv.trace_add("write", self.save_input)

        # Frames
        self.frame = Frame(window).grid()
        self.left_frame = Frame(self.frame)
        self.left_frame.grid(row=0, column=0)
        self.right_frame = Frame(self.frame)
        self.right_frame.grid(row=0, column=1)

        self.indo_list_wrapper = None
        self.indo_list_type = []
        self.indo_list_def = []

        # Searchbar
        self.search_bar = Frame(self.left_frame)
        self.search_bar.grid(row=0, column=0, sticky=W)

        # Audio
        self.previous_audio_file = ""

        # Init components
        self.input_field()
        self.submit_button()
        self.audio_button()

    def input_field(self):
        entry = Entry(self.search_bar, textvariable=self.word_sv)

        # Submit using enter key
        entry.bind("<Return>", self.search)

        entry.grid(row=0, column=0, sticky=W)

    def submit_button(self):
        button = Button(self.search_bar, text="Search",
                        command=self.search)
        button.grid(row=0, column=1, sticky=W)

    def save_input(self, var, index, mode):
        self.word = self.word_sv.get()

    def search(self, _=None):
        self.indo()

    def indo(self):
        self.clean_up_item([self.indo_list_wrapper])
        self.clean_up_list([self.indo_list_type, self.indo_list_def])

        res = indo_definitions(self.word)["indonesia"]
        if(len(res) == 0):
            return

        self.indo_list_wrapper = Frame(self.left_frame, pady=20)

        for idx, item in enumerate(res):

            try:
                definition = Label(self.indo_list_wrapper,
                                   text=item["def"])
                type = Label(self.indo_list_wrapper,
                             text=item["type"], justify="left")

                self.indo_list_def.append(definition)
                self.indo_list_type.append(type)

                type.grid(row=idx, column=0, sticky=W)
                definition.grid(row=idx, column=1, sticky=W)
            except:
                return

        self.indo_list_wrapper.grid(row=2, column=0, sticky=W)

    def audio_button(self):
        audio_button = Button(
            self.left_frame, text="Play Audio", command=self.play_audio)
        audio_button.grid(row=1, column=0, sticky=W)

    def play_audio(self):
        if self.word and not mixer.music.get_busy():
            # Remove previous audio
            if(self.previous_audio_file):
                mixer.music.unload()
                os.remove(self.previous_audio_file)

            # Enforce unique filename
            filename = temp_dir + "/" "voice"+str(uuid4())+".mp3"
            self.previous_audio_file = filename
            tts = gTTS(self.word)
            tts.save(filename)
            mixer.music.load(filename)  # Load the mp3
            mixer.music.play()  # Play it

    def clean_up_list(self, list):
        if(list):
            for nested in list:
                if(nested):
                    for l in nested:
                        l.destroy()

    def clean_up_item(self, componentList):
        if(componentList):
            for item in componentList:
                if(item):
                    item.destroy()


if __name__ == "__main__":
    dictionary()
    window.mainloop()
