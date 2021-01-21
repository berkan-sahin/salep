# Exchange rate functions
from operator import add
import doviz_api
# Discord API
import discord
from discord.ext import commands
# MongoDB
from pymongo import MongoClient
# Misc. imports  
from typing import Union
import logging
from random import choice

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

@salep.command()
async def döviz(ctx, currency: str):
    """Reports the current exchange rate between a user-specified currency and the Turkish Lira
    
    Args:
        ctx (discord.Context): Invocation context, provided by discord.py on function call
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
    return name if type(name) == str else name.id

@salep.command()
async def add_quote(ctx, name: Union[discord.Member, str], quote: str):
    """Adds a quote to the corresponding entry for the mentioned person and creates said entry
    if the person doesn't exist

    Args:
        ctx (discord.Context): Invocation context, passed by discord.py automatically
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
async def quote(ctx, name: Union[discord.Member, str]):
    """Picks and posts a quote belonging to the specific person and guild at random from the database

    Args:
        ctx (discord.Context): Invocation context, passed by discord.py automatically
        name (Union[discord.Member, str]): The name or mention of the person to pick a quote from
    """

    person = db.people.find_one({"name": extract_id(name), "guild": ctx.guild.id})
    if person is None:
        await ctx.send("This person does not exist")
        return

    await ctx.send(choice(person["quotes"]))

@salep.command()
async def capture_quote(ctx):
    """Captures the message that was replied to and stores it as a quote

    Args:
        ctx (discord.Context): Invocation context, passed automatically
    """

    target_msg = await ctx.fetch_message(ctx.message.reference.message_id)
    await add_quote(ctx, target_msg.author, target_msg.clean_content)

if __name__ == "__main__":
    logging.basicConfig(filename="salep.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    # Read exchange API key and bot token from the TOKEN file.
    with open("TOKEN", "r") as f:
        token = f.readline().strip()
        API_KEY = f.readline().strip()


    salep.run(token)


