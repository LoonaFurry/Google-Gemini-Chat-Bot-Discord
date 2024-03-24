import discord
import requests
import asyncio
from discord.ext import commands
import random

# Discord Bot Token
TOKEN = 'your-token-here'

# Define intents
intents = discord.Intents.all()
intents.messages = True  # Enable message events

# Gemini API endpoint
GEMINI_API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

# Your Gemini API key
GEMINI_API_KEY = 'your-token-here'

# Spam and swear word detection threshold
SPAM_THRESHOLD = 0.7
SWEAR_THRESHOLD = 0.5

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        # Get the message content without the mention
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()

        # Generate a response using the Gemini API
        response = await generate_response(content)

        # Send the response to the channel
        await message.channel.send(response)

    # Check if the message contains swear words or is spam
    if await is_swear_or_spam(message.content):
        await message.delete()
        delete_message = await message.channel.send(f"{message.author.mention}, please refrain from using inappropriate language or spamming.")
        await asyncio.sleep(10)
        await delete_message.delete()

async def generate_response(prompt):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, params={'key': GEMINI_API_KEY}))
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print("API Response:", data)
        else:
            print("API Error:", response.text)
    except Exception as e:
        print("API Exception:", e)
    return "I'm sorry, I couldn't generate a response."

async def is_swear_or_spam(text):
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ]
    }
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers, params={'key': GEMINI_API_KEY}))
        if response.status_code == 200:
            data = response.json()
            if 'promptFeedback' in data:
                prompt_feedback = data['promptFeedback']
                if 'blockReason' in prompt_feedback and prompt_feedback['blockReason'] == 'SAFETY':
                    if 'safetyRatings' in prompt_feedback:
                        safety_ratings = prompt_feedback['safetyRatings']
                        for rating in safety_ratings:
                            if rating['category'] == 'HARM_CATEGORY_HARASSMENT' and rating['probability'] in ['HIGH', 'MEDIUM']:
                                return True
                            elif rating['category'] == 'HARM_CATEGORY_SEXUALLY_EXPLICIT' and rating['probability'] == 'LOW':
                                return True
                else:
                    print("API Response:", data)
            else:
                print("API Response:", data)
        else:
            print("API Error:", response.text)
    except Exception as e:
        print("API Exception:", e)
    return False

if __name__ == "__main__":
    bot.run(TOKEN)