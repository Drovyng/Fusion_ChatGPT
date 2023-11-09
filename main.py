import g4f


# def get_gpt_response(messages: list[dict[str, str]]) -> str | None:
#     try:
#         return g4f.ChatCompletion.create(
#             model=g4f.models.gpt_35_turbo,
#             messages=messages
#         )
#     except Exception as reason:
#         print(reason)
#         return None
async def get_response(messages: list[dict[str, str]]) -> str | None:
    try:
        return await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "system", "content": "Ты работаешь как очень полезная и умная нейросеть, по умолчанию говоришь на русском, но можешь работать и на других языках."}] + messages[:]
        )
    except Exception as exceprion:
        print(exceprion)
        if "RetryProvider" in exceprion:
            return "Произошла ошибка на сервере"
        return None

import discord, config, json, os, asyncio, threading
from discord.ext import commands
from discord.ext.commands.context import Context, Message
bot = commands.Bot(help_command=None, command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Бот готов!")


async def handle_message(msg: Message):
    history = []
    if os.path.exists("history.json"):
        with open("history.json", "r") as file:
            history = json.load(file)
    history.append({"role": "user", "content": msg.content})
    response = await get_response(history)

    if not response is None and response != "":
        history.append({"role": "assistant", "content": response})

        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        previous_msg = msg

        for chunk in chunks:
            previous_msg = await previous_msg.reply(content=chunk, mention_author=False)
    else:
        await msg.reply(content="Извините, произошла ошибка!", mention_author=False)
        history.remove(history[-1])

    if len(history) > 20:
        history.pop(0)

    with open("history.json", "w+") as file:
        json.dump(history, file)


@bot.event
async def on_message(msg: Message):
    if msg.channel.id == config.CHANNEL_ID and msg.author.id != bot.user.id:
        if msg.content == "Очистить историю":
            if msg.author.id == config.AUTHOR_ID:
                os.remove("history.json")
                await msg.channel.purge(limit=10000)
        else:
            async with msg.channel.typing():
                await handle_message(msg)

bot.run(token=config.TOKEN)