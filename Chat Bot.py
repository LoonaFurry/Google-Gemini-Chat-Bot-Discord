import discord
import requests
import asyncio
from discord.ext import commands

# Discord Bot Token
TOKEN = 'your-token-here'

# Define intents
intents = discord.Intents.all()
intents.messages = True  # Enable message events

# Gemini API endpoint
GEMINI_API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

# Your Gemini API key
GEMINI_API_KEY = 'your-token-here'

# Default response if Gemini API fails
DEFAULT_RESPONSE = "I'm sorry, I don't have a response for that."

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the bot is mentioned in the message
    if bot.user in message.mentions:
        # Check if the message content is not empty
        if message.content.strip():
            question = message.content
            response = await ask_gemini(question)
            await message.channel.send(response)
        else:
            # If the message content is empty, don't respond
            return

async def ask_gemini(question):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": question
                    }
                ]
            }
        ]
    }
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, params={'key': GEMINI_API_KEY}))
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0 and 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content'] and len(data['candidates'][0]['content']['parts']) > 0 and 'text' in data['candidates'][0]['content']['parts'][0]:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print("API Response:", data)
                return DEFAULT_RESPONSE
        else:
            print("API Error:", response.text)
            return DEFAULT_RESPONSE
    except Exception as e:
        print("API Exception:", e)
        return DEFAULT_RESPONSE


if __name__ == "__main__":
    bot.run(TOKEN)
