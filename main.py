import os
import discord
from discord.ext import commands
import poe
from flask import Flask
import threading

app = Flask(__name__)

# Load GPT-4 API tokens from environment variables
gpt4_tokens = os.environ['GPT4_TOKENS'].replace('"',
                                                '').replace(' ',
                                                            '').split(',\n')
current_token_index = 0
client = poe.Client(gpt4_tokens[current_token_index])

# Set up the intents for the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

# Load your Discord bot token from an environment variable
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary mapping user-friendly names to language model codenames
language_models = {
  "Sage": "capybara",
  "ChatGPT": "chinchilla",
  "GPT-4": "beaver",
  "Claude": "a2",
  "Claude+": "a2_2",
  "Dragonfly": "Dragonfly",
}

prompt_counter = 0
max_prompts = 600


@app.route("/")
def handle_request():
  return "Bot is running!"


def run_flask_server():
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')


@bot.command()
async def Ai(ctx, model: str = "ChatGPT", *, message: str):
  """Send a message to GPT-4 and get a response. Optionally specify a different language model."""
  global prompt_counter
  global current_token_index
  global client

  prompt_counter += 1

  if prompt_counter > max_prompts:
    prompt_counter = 1
    current_token_index = (current_token_index + 1) % len(gpt4_tokens)
    client = poe.Client(gpt4_tokens[current_token_index])

  async with ctx.typing():
    model_codename = language_models.get(
      model.capitalize(),
      "capybara")  # Default to "capybara" if model name not found
    response = ""
    for chunk in client.send_message(model_codename, message):
      response += chunk["text_new"]

    await ctx.send(response)


@bot.command()
async def info(ctx):
  """Display information on how to use the bot and list available models."""
  info_message = (
    "To use the bot, type `!Ai <model_name> <message>`.\n"
    "Replace `<model_name>` with the name of the language model you want to use (default is ChatGPT).\n"
    "Replace `<message>` with the text you want the AI to respond to.\n\n"
    "Available models:\n"
    f"{', '.join(language_models.keys())}\n")
  await ctx.send(info_message)


threading.Thread(target=run_flask_server, daemon=True).start()
# Run the bot using the Discord bot token from the environment variable
bot.run(os.environ['DISCORD_BOT_TOKEN'])
