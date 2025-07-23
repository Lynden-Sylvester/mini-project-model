import discord
from discord.ui import View

class ConfirmView(View):
    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.interaction.user:
            await interaction.response.send_message('Confirmed', ephemeral=True)
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.interaction.user:
            await interaction.response.send_message('Cancelled', ephemeral=True)
            self.value = False
            self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.interaction.user
    
    async def on_timeout(self):
        await self.interaction.channel.send("Operation timed out.", ephemeral=True)

