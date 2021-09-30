from Command_handler import CommandManager


activation_words = ["voice assistant", "voice assist", "voice"]
bot = CommandManager(activation_words)


@bot.add_command
def hello():
    bot.say("I will speak this text")


if __name__ == "__main__":
    bot.run()
