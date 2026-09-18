import os
import json
import time
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from ai_chat import get_ai_response, get_code_help, get_translate, get_summarize

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

COOLDOWNS = {}
COOLDOWN_SECONDS = 3

def check_cooldown(user_id):
    now = time.time()
    if user_id in COOLDOWNS and now - COOLDOWNS[user_id] < COOLDOWN_SECONDS:
        return False
    COOLDOWNS[user_id] = now
    return True

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)

@bot.tree.command(name="ask", description="Ask the AI anything")
@app_commands.describe(question="Your question")
async def ask_slash(interaction: discord.Interaction, question: str):
    if not check_cooldown(interaction.user.id):
        await interaction.response.send_message("Slow down! Wait a few seconds.", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_ai_response(question)
    embed = discord.Embed(description=response, color=0x5865F2)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="AI Assistant | Free tier")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="code", description="Get help with coding")
@app_commands.describe(code="Your code or question about code")
async def code_slash(interaction: discord.Interaction, code: str):
    if not check_cooldown(interaction.user.id):
        await interaction.response.send_message("Slow down! Wait a few seconds.", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_code_help(code)
    embed = discord.Embed(title="Code Helper", description=response, color=0x57F287)
    embed.set_footer(text="AI Code Assistant")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="summarize", description="Summarize text")
@app_commands.describe(text="Text to summarize")
async def summarize_slash(interaction: discord.Interaction, text: str):
    if not check_cooldown(interaction.user.id):
        await interaction.response.send_message("Slow down! Wait a few seconds.", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_summarize(text)
    embed = discord.Embed(title="Summary", description=response, color=0xFEE75C)
    embed.set_footer(text="AI Summarizer")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="translate", description="Translate text to another language")
@app_commands.describe(text="Text to translate", language="Target language")
async def translate_slash(interaction: discord.Interaction, text: str, language: str):
    if not check_cooldown(interaction.user.id):
        await interaction.response.send_message("Slow down! Wait a few seconds.", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_translate(text, language)
    embed = discord.Embed(title=f"Translate to {language}", description=response, color=0xEB459E)
    embed.set_footer(text="AI Translator")
    await interaction.followup.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message):
        if not check_cooldown(message.author.id):
            await message.reply("Slow down! Wait a few seconds.", mention_author=False)
            return
        question = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        if question:
            async with message.channel.typing():
                response = get_ai_response(question)
            embed = discord.Embed(description=response, color=0x5865F2)
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            await message.reply(embed=embed, mention_author=False)
    await bot.process_commands(message)

bot.run(TOKEN)
