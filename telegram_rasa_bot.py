import gdown
import rasa
from rasa.core.agent import Agent
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Google Drive file ID (from the link you provided)
file_id = '184ZgbJASeV92FHNaDuT9ZT3F0hmIoIWY'
url = f'https://drive.google.com/uc?export=download&id={file_id}'

# Download the model from Google Drive
output = 'rasa_model.tar.gz'
gdown.download(url, output, quiet=False)

# Load the Rasa model
agent = Agent.load(output)

# Define function to handle messages from the Telegram bot
def handle_message(update, context):
    user_message = update.message.text
    # Get the response from Rasa
    response = agent.handle_text(user_message)
    # Send the response back to the Telegram user
    update.message.reply_text(response[0]['text'])

# Define a function to start the bot (command handler for "/start")
def start(update, context):
    update.message.reply_text("Hello! How can I assist you?")

# Set up the Telegram bot with your token
def main():
    updater = Updater(token="8032964681:AAFRC6k6MbgRbkt1-HyVfwg9KV6uQPM03Mo", use_context=True)
    dispatcher = updater.dispatcher

    # Handlers for the start command and incoming messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
