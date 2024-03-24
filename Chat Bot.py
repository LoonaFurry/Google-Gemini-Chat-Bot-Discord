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
        question = message.content
        response = await ask_gemini(question)

        # Ensure there is a response before sending it back to Discord
        if response:
            await message.channel.send(response)
        else:
            await message.channel.send("Error: No response from Gemini API")


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
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print("API Response:", data)
                return None
        else:
            print("API Error:", response.text)
            return None
    except Exception as e:
        print("API Exception:", e)
        return None


if __name__ == "__main__":
    bot.run(TOKEN)