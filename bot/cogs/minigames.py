import random
import discord
from discord import app_commands
from discord.ext import commands

class MinigamesCog(commands.Cog):
    """Small, stateless minigames: guess the number, scramble, trivia. State kept in-memory per bot process."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # games per channel
        self.guess_games = {}  # channel_id -> secret number
        self.trivia_questions = [
            {"q": "What is the capital of France?", "a": "Paris"},
            {"q": "Which planet is known as the Red Planet?", "a": "Mars"},
            {"q": "Who wrote 'Romeo and Juliet'?", "a": "William Shakespeare"},
            {"q": "What is 7 * 8?", "a": "56"},
            {"q": "In computing, what does CPU stand for?", "a": "Central Processing Unit"},
        ]

    @app_commands.command(name="guess_start", description="Start a 'guess the number' game in this channel")
    @app_commands.describe(max_number="Maximum number (default 100)")
    async def guess_start(self, interaction: discord.Interaction, max_number: int = 100):
        if max_number < 2 or max_number > 1000000:
            await interaction.response.send_message("Max must be between 2 and 1,000,000.", ephemeral=True)
            return
        secret = random.randint(1, max_number)
        self.guess_games[interaction.channel_id] = {"secret": secret, "max": max_number, "tries": 0}
        await interaction.response.send_message(f"🎯 Guess game started! I'm thinking of a number between 1 and {max_number}. Use `/guess_try number:...` to guess.")

    @app_commands.command(name="guess_try", description="Make a guess in the active 'guess the number' game")
    @app_commands.describe(number="Your guess")
    async def guess_try(self, interaction: discord.Interaction, number: int):
        state = self.guess_games.get(interaction.channel_id)
        if not state:
            await interaction.response.send_message("No active guess game in this channel. Start one with `/guess_start`.", ephemeral=True)
            return
        state["tries"] += 1
        secret = state["secret"]
        if number == secret:
            await interaction.response.send_message(f"🎉 Correct! {interaction.user.mention} guessed the number {secret} in {state['tries']} tries.")
            del self.guess_games[interaction.channel_id]
        elif number < secret:
            await interaction.response.send_message("🔼 Too low! Try again.", ephemeral=False)
        else:
            await interaction.response.send_message("🔽 Too high! Try again.", ephemeral=False)

    @app_commands.command(name="scramble", description="Scramble a word")
    @app_commands.describe(word="Word to scramble")
    async def scramble(self, interaction: discord.Interaction, word: str):
        chars = list(word)
        random.shuffle(chars)
        scrambled = ''.join(chars)
        await interaction.response.send_message(f"🧩 Scrambled: **{scrambled}**\nTry to guess the original word!")

    @app_commands.command(name="trivia", description="Answer a trivia question (answer revealed after 12s)")
    async def trivia(self, interaction: discord.Interaction):
        q = random.choice(self.trivia_questions)
        await interaction.response.send_message(f"❓ {q['q']}\nYou have 12 seconds to think... answer will be revealed soon.")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=12))
        # fallback to reveal
        await interaction.followup.send(f"✅ Answer: **{q['a']}**")

async def setup(bot: commands.Bot):
    await bot.add_cog(MinigamesCog(bot))
