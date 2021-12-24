import discord


# original code from https://github.com/Sly0511/TroveBot/blob/master/utils/buttons.py#L72
class Traceback(discord.ui.View):
    def __init__(self, ctx, exception, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.exception = exception

    @discord.ui.button(label="Show traceback", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def show(self, button: discord.ui.Button, interaction: discord.Interaction):
        if len(self.exception) > 2000:
            await interaction.response.send_message(f"```py\n{self.exception[:1990]}```", ephemeral=True)
            await interaction.response.send_message(f"```py\n{self.exception[1990:3980]}```", ephemeral=True)
        else:
            await interaction.response.send_message(f"```py\n{self.exception}```", ephemeral=True)
