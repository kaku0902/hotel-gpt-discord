import os
import discord
from openai import AsyncOpenAI

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

SYSTEM_PROMPT = """
You are a hotel operations AI assistant.

You help hotel owners and employees with:
- Hotel operations
- Guest communication
- Staff training
- Customer complaints
- Marketing ideas
- Korean, Vietnamese, and English translation
- Writing messages to hotel guests
- General hotel management questions

Answer in the same language as the user unless asked to translate.

Important:
If you do not know internal company information, hotel policy,
prices, employee information, reservations, or other private data,
do not invent it. Clearly say that the information needs to be
confirmed by hotel management.
"""


@bot.event
async def on_ready():
    print(f"GPT Hotel Agent connected as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith("!gpt"):
        return

    prompt = message.content[len("!gpt"):].strip()

    if not prompt:
        await message.channel.send(
            "질문을 입력해주세요. 예: `!gpt 고객에게 체크아웃 시간을 안내해줘`"
        )
        return

    try:
        async with message.channel.typing():
            response = await client.responses.create(
                model="gpt-4.1-mini",
                instructions=SYSTEM_PROMPT,
                input=prompt
            )

        answer = response.output_text

        # Discord has a message length limit.
        for i in range(0, len(answer), 1900):
            await message.channel.send(answer[i:i + 1900])

    except Exception as e:
        print(f"ERROR: {e}")
        await message.channel.send(
            "GPT 연결 중 오류가 발생했습니다. 관리자에게 확인해주세요."
        )


if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing.")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing.")

bot.run(DISCORD_TOKEN)
