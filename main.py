import discord
from discord.ext import commands
from keep_alive import keep_alive
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

OWNER_ID = 583975354826489866 # замени на свой Discord user ID (int)
LEVEL_CHANNEL_ID = 1371182706573967500  # канал для уведомлений о левелапах

# XP система
if os.path.exists("xp.json"):
    with open("xp.json", "r") as f:
        xp_data = json.load(f)
else:
    xp_data = {}

def save_xp():
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
                f"🎉 Добро пожаловать на наш сервер! Мы рады, что ты к нам присоединился.\n"
                f"📌 Обязательно загляни в канал с правилами, чтобы не пропустить важные моменты.\n"
                f"🧩 Выбирай роли, интересы и знакомься с комьюнити в спец. каналах.\n"
                f"💬 Не стесняйся писать в общий чат — у нас дружелюбная атмосфера!\n"
                f"❓ Вопросы? Обращайся к модераторам или администрации.\n\n"
                f"✨ Приятного времяпрепровождения!"
            ),
            color=0x000000
        )
        await channel.send(embed=embed)

    role = discord.utils.get(member.guild.roles, name="Подписчик")
    if role:
        await member.add_roles(role)

@bot.event
async def on_message(message):
    try:
    if message.author.bot:
        return

    user_id = str(message.author.id)
    xp_data.setdefault(user_id, 0)
    xp_data[user_id] += 3
    level_before = get_level(xp_data[user_id] - 10)
    level_after = get_level(xp_data[user_id])

    if level_after > level_before:
        level_channel = bot.get_channel(LEVEL_CHANNEL_ID)
        if level_channel:
            await level_channel.send(f"🎉 {message.author.mention}, ты достиг {level_after} уровня!")

        guild = message.guild
        role_map = {
            5: "Среднячёк",
            10: "Крутой 😎",
            15: "Звезда 🌟",
            20: "Олд"
        }

        if level_after in role_map:
            role_name = role_map[level_after]
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await message.author.add_roles(role)
                if level_channel:
                    await level_channel.send(f"🔰 {message.author.mention}, тебе выдана роль **{role.name}**!")

    save_xp()
    await bot.process_commands(message)

@bot.command()
async def ранг(ctx):
    user_id = str(ctx.author.id)
    xp = xp_data.get(user_id, 0)
    level = get_level(xp)
    await ctx.send(f"📊 {ctx.author.mention}, твой уровень: {level} | XP: {xp}")

@bot.command()
async def топ(ctx):
    if not xp_data:
        await ctx.send("🔍 Нет данных о пользователях.")
        return

    sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)
    top5 = sorted_users[:5]

    msg = "🏆 **Топ 5 по уровню:**\n"
    for i, (user_id, xp) in enumerate(top5, start=1):
        user = await bot.fetch_user(int(user_id))
        level = get_level(xp)
        msg += f"{i}. {user.name} — Уровень {level} | XP {xp}\n"

    await ctx.send(msg)

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
