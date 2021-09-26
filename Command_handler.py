import speech_recognition as sr
import traceback
import pyttsx3


engine = pyttsx3.init(driverName='sapi5') 
engine.setProperty('rate', 150)


class BadCommandError:
    pass


class CommandManager:
    def __init__(self, activation_words, print_run_info=True, activation_sentence="What command should I run?"):
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

    def run(self):
        """
        Run the CommandManager repeatedly by asking for user input.
        """

        while True:
            try:
                done = False
                user_input = input("Enter command: ")
                for word in self.activation_words:
                    if word in user_input and done is False:
                        word = user_input.split(word, 1)[1]
                        self.run_command(word[1:])
                        done = True
                if done is False:
                    raise "No activation Phrase was provided."
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

    def get_available_mics(self, print_info=True):
        if print_info:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
        return sr.Microphone.list_microphone_names()

    def get_audio(self):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
            audio = r.recognize_google(audio)
            return audio
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            self.online = False
