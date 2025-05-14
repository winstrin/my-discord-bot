import discord
from discord.ext import commands
from keep_alive import keep_alive
import json
import os
import asyncio

xp_lock = asyncio.Lock()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OWNER_ID = 583975354826489866  # замени на свой Discord user ID
LEVEL_CHANNEL_ID = 1371182706573967500  # канал для уведомлений о левелапах

# Загрузка XP
if os.path.exists("xp.json"):
    with open("xp.json", "r") as f:
        xp_data = json.load(f)
else:
    xp_data = {}

async def save_xp():
    async with xp_lock:
        with open("xp.json", "w") as f:
            json.dump(xp_data, f)

def get_level(xp):
    return int(xp ** 0.5)

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1371174377395327086)
    if channel:
        embed = discord.Embed(
            description=(
                f"👋 Привет, {member.mention}!\n\n"
                f"🎉 Добро пожаловать на наш сервер! Мы рады, что ты с нами.\n"
                f"📌 Загляни в канал с правилами, выбери роли, и не стесняйся общаться!"
            ),
            color=0x000000
        )
        await channel.send(embed=embed)

    role = discord.utils.get(member.guild.roles, name="Подписчик")
    if role:
        await member.add_roles(role)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)  # Обработка команд

    # XP только для обычных сообщений
    if message.content.startswith(bot.command_prefix):
        return

    user_id = str(message.author.id)
    xp_data.setdefault(user_id, 0)
    xp_data[user_id] += 3

    level_before = get_level(xp_data[user_id] - 3)
    level_after = get_level(xp_data[user_id])

    if level_after > level_before:
        xp_data.setdefault("last_level", {})
        last = xp_data["last_level"].get(user_id)

        if last == level_after:
            return  # уже отмечали этот уровень

        xp_data["last_level"][user_id] = level_after

        level_channel = bot.get_channel(LEVEL_CHANNEL_ID)
        if level_channel:
            await level_channel.send(f"🎉 {message.author.mention}, ты достиг {level_after} уровня!")

        # Выдача роли за уровень
        role_map = {
            5: "Среднячёк",
            10: "Крутой 😎",
            15: "Звезда 🌟",
            20: "Олд"
        }

        if level_after in role_map:
            role_name = role_map[level_after]
            role = discord.utils.get(message.guild.roles, name=role_name)
            if role:
                await message.author.add_roles(role)
                if level_channel:
                    await level_channel.send(f"🔰 {message.author.mention}, тебе выдана роль **{role.name}**!")

    await save_xp()

@bot.command()
async def ранг(ctx):
    user_id = str(ctx.author.id)
    xp = xp_data.get(user_id, 0)
    level = get_level(xp)

    embed = discord.Embed(
        title="📈 Твой ранг",
        description=f"**Уровень:** {level}\n**Опыт:** {xp}",
        color=discord.Color.purple()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command()
async def топ(ctx):
    filtered_data = {k: v for k, v in xp_data.items() if k != "last_level"}

    if not filtered_data:
        await ctx.send("🔍 Нет данных о пользователях.")
        return

    sorted_users = sorted(filtered_data.items(), key=lambda x: x[1], reverse=True)
    top5 = sorted_users[:5]

    embed = discord.Embed(
        title="🏆 Топ 5 по уровню",
        color=discord.Color.gold()
    )

    for i, (user_id, xp) in enumerate(top5, start=1):
        user = await bot.fetch_user(int(user_id))
        level = get_level(xp)
        embed.add_field(name=f"{i}. {user.name}", value=f"Уровень {level} | XP {xp}", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="сказать")
async def сказать(ctx, *, message: str):
    if ctx.author.id == OWNER_ID:
        embed = discord.Embed(description=message, color=0x000000)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ У тебя нет прав использовать эту команду.")

keep_alive()
bot.run(os.environ['TOKEN'])
