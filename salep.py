# Exchange rate functions
import doviz_api
# Discord API
import discord
from discord.ext import commands, tasks
# MongoDB
from pymongo import MongoClient
# for DGKO
from datetime import date
# Misc. imports  
from typing import Union, Optional
import logging
from random import choice
import os

# This is the API key for the exchange rate service
# It will be read from the TOKEN file
API_KEY = ""

salep = commands.Bot(command_prefix="s!")

# Initialize database
client = MongoClient()
db = client.salep


@salep.event
async def on_ready():
    logging.info('Logged in as')
    logging.info(salep.user.name)
    logging.info(salep.user.id)
    logging.info('------')

    # Add presence
    webpage = discord.Game("https://bsahin.xyz/proj/salep/")
    await salep.change_presence(activity=webpage)
    query_bday.start()

@salep.command()
async def döviz(ctx: commands.Context, currency: str):
    """Reports the current exchange rate between a user-specified currency and the Turkish Lira
    
    Args:
        ctx (commands.Context): Invocation context, provided by discord.py on function call
        currency (str): The name or the three-letter code for the desired currency
    """    

    try:
        exchange_rate, currency_abbr = doviz_api.get_exchange_rate(currency, API_KEY)
    except doviz_api.InvalidCurrencyError:
        await ctx.send(f"{currency} diye bir kur yok!")
        return
    
    await ctx.send(f"1 {currency_abbr} = {exchange_rate} {doviz_api.base_currency}")

def extract_id(name: Union[discord.Member, str]):
    """
    A helper function for storing and querying Members in the database
    """
    return name.lower() if type(name) == str else name.id

@salep.command()
async def add_quote(ctx: commands.Context, name: Union[discord.Member, str], *, quote: str):
    """Adds a quote to the corresponding entry for the mentioned person and creates said entry
    if the person doesn't exist

    Args:
        ctx (commands.Context): Invocation context, passed by discord.py automatically
        name (Union[discord.Member, str]): The name or mention of the person the quote belongs to
        quote (str): The quote to add
    """

    if db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id}) is None:
        person = {
            "name": extract_id(name),
            "guild": ctx.guild.id,
            "quotes": [quote]
        }

        db.people.insert_one(person)
        await ctx.send("Created stack for {0} and added quote".format(name if type(name) == str else name.mention))
        return

    db.people.update_one({"name": extract_id(name), "guild": ctx.guild.id}, {"$addToSet": {"quotes": quote}})
    await ctx.send("Added quote to stack")

@salep.command()
async def quote(ctx: commands.Context, name: Union[discord.Member, str]):
    """Picks and posts a quote belonging to the specific person and guild at random from the database

    Args:
        ctx (commands.Context): Invocation context, passed by discord.py automatically
        name (Union[discord.Member, str]): The name or mention of the person to pick a quote from
    """

    person = db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id})
    if person is None:
        await ctx.send("This person does not exist")
        return

    await ctx.send(choice(person["quotes"]))

@salep.command()
async def capture_quote(ctx: commands.Context):
    """Captures the message that was replied to and stores it as a quote

    Args:
        ctx (commands.Context): Invocation context, passed automatically
    """

    target_msg = await ctx.fetch_message(ctx.message.reference.message_id)
    await add_quote(ctx, target_msg.author, target_msg.clean_content)

@salep.command()
@commands.has_permissions(manage_messages=True)
async def rm_quote(ctx: commands.Context, name: Union[discord.Member, str], *, query: str):
    """Remove any quote containing the specified word(s)

    Args:
        ctx (commands.Context): Invocation context, passed automatically
        name (Union[discord.Member, str]): Name or mention of the person the quote belongs to
        query (str): The word(s) to look for
    """

    person = db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id})
    if person is None:
        await ctx.send("This person does not exist!")
        return
    
    rm_count = 0
    for quote in person["quotes"]:
        if query in quote:
            person["quotes"].remove(quote)
            rm_count += 1
    
    db.people.replace_one({"name": extract_id(name), "guild": ctx.guild.id}, person)
    await ctx.send("Removed {0} entries from {1}".format(rm_count, name if type(name) == str else name.mention))

@tasks.loop(hours=24)
async def query_bday():
    for guild in salep.guilds:
        for bday_child in db.people.find({"guild": guild.id, "bday-month": date.today().month, "bday-day": date.today().day}):
            member: discord.Member = guild.get_member(bday_child["name"])
            guild.system_channel.send("Happy birthday {0}!".format(member.mention))

@salep.command()
async def dgko(ctx: commands.Context, bday: str):
    """Add your birthday

    Args:
        ctx (commands.Context): Invocation context, provided automatically
        bday (str): Your birthday, in dd/mm/yyyy format
    """
    tmp = bday.split("/")
    
    if db.people.find_one({"name": ctx.author.id, "guild": ctx.guild.id}) is None:
        person = {
            "name": ctx.author.id,
            "guild": ctx.guild.id,
            "bday-day" : int(tmp[0]),
            "bday-month" : int(tmp[1])
        }

        db.people.insert_one(person)
        await ctx.send("Created {0} and added birthday".format(ctx.author.mention))
        return

    db.people.update_one({"name": ctx.author.id, "guild": ctx.guild.id}, {"$set": {"bday-day": int(tmp[0]), "bday-month": int(tmp[1])}})
    await ctx.send("Added birthday")
    

if __name__ == "__main__":
    logging.basicConfig(filename="salep.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    # Read exchange API key and bot token from the TOKEN file.
    with open("TOKEN", "r") as f:
        token = f.readline().strip()
        API_KEY = f.readline().strip()

    # Write PID to file for easy killing
    with open(".pid", "w") as f:
        f.write(str(os.getpid()))

    logging.info("PID: {0}".format(os.getpid()))

    salep.run(token)


