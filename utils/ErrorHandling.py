import discord

class ErrorHandling:

    @staticmethod
    def is_not_none(variable_name, variable_value):
        if not variable_value:
            if variable_name == "guild_name":
                raise ValueError("Guild not found in the database")
            if variable_name == ("base_path" or "guild_database" or "backups_path"):
                raise ValueError("No such path exists")
            if variable_name == "database_path":
                raise ValueError("Folder does not exist")
            else:
                raise ValueError(f"{variable_name} is {variable_value}")
            
    @staticmethod
    async def confirm_view_handling(confirm_view_value, interaction: discord.Interaction):
        if confirm_view_value is False:
            await interaction.followup.send("Deletion cancelled.", ephemeral=True)
        else:
            await interaction.followup.send("Operation timed out.", ephemeral=True)
