import traceback
import speech_recognition as sr
import threading as t
import time
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play


class BadCommandError:
    pass


def get_available_mics(print_info=True):
    if print_info:
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
    return sr.Microphone.list_microphone_names()


class CommandManager:
    def __init__(self, activation_words, print_run_info=True, activation_sentence="What command should I run?", activation_text="What command would you like to run?"):
        """
        The CommandManager allows users to register functions for
        calling them in an interactive shell!

        Each command can be registered in the CommandManager by wrapping
        it with the add_command decorator. This will store the function in
        the manager by looking at it's __name__ attribute and later allow
        users to reference the function by that name.

        All commands given to the CommandManager must start with "!",
        followed by the name of the registered function.
        """

        self.activation_words = activation_words
        self.commands = {}
        self.print_run_info = print_run_info
        self.activation_sentence = activation_sentence
        self.online = False
        self.activation_text = activation_text
        self.running_command = False

    def run(self):
        """
        Run the CommandManager repeatedly by asking for user input.
        """

        while True:
            try:
                if self.running_command is False:
                    self.start_thread()
            except Exception:
                traceback.print_exc()

    def run_command(self, user_input):
        """
        Parses input given by the user to determine an appropriate
        command to call. Commands may only be run one at a time and
        must start with "!"
        """

        # Strip out the prefix and use the first word as the command name
        command_name = user_input.split()[0]

        # Check that we have a command registered for that name.
        if command_name not in self.commands:
            print(f"Unknown command: '{user_input}'.")
            return

        self.commands[command_name]()

    def add_command(self, command):
        """
        Register the command to the manager. Uses the __name__ attribute of
        the function to store a reference to the function.
        """

        self.commands[command.__name__] = command
        return command

    def get_audio_online(self, timeout_var=2):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=timeout_var, phrase_time_limit=2)
            audio = r.recognize_google(audio)
            return audio
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            self.online = False

    def print_audio(self):
        if self.running_command is True:
            return
        self.running_command = True
        audio = str(self.get_audio_online())
        print(audio)
        if audio:
            for word in self.activation_words:
                if word in audio:
                    audio = audio.replace(f"{word}", "", 1)
                    audio = audio.strip()
                    print(word, audio)
                    if audio != "":
                        audio = audio.replace(" ", "_")
                        print(audio)
                        try:
                            self.run_command(audio)
                        except:
                            self.say("Say the name of the command you would like to run")
                            listen = self.get_audio_online(timeout_var=4)
                            print(f"listen = {listen}")
                            if listen is not None:
                                for command in self.commands.keys():
                                    if str(command) in str(listen):
                                        self.commands[command]()
                                        break
                    else:
                        self.say("Say the name of the command you would like to run")
                        listen = self.get_audio_online(timeout_var=4)
                        print(f"listen = {listen}")
                        for command in self.commands.keys():
                            if command in listen:
                                self.commands[command]()
                                break
                    break
        self.running_command = False

    def start_thread(self):
        thread = t.Thread(target=self.print_audio)
        thread.start()
        time.sleep(1)

    def say(self, text="Hello World!", lang="en"):

        # get audio from server
        tts = gTTS(text=text, lang=lang)

        # convert to file-like object
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # --- play it ---

        song = AudioSegment.from_file(fp, format="mp3")
        play(song)
