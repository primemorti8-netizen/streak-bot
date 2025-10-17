import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv  # <--- добавили это

# Загружаем .env
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # важно! чтобы бот мог менять ники

bot = commands.Bot(command_prefix="!", intents=intents)

streaks = {}

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен и готов!")
    check_streaks.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    now = datetime.utcnow()

    if user_id not in streaks:
        streaks[user_id] = {"count": 1, "last_msg": now}
    else:
        last_msg = streaks[user_id]["last_msg"]

        if (now.date() - last_msg.date()).days == 1:
            streaks[user_id]["count"] += 1
            streaks[user_id]["last_msg"] = now
        elif (now.date() - last_msg.date()).days == 0:
            streaks[user_id]["last_msg"] = now
        elif (now.date() - last_msg.date()).days > 1:
            streaks[user_id] = {"count": 1, "last_msg": now}

    await update_nickname(message.author, message.guild)
    await bot.process_commands(message)

async def update_nickname(member, guild):
    try:
        count = streaks[member.id]["count"]
        base_name = member.name.split("🔥")[0].strip()
        new_nick = f"{base_name} 🔥{count}"
        await member.edit(nick=new_nick)
    except discord.Forbidden:
        print(f"❌ Нет прав менять ник для {member.name}")
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении ника: {e}")

@tasks.loop(hours=1)
async def check_streaks():
    now = datetime.utcnow()
    for user_id, data in list(streaks.items()):
        if (now - data["last_msg"]) > timedelta(days=1):
            streaks[user_id]["count"] = 0

if not token:
    print("❌ Токен не найден. Проверь .env файл!")
else:
    bot.run(token)
