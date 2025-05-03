import gdown
import os
from rasa.core.agent import Agent
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Google Drive model file
file_id = '184ZgbJASeV92FHNaDuT9ZT3F0hmIoIWY'
url = f'https://drive.google.com/uc?export=download&id={file_id}'
model_file = 'rasa_model.tar.gz'

# Download model if not already downloaded
if not os.path.exists(model_file):
    print("Downloading model...")
    gdown.download(url, model_file, quiet=False)
else:
    print("Model already downloaded.")

# Load Rasa model
print("Loading model...")
agent = Agent.load(model_file)
print("Model loaded.")

# Handle incoming messages
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    responses = agent.handle_text(user_message)
    if responses:
        update.message.reply_text(responses[0]['text'])
    else:
        update.message.reply_text("Sorry, I didn't understand that.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! I'm your Rasa bot. How can I help?")

def main():
    updater = Updater(token="8032964681:AAFRC6k6MbgRbkt1-HyVfwg9KV6uQPM03Mo", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
