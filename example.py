from Command_manager import CommandManager
import pyttsx3


engine = pyttsx3.init(driverName='sapi5')
engine.setProperty('rate', 150)


activation_words = ["voice assistant"]
bot = CommandManager(activation_words)


@bot.add_command
def hello():
    engine.say("I will speak this text")
    engine.runAndWait()


if __name__ == "__main__":
    bot.run()
