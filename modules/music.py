import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
from typing import Literal
from typing import Optional
import wavelink
from wavelink.ext import spotify
import asyncio
import settings
from os import getenv
from dotenv import load_dotenv

load_dotenv()

import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
spotify_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=getenv("SPOTIPY_CLIENT_ID"),client_secret=getenv("SPOTIPY_CLIENT_SECRET")))

import pytube
from pytube import Playlist
#import linktools

sc = spotify.SpotifyClient(
    client_id=getenv("SPOTIPY_CLIENT_ID"),
    client_secret=getenv("SPOTIPY_CLIENT_SECRET")
)

class spotipy:
    async def get(type,query):
        if type == spotify.SpotifySearchType.track:
            track_name = spotify_client.track(query)["name"]
            artist = spotify_client.track(query)["artists"]
            artist = spotify_client.track(query)["artists"][0]["name"]
            query = f"{track_name} {artist}"
            return query
        if type != spotify.SpotifySearchType.track:
            sp_playlist = []
        if type == spotify.SpotifySearchType.album:
            tracks = spotify_client.album_tracks(query)["items"]
            for t in range(len(tracks)):
                track_name = tracks[t]["name"]
                artist = tracks[t]["artists"][0]["name"]
                query = f"{track_name} {artist}"
                sp_playlist.append(query)
            return sp_playlist
        elif type == spotify.SpotifySearchType.playlist:
            tracks = spotify_client.playlist_items(playlist_id=query,fields="items.track.name")["items"]
            artists = spotify_client.playlist_items(playlist_id=query,fields="items.track.artists.name")["items"]
            for t in range(len(tracks)):
                track_name = tracks[t]["track"]["name"]
                artist = artists[t]["track"]["artists"][0]["name"]
                query = f"{track_name} {artist}"
                sp_playlist.append(query)
            return sp_playlist
    
    async def list_name(type,query):
        if type == spotify.SpotifySearchType.album:
            return spotify_client.album(query)["name"]
        if type == spotify.SpotifySearchType.playlist:
            return spotify_client.playlist(query)["name"]

class music(commands.GroupCog, name="music"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload) -> None:
        if payload.player.current:
            global last_track ; last_track = payload.player.current

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload) -> None:
        #REPLACED FINISHED
        if payload.reason == "FINISHED":
            try:
                await payload.player.play(payload.player.queue[payload.player.queue.find_position(last_track)+1],replace=True)
            except:
                if payload.player.queue.loop:
                    await payload.player.play(payload.player.queue[payload.player.queue.find_position(last_track)],replace=True)
                else:
                    await payload.player.stop()


    #/resume
    @app_commands.command(name="resume",description="Resumes the song's playback")
    async def resume(self, interaction: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild_id)
        await player.resume()
        await interaction.response.send_message(embed=discord.Embed(title=f"**{player.current.title}**",url=player.current.uri).set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Resumed playing:"))


    #/pause
    @app_commands.command(name="pause",description="Pauses the song's playback")
    async def pause(self, interaction: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild_id)
        await player.pause()
        await interaction.response.send_message(embed=discord.Embed(title=f"**{player.current.title}**",url=player.current.uri).set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Paused playing:"))

    # #/loop
    # @app_commands.command(name="loop",description="Loops the current song!")
    # async def loop(self, interaction: discord.Interaction,type:Choice[Literal["Current","All"]]):
    #     node = wavelink.NodePool.get_node()
    #     player = node.get_player(interaction.guild_id)
    #     if await player.queue.loop() == False:
    #         if str(type).lower() == "current":
    #             await player.queue.loop(True)
    #             await interaction.response.send_message(embed=discord.Embed(title=f"**{player.current.title}**",url=player.current.uri).set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Now looping:"))
    #         elif str(type).lower() == "all":
    #             await player.queue.loop_all(True)
    #             await interaction.response.send_message(embed=discord.Embed(title=f"Looping the entire queue!").set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Now looping:"))
    #     if await player.queue.loop() == True:
    #         await player.queue.loop(False) ; await player.queue.loop_all(False)

    #/player
    @app_commands.command(name="player",description="| Music | Shows a pretty GUI player to control the current playback")
    async def player(self, interaction: discord.Interaction):
        #The constant defining of the node and player are in place to avoid any bugs when switching channels or similar situations
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild_id)

        global emb
        emb = discord.Embed(title=f"{player.current.title}",url=player.current.uri).set_author(name="Now playing:").set_thumbnail(url=pytube.YouTube(player.current.uri).thumbnail_url)

        class PlayerView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.timeout = None
                
                self.update_player.start()
                global song
                song = player.current
            
            @discord.ui.button(emoji="⏪",custom_id="player_rewind_button")
            async def rewind_callback(self, interaction:discord.Interaction, button:discord.Button):
                node = wavelink.NodePool.get_node()
                player = node.get_player(interaction.guild_id)
                next_song = player.current
                try:
                    await player.play(player.queue[player.queue.find_position(player.current)-1])
                except ValueError:
                    await interaction.channel.send("You're already playing the first song in the queue!")
                await interaction.response.edit_message(embed=discord.Embed(title=f"{player.current.title}",description=f"Rewinded from: [{next_song.title}]({next_song.uri})",url=player.current.uri).set_author(name="Now playing:").set_thumbnail(url=pytube.YouTube(player.current.uri).thumbnail_url),view=self)

            @discord.ui.button(emoji= "▶️" if player.is_paused() else "⏸️",style=discord.ButtonStyle.green if player.is_paused() else discord.ButtonStyle.secondary,custom_id="player_pause_button")
            async def play_callback(self, interaction:discord.Interaction, button:discord.Button):
                node = wavelink.NodePool.get_node()
                player = node.get_player(interaction.guild_id)
                global song
                global emb
                song = player.current
                if player.is_paused():
                    emb = discord.Embed(title=f"**{song.title}**",url=song.uri).set_thumbnail(url=str(pytube.YouTube(song.uri).thumbnail_url)).set_author(name="Now playing:")
                    await player.resume()
                    button.emoji = "⏸️"
                    button.style = discord.ButtonStyle.secondary
                    await interaction.response.edit_message(embed=emb,view=self)
                elif not player.is_paused():
                    emb = discord.Embed(title=f"**{song.title}**",url=song.uri).set_thumbnail(url=str(pytube.YouTube(song.uri).thumbnail_url)).set_author(name="Paused:")
                    await player.pause()
                    button.emoji = "▶️"
                    button.style = discord.ButtonStyle.green
                    await interaction.response.edit_message(embed=emb,view=self)


            @discord.ui.button(emoji="⏭️",custom_id="player_skip_button")
            async def skip_callback(self, interaction:discord.Interaction, button:discord.Button):
                global song
                global emb
                node = wavelink.NodePool.get_node()
                player = node.get_player(interaction.guild_id)
                previous_song = player.current
                try:
                    await player.play(player.queue[player.queue.find_position(player.current)+1],replace=True)
                except:
                    await player.play(player.queue[0],replace=True)
                emb = discord.Embed(title=f"**{player.current.title}**",description=f"[{previous_song.title}]({previous_song.uri}) was skipped!",url=player.current.uri).set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Now playing:")
                await interaction.response.edit_message(embed=emb)

            @discord.ui.button(emoji="⏹️",style=discord.ButtonStyle.danger,custom_id="player_stop_button")
            async def stop_callback(self, interaction:discord.Interaction, button:discord.Button):
                node = wavelink.NodePool.get_node()
                player = node.get_player(interaction.guild_id)    
                self.update_player.cancel()
                await player.disconnect()
                self.stop()
                await interaction.message.delete()

            @tasks.loop(seconds=1)
            async def update_player(self):
                global song
                try:
                    if song != player.current:
                        song = player.current
                        emb.title = f"{song.title}" ; emb.url = song.uri
                        emb.description = None
                        emb.set_thumbnail(url=pytube.YouTube(song.uri).thumbnail_url)
                        await discord.Message.edit(await interaction.original_response(),embed=emb,view=PlayerView())
                    else:
                        pass
                except NameError:
                    pass
        
        await interaction.response.send_message(embed=emb,view=PlayerView())

    #/play
    @app_commands.command(name="play",description="| Music | Searches/Plays a music URL from YouTube, YouTube Music, Spotify, SoundCloud")
    async def play(self, interaction: discord.Interaction, *, query: str):
        await interaction.response.defer(thinking=True)
        playlist = False
        spotify_query = False
        spotify_type = None
        try:
            if not interaction.guild.voice_client:
                vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            else:
                vc: wavelink.Player = interaction.guild.voice_client
        except:
            return await interaction.followup.send("I'm not connected to any voice channels ¯\_(ツ)_/¯")

        if any(["music.youtube.com/playlist" in query]):
            query = re.sub(re.escape("https://music.youtube.com"),"https://youtube.com",query)
            query = re.sub(re.escape("http://music.youtube.com"),"https://youtube.com",query)
            track = await wavelink.YouTubePlaylist.search(query)
            playlist = True
        elif any(["music.youtube.com" in query]):
            track = await wavelink.YouTubeMusicTrack.search(query,return_first=True)
        elif any(["playlist?list=" in query]):
            track = await wavelink.YouTubePlaylist.search(query)
            playlist = True
        elif any(["open.spotify.com" in query]):
            spotify_query = True
            decoded = spotify.decode_url(query)
            if decoded and decoded['type'] is spotify.SpotifySearchType.track:
                track = await spotify.SpotifyTrack.search(query=decoded["id"], type=decoded["type"])
                spotify_type = spotify.SpotifySearchType.track

            elif decoded and decoded['type'] is spotify.SpotifySearchType.playlist:
                playlist = True
                spotify_type = spotify.SpotifySearchType.playlist

            elif decoded and decoded['type'] is spotify.SpotifySearchType.album:
                playlist = True
                spotify_type = spotify.SpotifySearchType.album
        else:
            try:
                track = await wavelink.YouTubeTrack.search(query, return_first=True)
            except wavelink.NoTracksError:
                print(f"fuck {query}")

        vc.autoplay = False
        if vc.is_playing():
            counter = 0
            if spotify_query and playlist:
                for track in await spotipy.get(type=spotify_type,query=query):
                    try:
                        await vc.queue.put_wait(await wavelink.YouTubeTrack.search(track,return_first=True))
                        counter+=1
                    except wavelink.NoTracksError:
                        pass
                await interaction.followup.send(embed=discord.Embed(title=f"**{counter} Songs!**",description=f"From the Spotify playlist/album:[{await spotipy.list_name(spotify_type,query)}]({query})").set_author(name="Added to queue"))
            elif playlist and not spotify_query:
                counter = 0
                for track in track.tracks:
                    vc.queue.put(track)
                    counter+=1
                await interaction.followup.send(embed=discord.Embed(title=f"**{counter} songs!**",description=f"From the playlist/album: **[{Playlist(query).title}]({query})**").set_author(name="Added to queue:"))
            else:
                vc.queue.put(track)
                try:
                    await interaction.followup.send(embed=discord.Embed(title=f"**{track.title}**",url=track.uri).set_author(name="Added to queue").set_thumbnail(url=str(pytube.YouTube(track.uri).thumbnail_url)))
                except:
                    await interaction.followup.send(embed=discord.Embed(title=f"**{track.title}**",url=track.uri).set_author(name="Added to queue"))

        else:
            if spotify_query and playlist:
                counter = 0
                for track in await spotipy.get(type=spotify_type,query=query):
                    if counter < 1:
                        try:
                            await vc.queue.put_wait(await wavelink.YouTubeTrack.search(track,return_first=True))
                            await vc.play(vc.queue[0])
                            counter+=1
                        except wavelink.NoTracksError:
                            pass
                    else:
                        try:                
                            await vc.queue.put_wait(await wavelink.YouTubeTrack.search(track,return_first=True))
                            counter+=1
                        except wavelink.NoTracksError:
                            pass
                try:
                    await interaction.followup.send(embed=discord.Embed(title=f"**{vc.current.title}**",description=f"From the Spotify playlist/album: [{await spotipy.list_name(spotify_type,query)}]({query})",url=vc.current.uri).set_author(name="Now playing:").set_thumbnail(url=pytube.YouTube(vc.current.uri).thumbnail_url))
                except:
                    await interaction.followup.send(embed=discord.Embed(title=f"**{vc.current.title}**",description=f"From the Spotify playlist/album: [{await spotipy.list_name(spotify_type,query)}]({query})",url=vc.current.uri).set_author(name="Now playing:"))

            elif playlist and not spotify_query:
                for track in track.tracks:
                    vc.queue.put(track)
                await vc.play(vc.queue.get())
                await interaction.followup.send(embed=discord.Embed(title=f"{vc.current.title}",description=f"From the playlist: **[{Playlist(query).title}]({query})**",url=vc.current.uri).set_author(name="Now playing:").set_thumbnail(url=pytube.YouTube(vc.current.uri).thumbnail_url))
            else:
                vc.queue.put(track)
                await vc.play(track)
                embed = discord.Embed(title=f"**{vc.current.title}**",url=vc.current.uri).set_author(name="Now playing:")
                embed.set_thumbnail(url=str(pytube.YouTube(vc.current.uri).thumbnail_url))
                await interaction.followup.send(embed=embed)

    #/skip
    @app_commands.command(name="skip",description="| Music | Skips to the next song on the queue")
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild_id)
        previous_song = player.current
        try:
            await player.play(player.queue[player.queue.find_position(player.current)+1],replace=True)
        except:
            await player.play(player.queue[0],replace=True)
        try:
            await interaction.followup.send(embed=discord.Embed(title=f"**{player.current.title}**",description=f"[{previous_song.title}]({previous_song.uri}) was skipped!",url=player.current.uri).set_thumbnail(url=str(pytube.YouTube(player.current.uri).thumbnail_url)).set_author(name="Now playing:"))
        except:
            await interaction.followup.send(embed=discord.Embed(title=f"**{player.current.title}**",description=f"[{previous_song.title}]({previous_song.uri}) was skipped!",url=player.current.uri).set_author(name="Now playing:"))

    # #/stealth_skip
    # @app_commands.command(name="stealth_skip",description="| Music / Debugging | Skips to the next song on the queue without replacing it")
    # async def stealth_skip(self, interaction: discord.Interaction):
    #     await interaction.response.defer(thinking=True)
    #     node = wavelink.NodePool.get_node()
    #     player = node.get_player(interaction.guild_id)
    #     previous_song = player.current

    #     await player.seek(player.current.duration)

    #     next_song = player.queue[player.queue.find_position(player.current)+1]
    #     await interaction.followup.send(embed=discord.Embed(title=f"**{next_song.title}**",description=f"[{previous_song.title}]({previous_song.uri}) was skipped without replacing (Stealth)!",url=next_song.uri).set_thumbnail(url=str(pytube.YouTube(next_song.uri).thumbnail_url)).set_author(name="Now playing:"))

    #/rewind
    @app_commands.command(name="rewind",description="| Music | Goes to the previous song in the queue")
    async def rewind(self, interaction: discord.Interaction):
        node = wavelink.NodePool.get_node()
        player = node.get_player(interaction.guild_id)
        next_song = player.current
        try:
            await player.play(player.queue[player.queue.find_position(player.current)-1])
        except ValueError:
            return await interaction.response.send_message("Already playing the first song in the queue!")
        try:
            await interaction.response.send_message(embed=discord.Embed(title=f"{player.current.title}",description=f"Rewinded from: [{next_song.title}]({next_song.uri})",url=player.current.uri).set_author(name="Now playing:").set_thumbnail(url=pytube.YouTube(player.current.uri).thumbnail_url))
        except:
            await interaction.response.send_message(embed=discord.Embed(title=f"{player.current.title}",description=f"Rewinded from: [{next_song.title}]({next_song.uri})",url=player.current.uri))

    #/volume
    @app_commands.command(name="volume",description="Changes the playback's volume from 0 - 1000")
    async def volume(self, interaction: discord.Interaction,volume: app_commands.Range[int,0,1000]):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("I'm not connected to any voice channels ¯\_(ツ)_/¯")
        else:
            node = wavelink.NodePool.get_node()
            player = node.get_player(interaction.guild_id)
            await player.set_volume(volume)
            await interaction.response.send_message(f"The volume was set to {volume}%")

    #/queue
    @app_commands.command(name="queue",description="| Music | Shows all the songs in the current queue")
    async def queue(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("I'm not connected to any voice channels ¯\_(ツ)_/¯")
        else:
            node = wavelink.NodePool.get_node()
            player = node.get_player(interaction.guild_id)

            embed=discord.Embed(title=f"Now playing:")
            embed.description = ""

            total_chars = 0
            item_chars = 0
            music_list="\n"
            for i, item in enumerate(player.queue):
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
                emb = discord.Embed(title="There's nothing playing",description="Maybe you can change that ;)")
                emb.footer("To play a song, you can either search for it, or paste its link in the query inside the `/play` command!")
                await interaction.response.send_message(embed=emb)

    #/stop
    @app_commands.command(name="stop",description="Stops the current playback, and disconnects from the voice channel")
    async def stop(self ,ctx: discord.Interaction) -> None:
        if not ctx.guild.voice_client:
            await ctx.response.send_message("I'm not connected to any voice channels ¯\_(ツ)_/¯")
        else:
            vc: wavelink.Player = ctx.guild.voice_client
            await vc.disconnect()
            await ctx.response.send_message("Okay! Stopped the current playback!")

async def setup(bot: commands.Bot) -> None:
    node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='dummythicc')
    await wavelink.NodePool.connect(client=bot, nodes=[node],spotify=sc)
    await bot.add_cog(music(bot))