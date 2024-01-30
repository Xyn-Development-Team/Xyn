class module:
    name = "Music"
    cog_name = "music"
    description = "Lot's of music commands!"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"

import os

if __name__ == "__main__":
    # This is supposed to be imported by Xyn! You dummy!!!
    # We can't really localize this, since loading localization with this being directly executed would crash :c
    print("This is supposed to be imported by Xyn! You dummy!!!")
    os._exit(1)
else:
    import discord
    from discord import app_commands
    from discord.ext import commands
    import random
    import requests
    import storage
    from typing import Optional, Union, cast
    import localization
    import re
    import wavelink
    from dotenv import load_dotenv ; load_dotenv()
    from os import getenv

class music(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
            player: wavelink.Player | None = payload.player
            if not player:
                # Handle edge cases...
                return

            original: wavelink.Playable | None = payload.original
            track: wavelink.Playable = payload.track

            embed: discord.Embed = discord.Embed(title="Now Playing")
            embed.description = f"**{track.title}** by `{track.author}`"

            if track.artwork:
                embed.set_image(url=track.artwork)

            if original and original.recommended:
                embed.description += f"\n\n`This track was recommended via {track.source}`"

            if track.album.name:
                embed.add_field(name="Album", value=track.album.name)

            await player.home.send(embed=embed)

    #TODO: Use embeds with the song name, album art/thumbnail and artist name
    #/play
    @app_commands.command(name="play",description="Starts playing a song or adds it to the current queue!")
    async def play(self, interaction: discord.Interaction, query:str, vc: Optional[discord.VoiceChannel]):
        if not interaction.guild:
            return await interaction.response.send_message(str(localization.internal.read("guild_only")))
        
        await interaction.response.defer(thinking=True)

        player = wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)

        if vc:
            player = await vc.connect(cls=wavelink.Player)
        elif not player:
            if interaction.user.voice:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            else:
                return await interaction.followup.send(localization.external.read("no_voice"))

        player.autoplay = wavelink.AutoPlayMode.partial

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.followup.send(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.")
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await player.queue.put_wait(tracks)
            await interaction.followup.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.followup.send(f"Added **`{track}`** to the queue.")

        if not player.playing:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get(), volume=100)

async def setup(bot: commands.Bot) -> None:
    nodes = [wavelink.Node(uri=node, password=password) for node, password in zip(eval(getenv("lavalink_nodes")), eval(getenv("lavalink_passwords")))]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=100)
    
    print("music.py was loaded!")
    await bot.add_cog(music(bot))