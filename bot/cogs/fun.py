import random
import discord
from discord import app_commands
from discord.ext import commands

class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.eight_ball = [
            "It is certain.", "Without a doubt.", "You may rely on it.", "Ask again later.", "Cannot predict now.", "Don't count on it.", "My reply is no.", "Very doubtful."
        ]

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🎲 {result}")

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        answer = random.choice(self.eight_ball)
        await interaction.response.send_message(f"🎱 {answer}")

    @app_commands.command(name="rps", description="Play rock-paper-scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choice = choice.lower()
        options = ["rock", "paper", "scissors"]
        if choice not in options:
            await interaction.response.send_message("Choose rock, paper, or scissors.", ephemeral=True)
            return
        bot_choice = random.choice(options)
        outcome = "draw"
        if (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"):
            outcome = "win"
        elif choice == bot_choice:
            outcome = "draw"
        else:
            outcome = "lose"
        await interaction.response.send_message(f"You: {choice}\nBot: {bot_choice}\nResult: {outcome}")

async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
