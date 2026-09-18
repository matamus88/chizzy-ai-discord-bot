import os
import json
import time
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from ai_chat import get_ai_response, get_code_help, get_translate, get_summarize, get_premium_response

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SUPPORT_SERVER = os.getenv('SUPPORT_SERVER', '')
PREMIUM_PRICE = "$5/month"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

COOLDOWNS = {}
FREE_COOLDOWN = 5
PREMIUM_COOLDOWN = 1

PREMIUM_FILE = 'premium_servers.json'

def load_premium():
    try:
        with open(PREMIUM_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_premium(data):
    with open(PREMIUM_FILE, 'w') as f:
        json.dump(data, f)

def is_premium(server_id):
    premium = load_premium()
    return str(server_id) in premium

def check_cooldown(user_id, server_id):
    now = time.time()
    cooldown = PREMIUM_COOLDOWN if is_premium(server_id) else FREE_COOLDOWN
    if user_id in COOLDOWNS and now - COOLDOWNS[user_id] < cooldown:
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

@bot.tree.command(name="premium", description="Learn about Chizzy AI Premium")
async def premium_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⭐ Chizzy AI Premium",
        description=f"Upgrade your server for **{PREMIUM_PRICE}**!",
        color=0xFFD700
    )
    embed.add_field(name="🚀 Free Tier", value="• 5 second cooldown\n• Basic AI responses\n• Standard commands", inline=True)
    embed.add_field(name="⭐ Premium Tier", value="• 1 second cooldown\n• Better AI responses\n• Priority support\n• Premium badge", inline=True)
    embed.add_field(name="💳 How to Upgrade", value=f"DM the bot owner or join our support server!", inline=False)
    if SUPPORT_SERVER:
        embed.add_field(name="🔗 Support Server", value=f"[Join Here]({SUPPORT_SERVER})", inline=False)
    embed.set_footer(text="Premium payments via PayPal/CashApp")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="View bot statistics")
async def stats_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Chizzy AI Stats", color=0x5865F2)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
    premium_count = len(load_premium())
    embed.add_field(name="Premium Servers", value=str(premium_count), inline=True)
    embed.set_footer(text="Chizzy AI - Free AI for Discord")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ask", description="Ask the AI anything")
@app_commands.describe(question="Your question")
async def ask_slash(interaction: discord.Interaction, question: str):
    if not check_cooldown(interaction.user.id, interaction.guild_id):
        cooldown = "1 second" if is_premium(interaction.guild_id) else "5 seconds"
        await interaction.response.send_message(f"Slow down! Premium gets {cooldown} cooldown.", ephemeral=True)
        return
    await interaction.response.defer()
    if is_premium(interaction.guild_id):
        response = get_premium_response(question)
    else:
        response = get_ai_response(question)
    embed = discord.Embed(description=response, color=0xFFD700 if is_premium(interaction.guild_id) else 0x5865F2)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    tier = "⭐ Premium" if is_premium(interaction.guild_id) else "Free"
    embed.set_footer(text=f"Chizzy AI | {tier}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="code", description="Get help with coding")
@app_commands.describe(code="Your code or question about code")
async def code_slash(interaction: discord.Interaction, code: str):
    if not check_cooldown(interaction.user.id, interaction.guild_id):
        await interaction.response.send_message("Slow down!", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_code_help(code)
    embed = discord.Embed(title="Code Helper", description=response, color=0x57F287)
    tier = "⭐ Premium" if is_premium(interaction.guild_id) else "Free"
    embed.set_footer(text=f"Chizzy AI | {tier}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="summarize", description="Summarize text")
@app_commands.describe(text="Text to summarize")
async def summarize_slash(interaction: discord.Interaction, text: str):
    if not check_cooldown(interaction.user.id, interaction.guild_id):
        await interaction.response.send_message("Slow down!", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_summarize(text)
    embed = discord.Embed(title="Summary", description=response, color=0xFEE75C)
    tier = "⭐ Premium" if is_premium(interaction.guild_id) else "Free"
    embed.set_footer(text=f"Chizzy AI | {tier}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="translate", description="Translate text to another language")
@app_commands.describe(text="Text to translate", language="Target language")
async def translate_slash(interaction: discord.Interaction, text: str, language: str):
    if not check_cooldown(interaction.user.id, interaction.guild_id):
        await interaction.response.send_message("Slow down!", ephemeral=True)
        return
    await interaction.response.defer()
    response = get_translate(text, language)
    embed = discord.Embed(title=f"Translate to {language}", description=response, color=0xEB459E)
    tier = "⭐ Premium" if is_premium(interaction.guild_id) else "Free"
    embed.set_footer(text=f"Chizzy AI | {tier}")
    await interaction.followup.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message):
        if not check_cooldown(message.author.id, message.guild.id if message.guild else 0):
            await message.reply("Slow down! Upgrade to Premium for faster responses.", mention_author=False)
            return
        question = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        if question:
            async with message.channel.typing():
                if message.guild and is_premium(message.guild.id):
                    response = get_premium_response(question)
                else:
                    response = get_ai_response(question)
            embed = discord.Embed(description=response, color=0xFFD700 if (message.guild and is_premium(message.guild.id)) else 0x5865F2)
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            await message.reply(embed=embed, mention_author=False)
    await bot.process_commands(message)

bot.run(TOKEN)
