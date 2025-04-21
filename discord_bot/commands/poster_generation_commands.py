from discord import Interaction

from discord_bot.bot import PropagandaBot
from discord_bot.content_generation.generate_poster import generate_and_post_poster


def register_poster_generation_commands(bot: PropagandaBot):
    @bot.tree.command(
        name="generate",
        description="Generate a propaganda poster immediately")
    async def generate(interaction: Interaction):
        await interaction.response.send_message(
            "A True Piece is in the Making... Smoke a true cigarette in the meanwhile 🚬.")
        await generate_and_post_poster(bot, interaction.channel)
