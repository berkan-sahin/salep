# Salep

This is a Discord bot with no specific purpose. Right now it can report various exchange rates for Turkish Lira (TRY). More features will be added down the line.

## Setup

```bash
git clone https://github.com/berkan-sahin/salep.git # Clone the repository
cd salep
python3 -m venv .venv # Create virtual env
source .venv/bin/activate # Switch into virtual env
python3 -m pip install discord.py requests # Install dependencies
echo "YOUR-DISCORD-TOKEN-HERE" > TOKEN # Token file stores private info
echo "YOUR-CURRENCY-API-KEY-HERE" >> TOKEN # *MAKE SURE TO ADD IT IN .gitignore in order to avoid bot abuse*
python3 salep.py # Test the bot, when you are done hit Ctrl-C
```

For subsequent runs, you can run the `launch.sh` from inside the project root
