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

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        
        # Replaced / Finished / Stopped
        if payload.reason == "STOPPED":
            return
        elif payload.reason == "FINISHED":
            return
        elif payload.reason == "REPLACED":
            return

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
            player: wavelink.Player | None = payload.player
            if not player:
                # Handle edge cases...
                return
            
            original: wavelink.Playable | None = payload.original
            track: wavelink.Playable = payload.track

            embed: discord.Embed = discord.Embed(title=track.title,url=track.uri).set_author(name="Now playing:")
            if track.artist.url:
                embed.description = f"[{track.author}]({track.artist.url})"
            else:
                embed.description = f"{track.author}"

            if track.artwork:
                embed.set_image(url=track.artwork)

            if original and original.recommended:
                embed.description += f"\n\n`This track was recommended via {track.source}`"

            if track.album.name:
                embed.add_field(name="Album", value=track.album.name)

            await player.home.send(embed=embed)

    #/skip
    @app_commands.command(name="skip",description="Skips to the next song!")
    async def skip(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        previous_song = player.current
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))

        await player.skip(force=True)
        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title,description=f"[{player.current.author}]({player.current.artist.url})\nSkipped:[{previous_song.title}]({previous_song.uri})",url=player.current.uri)
        else:
            embed = discord.Embed(title=player.current.title,description=f"{player.current.author}\nSkipped:[{previous_song.title}]({previous_song.uri})",url=player.current.uri)
        embed.set_thumbnail(url=player.current.artwork)
        embed.set_author(name=f"Now playing:")

        await interaction.response.send_message(embed=embed)
        await interaction.response.send_message("OwO")

    #/now_playing
    @app_commands.command(name="now_playing",description="Take a peek at what's playing right now")
    async def now_playing(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", storage.guild.read(interaction.guild_id,"language")))
        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title,description=f"[{player.current.author}]({player.current.artist.url})",url=player.current.uri).set_thumbnail(url=player.current.artwork).set_author(name="Now playing:")
        else:
            embed = discord.Embed(title=player.current.title,description=f"{player.current.author}",url=player.current.uri).set_thumbnail(url=player.current.artwork).set_author(name="Now playing:")
        await interaction.response.send_message(embed=embed)

    #/volume
    @app_commands.command(name="volume",description="Changes the volume of the current playback")
    @app_commands.describe(volume="From [1% to 1000%]")
    async def volume(self, interaction:discord.Interaction, volume:app_commands.Range[int,1,1000]):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        await player.set_volume(volume)
        embed = discord.Embed(title=player.current.title,url=player.current.uri).set_author(name=localization.external.read("now_playing", storage.guild.read(interaction.guild.id,"language"))).set_thumbnail(url=player.current.artwork)
        if player.current.artist.url:
            embed.description = f"[{player.current.author}]({player.current.artist.url})\nVolume was set to {volume}%"
        else:
            embed.description = f"{player.current.author}\n{str(localization.external.read('volume_set',storage.guild.read(interaction.guild.id,'language'))).format(volume=volume)}"

        await interaction.response.send_message(embed=embed)

    #/pause
    @app_commands.command(name="pause",description="Pauses the current song!")
    async def pause(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", storage.guild.read(interaction.guild_id,"language")))      

        await player.pause(True)
        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title,description=f"[{player.current.author}]({player.current.artist.url})\nwas **paused!**",url=player.current.uri).set_thumbnail(url=player.current.artwork)
        else:
            embed = discord.Embed(title=player.current.title,description=f"{player.current.author}\nwas **paused!**",url=player.current.uri).set_thumbnail(url=player.current.artwork)
        await interaction.response.send_message(embed=embed)

    #/resume
    @app_commands.command(name="resume",description="Resumes playing the current song!")
    async def resume(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", storage.guild.read(interaction.guild_id,"language")))      

        await player.pause(False)
        embed = discord.Embed(title=player.current.title,description=str(localization.external.read("resumed",storage.guild.read(interaction.guild.id, "language"))).format(author=player.current.author),url=player.current.uri).set_thumbnail(url=player.current.artwork)
        await interaction.response.send_message(embed=embed)

    #/play
    @app_commands.command(name="play",description="Starts playing a song or adds it to the current queue!")
    @app_commands.describe(query="A YouTube or Spotify URL or search term!", vc="A voice chat fot that bot to connect, instead of your current one")
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
                return await interaction.followup.send(localization.external.read("no_voice_play",storage.guild.read(interaction.guild.id,"language")))

        player.autoplay = wavelink.AutoPlayMode.partial
        player.home = interaction.channel

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.followup.send(localization.external.read("not_found",storage.guild.read(interaction.guild.id, "language")))
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await player.queue.put_wait(tracks)
            embed = discord.Embed(title=tracks.name,url=tracks.url,description=tracks.author).set_author(name=f"Queued {added} songs from the playlist:").set_thumbnail(url=tracks.artwork)
            await interaction.followup.send(embed=embed)
            #await interaction.followup.send(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        elif isinstance(tracks, wavelink.Album):
            added: int = await player.queue.put_wait(tracks)
            embed = discord.Embed(title=tracks.name,url=tracks.url,description=tracks.author).set_author(name=f"Queued {added} songs from the album:").set_thumbnail(url=tracks.artwork)
            await interaction.followup.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            if track.artist.url:
                embed = discord.Embed(title=track.title,url=track.uri,description=f"[{track.author}]({track.artist.url})").set_author(name="Added to the queue:").set_thumbnail(url=track.artwork)
            else:
                embed = discord.Embed(title=track.title,url=track.uri,description=f"{track.author}").set_author(name="Added to the queue:").set_thumbnail(url=track.artwork)
            await interaction.followup.send(embed=embed)
            #await interaction.followup.send(f"Added **`{track}`** to the queue.")

        if not player.playing:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get(), volume=100)

    #/queue
    @app_commands.command(name="queue",description="| Music | Shows all the songs in the current queue")
    async def queue(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("only_guild",storage.guild.read(interaction.guild_id,"language")))
        if not interaction.guild.voice_client:
            return await interaction.response.send_message(localization.external.read("no_voice",storage.guild.read(interaction.guild_id,"language")),ephemeral=True)
        else:
            player = wavelink.Player
            player = cast(wavelink.Player, interaction.guild.voice_client)

            # A visual version of the queue, with the only real difference being that the current song is there!
            queue = [player.current]
            for song in player.queue:
                queue.append(song)

            embed=discord.Embed(title=player.current.title, url=player.current.uri).set_thumbnail(url=player.current.artwork)
            embed.set_author(name=localization.external.read("now_playing", storage.guild.read(interaction.guild.id,"language")))
            embed.description = f"[{player.current.author}]({player.current.artist.url})\n" if player.current.artist.url else player.current.author + "\n"

            total_chars = 0
            item_chars = 0
            music_list="\n"
            for i, item in enumerate(queue):
                if total_chars + item_chars > 4000:
                    embed.description+="..."
                    break
                else:
                    if item.title == player.current.title:
                        item_chars = len(f"\n **{i+1} - >> [{item.title}]({item.uri})**")
                        embed.description+= (f"\n **{i+1} - >> [{item.title}]({item.uri})**")
                    else:
                        item_chars = len(f"{i+1} - [{item.title}]({item.uri})")
                        embed.description+= (f"\n{i+1} - [{item.title}]({item.uri})")
                    total_chars += item_chars

            if player.queue:
                await interaction.response.send_message(embed=embed)
            else:
                emb = discord.Embed(title=localization.external.read("nothing_playing", storage.guild.read(interaction.guild.id,"language")),description=localization.external.read("nothing_playing_tease", storage.guild.read(interaction.guild.id,"language")))
                await interaction.response.send_message(embed=emb)

    #/stop
    @app_commands.command(name="stop",description="Stops playing the queue and disconnects from the voice channel")
    async def stop(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        
        await player.disconnect()
        await interaction.response.send_message(localization.external.read("playback_stopped",storage.guild.read(interaction.guild.id, "language")))

async def setup(bot: commands.Bot) -> None:
    nodes = [wavelink.Node(uri=node, password=password) for node, password in zip(eval(getenv("lavalink_nodes")), eval(getenv("lavalink_passwords")))]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=100)
    
    print("music.py was loaded!")
    await bot.add_cog(music(bot))