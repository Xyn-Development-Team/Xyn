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
    from typing import Optional, Union, cast, Literal
    import localization
    import re
    import wavelink
    from dotenv import load_dotenv ; load_dotenv()
    from os import getenv
    import imagetools

class music(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        self.queues = {}
        self.queue_positions = {}
        self.queue_modes = {}

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:

        player: wavelink.Player | None = payload.player
        if not player:
            return

        queue = self.queues[player.guild.id]
        self.queue_modes[player.guild.id]

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track
        
        language = storage.guild.read(player.guild.id, "language")

        # Replaced / Finished / Stopped
        if payload.reason == "stopped":
            return
        
        elif payload.reason == "finished":
            last_position = self.queue_positions[player.guild.id]

            if self.queue_modes[player.guild.id] == "loop":
                return await player.play(queue[self.queue_positions[player.guild.id]])
            else:
                if int(self.queue_positions[player.guild.id])+1 >= len(queue):
                    self.queue_positions[player.guild.id] = 0
                    if self.queue_modes[player.guild.id] == "normal":
                        embed = discord.Embed(title=localization.external.read("queue_end_title", language), description=localization.external.read("queue_end_description", language), color=discord.Color.from_str(imagetools.get_average_color(track.artwork)) if track.artwork else discord.Color.random())
                        await player.home.send(embed=embed)
                        return await player.play(queue[self.queue_positions[player.guild.id]], paused=True)
                    else:
                        return await player.play(queue[self.queue_positions[player.guild.id]])
                else:
                    self.queue_positions[player.guild.id] += 1
                await player.play(queue[self.queue_positions[player.guild.id]])
        
        elif payload.reason == "replaced":
            return

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
            player: wavelink.Player | None = payload.player
            if not player:
                # Handle edge cases...
                return
            
            original: wavelink.Playable | None = payload.original
            track: wavelink.Playable = payload.track

            language = storage.guild.read(player.guild.id, "language")

            embed: discord.Embed = discord.Embed(title=track.title, url=track.uri, color=discord.Color.from_str(imagetools.get_average_color(track.artwork)) if track.artwork else discord.Color.random()).set_author(name=localization.external.read("now_playing", language))
            if track.artist.url:
                embed.description = f"[{track.author}]({track.artist.url})"
            else:
                embed.description = f"{track.author}"

            if track.artwork:
                embed.set_image(url=track.artwork)

            if original and original.recommended:
                embed.description += f"\n\n`This track was recommended via {track.source}`"

            if track.album.name:
                embed.add_field(name=localization.external.read("album", language), value=track.album.name)

            await player.home.send(embed=embed)

    #/stealth_skip
    @app_commands.command(name="stealth_skip", description="(Debugging) Skips to the next song without replacing!")
    async def stealth_skip(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        await player.seek(player.current.length)
        await interaction.response.send_message("skipped uwu")

    #/skip
    @app_commands.command(name="skip",description="Skips to the next song!")
    async def skip(self, interaction:discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
        else:
            language = storage.guild.read(interaction.guild.id, "language")

        if not interaction.guild.id in self.queues:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))

        queue = self.queues[interaction.guild.id]
        self.queue_positions[interaction.guild.id]

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        language = storage.guild.read(interaction.guild.id, "language")
        previous_song = player.current

        if self.queue_positions[interaction.guild.id] + 1 >= len(queue):
            self.queue_positions[interaction.guild.id] = 0
        else:
            self.queue_positions[interaction.guild.id] += 1
        await player.play(queue[self.queue_positions[interaction.guild.id]])

        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title, description=f"[{player.current.author}]({player.current.artist.url})\nSkipped:[{previous_song.title}]({previous_song.uri})", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random())
        else:
            embed = discord.Embed(title=player.current.title, description=f"{player.current.author}\nSkipped:[{previous_song.title}]({previous_song.uri})", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random())
        if player.current.artwork:
            embed.set_thumbnail(url=player.current.artwork)
        embed.set_author(name=localization.external.read("now_playing", language))

        await interaction.response.send_message(embed=embed)

    #/now_playing
    @app_commands.command(name="now_playing",description="Take a peek at what's playing right now")
    async def now_playing(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
        language = storage.guild.read(interaction.guild.id, "language")
        
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", storage.guild.read(interaction.guild_id,"language")))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", storage.guild.read(interaction.guild_id,"language")))
        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title, description=f"[{player.current.author}]({player.current.artist.url})", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork).set_author(name=localization.external.read("now_playing", language))
        else:
            embed = discord.Embed(title=player.current.title, description=f"{player.current.author}", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork).set_author(name=localization.external.read("now_playing", language))
        
        await interaction.response.send_message(embed=embed)

    #/volume
    @app_commands.command(name="volume",description="Changes the volume of the current playback")
    @app_commands.describe(volume="From [1% to 1000%]")
    async def volume(self, interaction:discord.Interaction, volume:app_commands.Range[int,1,1000]):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
        language = storage.guild.read(interaction.guild.id, "language")
        
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", language))
        await player.set_volume(volume)
        
        embed = discord.Embed(title=player.current.title, url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_author(name=localization.external.read("now_playing", language)).set_thumbnail(url=player.current.artwork)
        
        if player.current.artist.url:
            embed.description = f"[{player.current.author}]({player.current.artist.url})\nVolume was set to {volume}%"
        else:
            embed.description = f"{player.current.author}\n{str(localization.external.read('volume_set', language)).format(volume=volume)}"

        await interaction.response.send_message(embed=embed)

    #/pause
    @app_commands.command(name="pause",description="Pauses the current song!")
    async def pause(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
        language = storage.guild.read(interaction.guild.id, "language")
        
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", language))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", language))      

        await player.pause(True)
        if player.current.artist.url:
            embed = discord.Embed(title=player.current.title, description=f"[{player.current.author}]({player.current.artist.url})\nwas **paused!**", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork)
        else:
            embed = discord.Embed(title=player.current.title, description=f"{player.current.author}\nwas **paused!**", url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork)
        await interaction.response.send_message(embed=embed)

    #/resume
    @app_commands.command(name="resume",description="Resumes playing the current song!")
    async def resume(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        language = storage.guild.read(interaction.guild.id, "language")
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", language))
        elif not player.playing:
            return await interaction.response.send_message(localization.external.read("nothing_playing", language))      

        await player.pause(False)
        embed = discord.Embed(title=player.current.title, description=str(localization.external.read("resumed", language)).format(author=player.current.author), url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork)
        await interaction.response.send_message(embed=embed)

    #/loop
    @app_commands.command(name="loop", description="Loops through the queue in different manners!")
    async def loop(self, interaction: discord.Interaction, mode:Literal["Song", "Queue", "Disabled"]):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        language = storage.guild.read(interaction.guild.id, "language")
        
        self.queue_modes[player.guild.id] = self.queue_modes[interaction.guild.id]

        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", language))

        if mode == "Song":
            self.queue_modes[player.guild.id] = "loop"
            return await interaction.response.send_message(localization.external.read("loop", language))
        elif mode == "Queue":
            self.queue_modes[player.guild.id] = "loop_all"
            return await interaction.response.send_message(localization.external.read("loop_all", language))
        elif mode == "Disabled":
            self.queue_modes[player.guild.id] = "normal"
            return await interaction.response.send_message(localization.external.read("loop_disabled", language))

    #/play
    @app_commands.command(name="play",description="Starts playing a song or adds it to the current queue!")
    @app_commands.describe(query="A YouTube or Spotify URL or search term!", vc="A voice chat fot that bot to connect, instead of your current one")
    async def play(self, interaction: discord.Interaction, query:Optional[str], file:Optional[discord.Attachment], vc:Optional[discord.VoiceChannel]):

        if not interaction.guild:
            return await interaction.response.send_message(str(localization.internal.read("guild_only", str(interaction.locale).lower())))
        
        language = storage.guild.read(interaction.guild.id, "language")

        if not query and not file:
            return await interaction.response.send_message(localization.external.read("no_source", language))

        if file:
            supported_extensions = ['mp3', 'wav', 'ogg', 'flac', 'webm', 'mka', 'aac', 'aiff', 'mid', 'midi', 'wma']
            file_extension = file.filename.lower().split('.')[-1]  # Get the extension from the filename
            
            if file_extension not in supported_extensions:
                return await interaction.response.send_message(localization.external.read("unknown_format", language))
            query = file.url

        await interaction.response.defer(thinking=True)
        
        if interaction.guild.id not in self.queues:
            self.queues[interaction.guild.id] = []
        if interaction.guild.id not in self.queue_positions:
            self.queue_positions[interaction.guild.id] = 0
        if interaction.guild.id not in self.queue_modes:
            self.queue_modes[interaction.guild.id] = "normal"

        player = wavelink.Player
        player = cast(wavelink.Player, interaction.guild.voice_client)

        if vc:
            player = await vc.connect(cls=wavelink.Player)
        elif not player:
            if interaction.user.voice:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            else:
                return await interaction.followup.send(localization.external.read("no_voice_play", language))

        player.autoplay = wavelink.AutoPlayMode.disabled # We're implementing our own solution
        player.home = interaction.channel

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.followup.send(localization.external.read("not_found", language))
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added = 0
            for track in tracks:
                added += 1
                self.queues[interaction.guild.id].append(track)
            #added: int = await player.queue.put_wait(tracks)
            embed = discord.Embed(title=tracks.name, url=tracks.url, description=tracks.author, color=discord.Color.from_str(imagetools.get_average_color(tracks.artwork)) if tracks.artwork else discord.Color.random()).set_author(name=str(localization.external.read("queued_playlist", language)).format(added=added)).set_thumbnail(url=tracks.artwork)
            await interaction.followup.send(embed=embed)
        elif isinstance(tracks, wavelink.Album):
            added = 0
            for track in tracks:
                added += 1
                self.queues[interaction.guild.id].append(track)
            embed = discord.Embed(title=tracks.name, url=tracks.url, description=tracks.author, color=discord.Color.from_str(imagetools.get_average_color(tracks.artwork)) if tracks.artwork else discord.Color.random()).set_author(name=f"Queued {added} songs from the album:").set_thumbnail(url=tracks.artwork)
            await interaction.followup.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            self.queues[interaction.guild.id].append(track)
            #await player.queue.put_wait(track)
            if track.artist.url:
                embed = discord.Embed(title=track.title, url=track.uri, description=f"[{track.author}]({track.artist.url})", color=discord.Color.from_str(imagetools.get_average_color(track.artwork)) if track.artwork else discord.Color.random()).set_author(name="Added to the queue:").set_thumbnail(url=track.artwork)
            else:
                embed = discord.Embed(title=track.title, url=track.uri, description=f"{track.author}", color=discord.Color.from_str(imagetools.get_average_color(track.artwork)) if track.artwork else discord.Color.random()).set_author(name="Added to the queue:").set_thumbnail(url=track.artwork)
            await interaction.followup.send(embed=embed)

        if not player.playing:
            # Play now since we aren't playing anything...
            return await player.play(self.queues[interaction.guild.id][0], volume=100)

    #/queue
    @app_commands.command(name="queue",description="| Music | Shows all the songs in the current queue")
    async def queue(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only",storage.guild.read(interaction.guild_id,"language")))
        else:
            language = storage.guild.read(interaction.guild.id, "language")
            player = wavelink.Player
            player = cast(wavelink.Player, interaction.guild.voice_client)

        if interaction.guild.id in self.queues:
            queue = self.queues[interaction.guild.id]
        else:
            emb = discord.Embed(title=localization.external.read("nothing_playing", language),description=localization.external.read("nothing_playing_tease", storage.guild.read(interaction.guild.id,"language")))
            return await interaction.response.send_message(embed=emb)

        embed=discord.Embed(title=player.current.title, url=player.current.uri, color=discord.Color.from_str(imagetools.get_average_color(player.current.artwork)) if player.current.artwork else discord.Color.random()).set_thumbnail(url=player.current.artwork)
        embed.set_author(name=localization.external.read("now_playing", language))
        embed.description = f"[{player.current.author}]({player.current.artist.url})\n" if player.current.artist.url else player.current.author + "\n\n**Queue:**"

        total_chars = 0
        item_chars = 0
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
            
        await interaction.response.send_message(embed=embed)

    #/stop
    @app_commands.command(name="stop",description="Stops playing the queue and disconnects from the voice channel")
    async def stop(self, interaction:discord.Interaction):
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        
        if not interaction.guild:
            return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
        language = storage.guild.read(interaction.guild.id, "language")
        
        if not player:
            return await interaction.response.send_message(localization.external.read("not_connected", language))
        
        await player.disconnect()
        player.cleanup()
        
        del self.queues[interaction.guild.id]
        del self.queue_modes[interaction.guild.id]
        del self.queue_positions[interaction.guild.id]
        await interaction.response.send_message(localization.external.read("playback_stopped", language))

async def setup(bot: commands.Bot) -> None:
    nodes = [wavelink.Node(uri=node, password=password) for node, password in zip(eval(getenv("lavalink_nodes")), eval(getenv("lavalink_passwords")))]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=None)
    
    print("music.py was loaded!")
    await bot.add_cog(music(bot))