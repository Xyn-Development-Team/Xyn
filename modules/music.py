#Porting done
#Translation done!

import lightbulb
from lightbulb.ext import tasks
import hikari
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lavaplayer
import asyncio
import miru
import pythumb
import os
import re
import guild_settings as gs
from dotenv import load_dotenv
load_dotenv()

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

#Player classes

class MusicViewPaused(miru.View):

    def __init__(self) -> None:
        super().__init__(timeout=60)

    @miru.button(label="Stop",emoji=chr(9209), style=hikari.ButtonStyle.DANGER)
    async def stop_button(self, button: miru.Button, ctx: miru.Context):
        self.stop()
        await lavalink.stop(ctx.guild_id)
        await music.bot.update_voice_state(ctx.guild_id, None)
        await self.message.delete()

    @miru.button(label="Resume", emoji="▶️", style=hikari.ButtonStyle.SUCCESS)
    async def resume_button(self, button: miru.Button, ctx: miru.Context) -> None:
        await lavalink.pause(ctx.guild_id, False)
        View = MusicView()
        message = await self.message.edit(components=View.build())
        await View.start(message)

    @miru.button(label="Skip", emoji="⏩", style=hikari.ButtonStyle.PRIMARY)
    async def skip_button(self, button: miru.Button, ctx: miru.Context):
        await lavalink.skip(ctx.guild_id)

    @miru.button(label="Volume +", emoji="🔊", style=hikari.ButtonStyle.PRIMARY)
    async def volup_button(self, button: miru.Button, ctx: miru.Context):
        node = await lavalink.get_guild_node(ctx.guild_id)
        await lavalink.volume(ctx.guild_id,node.volume + 10)

    @miru.button(label="Volume -", emoji="🔉", style=hikari.ButtonStyle.PRIMARY)
    async def voldown_button(self, button: miru.Button, ctx: miru.Context):
        node = await lavalink.get_guild_node(ctx.guild_id)
        await lavalink.volume(ctx.guild_id,node.volume - 10)

    async def on_timeout(self):
        try:
            await self.message.delete()
        except hikari.errors.NotFoundError:
            pass
        

class MusicView(miru.View):

    def __init__(self) -> None:
        super().__init__(timeout=60)

    @miru.button(label="Stop",emoji=chr(9209), style=hikari.ButtonStyle.DANGER)
    async def stop_button(self, button: miru.Button, ctx: miru.Context):
        self.stop()
        await lavalink.stop(ctx.guild_id)
        await music.bot.update_voice_state(ctx.guild_id, None)
        await self.message.delete()

    @miru.button(label="Pause", emoji="⏸️", style=hikari.ButtonStyle.PRIMARY)
    async def pause_button(self, button: miru.Button, ctx: miru.Context) -> None:

        await lavalink.pause(ctx.guild_id, True)
        View = MusicViewPaused()
        node = await lavalink.get_guild_node(ctx.guild_id)
        message = await self.message.edit(components=View.build())
        await View.start(message)

    @miru.button(label="Skip", emoji="⏩", style=hikari.ButtonStyle.PRIMARY)
    async def skip_button(self, button: miru.Button, ctx: miru.Context):
        await lavalink.skip(ctx.guild_id)

    @miru.button(label="Volume +", emoji="🔊", style=hikari.ButtonStyle.PRIMARY)
    async def volup_button(self, button: miru.Button, ctx: miru.Context):
        node = await lavalink.get_guild_node(ctx.guild_id)
        await lavalink.volume(ctx.guild_id,node.volume + 10)

    @miru.button(label="Volume -", emoji="🔉", style=hikari.ButtonStyle.PRIMARY)
    async def voldown_button(self, button: miru.Button, ctx: miru.Context):
        node = await lavalink.get_guild_node(ctx.guild_id)
        await lavalink.volume(ctx.guild_id,node.volume - 10)

    async def on_timeout(self):
        try:
            await self.message.delete()
        except hikari.errors.NotFoundError:
            pass


music = lightbulb.Plugin("music")

lavalink = lavaplayer.Lavalink(host=os.getenv("lavalink_host"),port=int(os.getenv("lavalink_port")),password=os.getenv("lavalink_password"),user_id=int(os.getenv("user_id")))

async def get_spotify(type,query,pos=0):
    
    if type == "track":
        track_name = spotify.track(query)["name"]
        artist = spotify.track(query)["artists"]
        artist = spotify.track(query)["artists"][0]["name"]
        query = f"{track_name} {artist}"
        return query
    if type != "track":
        sp_playlist = []
    if type == "album":
        tracks = spotify.album_tracks(query)["items"]
        for t in range(len(tracks)):
            track_name = tracks[t]["name"]
            artist = tracks[t]["artists"][0]["name"]
            query = f"{track_name} {artist}"
            sp_playlist.append(query)
        return sp_playlist
    elif type == "playlist":
        tracks = spotify.playlist_items(playlist_id=query,fields="items.track.name")["items"]
        artists = spotify.playlist_items(playlist_id=query,fields="items.track.artists.name")["items"]
        for t in range(len(tracks)):
            track_name = tracks[t]["track"]["name"]
            artist = artists[t]["track"]["artists"][0]["name"]
            query = f"{track_name} {artist}"
            sp_playlist.append(query)
        return sp_playlist

#Join function
async def join(ctx:lightbulb.context.Context):
    voice_state = music.app.cache.get_voice_state(ctx.guild_id,ctx.user.id)
    if not voice_state:
        await ctx.respond(gs.text('no_voice',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
        return "no_voice"
    channel_id = voice_state.channel_id
    await music.app.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)


def transform_uri(id,uri):
    if gs.read(id,"services","yt_client",True,"YouTube") == "Poketube":
        uri = re.sub("www.youtube.com","poketube.fun",uri)
        uri = re.sub("youtube.com","poketube.fun",uri)
    elif gs.read(id,"services","yt_client",True,"YouTube") == "YouTube":
        uri = uri
    return uri

#/play
@music.command()
@lightbulb.option(name="query", description="Music's name / partial name or even a url", required=True)
@lightbulb.command(name="play", description="Play a cool music in your voice channel",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def play_command(ctx: lightbulb.context.Context,music=None):
    multi_spotify = False
    if music:
        query = music
    query = ctx.options.query  # get query from options
    sp_playlist = []
    
    #A poorly made support for Poketube!
    if any(["poketube.fun/watch?v=" in query]):
        pattern = re.escape("poketube.fun/watch?v=")
        id = re.sub(re.escape("https://"),"",query)
        id = re.sub(re.escape("http://"),"",id)
        id = re.sub(re.escape("www."),"",id)
        id = re.sub(re.escape("www"),"",id)
        id = re.sub(pattern,"",id)
        query = f"https://youtube.com/watch?v={id}"
        poketube = True

    if any(["poketube.fun/music?v=" in query]):
        pattern = re.escape("poketube.fun/watch?v=")
        id = re.sub(re.escape("https://"),"",query)
        id = re.sub(re.escape("http://"),"",id)
        id = re.sub(re.escape("www."),"",id)
        id = re.sub(re.escape("www"),"",id)
        id = re.sub(pattern,"",id)
        id = re.sub("poketube.fun/music?v=","",query)
        query = f"https://youtube.com/watch?v={id}"
        poketube = True

    if any(["open.spotify.com/track/" in query]):
        query = await get_spotify("track", query)
            
    elif any(["open.spotify.com/album/" in query]):
        multi_spotify = True
        tracks = spotify.album_tracks(query)["items"]
        sp_playlist = await get_spotify("album", query)

    elif any(["open.spotify.com/playlist/" in query]):
        multi_spotify = True
        sp_playlist = await get_spotify("playlist",query)
                                
    if multi_spotify == True:
        query = sp_playlist 
        for q in query:
            result = await lavalink.auto_search_tracks(q)

            if not result:
                await ctx.respond(f"{query[q]} wasn't found!")
                continue
            elif isinstance(result, lavaplayer.TrackLoadFailed):
                await ctx.respond(gs.text('generic_error_music',gs.guild_language(ctx.guild_id)).format(result.message),gs.get_uwu(ctx.guild_id))
                return
            try:
                await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
                await join(ctx)
            except IndexError:
                pass
                await lavalink.volume(ctx.guild_id,50) #Safe volume
            except:
                await join(ctx)
                try:
                    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
                    await join(ctx)
                except IndexError:
                    pass
                await lavalink.volume(ctx.guild_id,50) #Safe volume
            node = await lavalink.get_guild_node(ctx.guild_id)
        return await ctx.respond(gs.text('added_spotify',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
    
    elif multi_spotify == False:
        result = await lavalink.auto_search_tracks(query)  # search for the query
        if not result:
            await ctx.respond(gs.text('music_not_found',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
            return
        elif isinstance(result, lavaplayer.TrackLoadFailed):
            await ctx.respond(gs.text('generic_error_music',gs.guild_language(ctx.guild_id)).format(result.message),gs.get_uwu(ctx.guild_id))
            return
        elif isinstance(result, lavaplayer.PlayList):
            try:
                await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
                await ctx.respond(gs.text('playlist_added',gs.guild_language(ctx.guild_id)).format(len(result.tracks)),gs.get_uwu(ctx.guild_id))
            except:
                await join(ctx)
                await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
                try:    
                    await ctx.respond(gs.text('playlist_added',gs.guild_language(ctx.guild_id)).format(len(result.tracks)),gs.get_uwu(ctx.guild_id))
                except:
                    await ctx.respond("Playlist added to queue")
            return 
        try:
            await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
            await lavalink.volume(ctx.guild_id,50) #Safe volume
        except:
            if await join(ctx) == "no_voice":
                #await ctx.respond(gs.text('no_voice',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
                return
            await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
            await lavalink.volume(ctx.guild_id,50) #Safe volume
        await ctx.respond(gs.text('added_queue',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(result[0].title,transform_uri(ctx.guild_id,result[0].uri)))

#/now_playing
@music.command()
@lightbulb.command("now_playing","See what's playing at the moment")
@lightbulb.implements(lightbulb.SlashCommand)
async def now_playing(ctx: lightbulb.context.Context):
    emb = hikari.Embed(title=gs.text("not_playing",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),description=gs.text("yet",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
    emb.set_footer(gs.text("not_playing_tease",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond(emb)
        return
    if gs.read(ctx.guild_id,"services","yt_client",True,"YouTube") == "Poketube":
        uri = re.sub("www.youtube.com","poketube.fun",node.queue[0].uri)
        uri = re.sub("youtube.com","poketube.fun",uri)
    elif gs.read(ctx.guild_id,"services","yt_client",True,"YouTube") == "YouTube":
        uri = node.queue[0].uri
    await ctx.respond(f"{gs.text('now_playing',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(node.queue[0].title,uri)}")
    # await ctx.respond(f"Now Playing...\n[{node.queue[0].title}]({node.queue[0].uri})")

#/music_skip
@music.command()
@lightbulb.command("music_skip","Skip a song on the queue")
@lightbulb.implements(lightbulb.SlashCommand)
async def music_skip(ctx: lightbulb.context.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue: #Checks if anything else is playing
        await now_playing(ctx)
    else:
        await lavalink.skip(ctx.guild_id)
        await ctx.respond(f"{gs.text('skipped_music',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(node.queue[1].title,node.queue[1].uri)}")
        #ctx.respond(f"Skipped to the next song:\n [{node.queue[1].title}]({node.queue[1].uri})") #Bugfixed 0, current song | 1 next song  

#/resume
@music.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(lightbulb.SlashCommand)
async def resume_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond(gs.text("resumed_music",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))

#/vol
@music.command()
@lightbulb.option(name="vol", description="Volume to set (It usually starts at 50%)", required=True)
@lightbulb.command(name="volume", description="Changes the bot's music volume")
@lightbulb.implements(lightbulb.SlashCommand)
async def volume_command(ctx: lightbulb.context.Context):
    volume = int(ctx.options.vol)
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"{gs.text('volume_set',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(volume)}")

#/pause
@music.command()
@lightbulb.command(name="pause", description="Pauses the current music playback")
@lightbulb.implements(lightbulb.SlashCommand)
async def pause_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, True)
    node = await lavalink.get_guild_node(ctx.guild_id)
    await ctx.respond(f"{gs.text('paused',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(title=node.queue[0].title)}")

#/stop
@music.command()
@lightbulb.command(name="stop", description="Stop the music")
@lightbulb.implements(lightbulb.SlashCommand)
async def stop_command(ctx: lightbulb.context.Context):
    try:
        await lavalink.stop(ctx.guild_id)
    except:
        pass
    try:
        await music.app.update_voice_state(ctx.guild_id, None)
    except:
        await ctx.respond(gs.text("stuck",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
    else:
        await ctx.respond(gs.text("music_stop",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))

#/queue
@music.command() #Queue
@lightbulb.command(name="queue", description="Shows which songs are on the queue") 
@lightbulb.implements(lightbulb.SlashCommand)
async def queue_command(ctx: lightbulb.context.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        emb = hikari.Embed(title=gs.text("not_playing",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),description=gs.text("yet",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
        emb.set_footer(gs.text("not_playing_tease",gs.guild_language(ctx.guild_id)))
    else:
        emb = hikari.Embed(
            description="\n".join(
                [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
        )
    await ctx.respond(emb)


#/play_random
@music.command()
@lightbulb.command(name="play_random", description="Plays a random song from YouTube",auto_defer=True) 
@lightbulb.implements(lightbulb.SlashCommand)
async def play_random(ctx: lightbulb.context.Context):
    from pytube import Playlist
    import random
    playlist_ids = ["PL15B1E77BB5708555","PL55713C70BA91BD6E","PLFgquLnL59akA2PflFpeQG9L01VFg90wS","PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI","PLw-VjHDlEOgvWPpRBs9FRGgJcKpDimTqf"]
    p = Playlist(f"https://www.youtube.com/playlist?list={random.choice(playlist_ids)}")
    music = random.randint(0,len(p.videos))
    query = p.video_urls[music]
    #await ctx.respond(str(query))

    result = await lavalink.auto_search_tracks(query)  # search for the query
    if not result:
        await ctx.respond(gs.text('music_not_found',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond(gs.text('generic_error_music',gs.guild_language(ctx.guild_id)).format(result.message),gs.get_uwu(ctx.guild_id))
        return
    elif isinstance(result, lavaplayer.PlayList):
        try:
            await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
            await ctx.respond(gs.text('playlist_added',gs.guild_language(ctx.guild_id)).format(len(result.tracks)),gs.get_uwu(ctx.guild_id))
        except:
            await join(ctx)
            await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
            try:    
                await ctx.respond(gs.text('playlist_added',gs.guild_language(ctx.guild_id)).format(len(result.tracks)),gs.get_uwu(ctx.guild_id))
            except:
                await ctx.respond("Playlist added to queue")
        return 
    try:
        await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
        await lavalink.volume(ctx.guild_id,50) #Safe volume
    except:
        if await join(ctx) == "no_voice":
            #await ctx.respond(gs.text('no_voice',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
        await lavalink.volume(ctx.guild_id,50) #Safe volume
    if gs.read(ctx.guild_id,"services","yt_client",True,"YouTube") == "Poketube":
        uri = re.sub("www.youtube.com","poketube.fun",result[0].uri)
        uri = re.sub("youtube.com","poketube.fun",uri)
    elif gs.read(ctx.guild_id,"services","yt_client",True,"YouTube") == "YouTube":
        uri = result[0].uri
    await ctx.respond(gs.text('added_queue',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(result[0].title,uri))

@music.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    try:
        await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)
    except lavaplayer.exceptions.NodeError:
        pass

@music.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)

#/player
@music.command #Embeded player a.k.a embp
@lightbulb.command("player","A Cool little GUI player!",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def emb_player(ctx: lightbulb.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue: #Checks if anything else is playing
        await now_playing(ctx)
        return
    if node.is_pause == False:
        View = MusicView()  # Create a new View
    elif node.is_pause == True:
        View = MusicViewPaused()
    class res():
        emb = hikari.Embed(title=f"{node.queue[0].title}",description=f"{node.queue[0].author}")
        try:
            thumb = emb.set_thumbnail(pythumb.Thumbnail(node.queue[0].uri).fetch())
        except:
            thumb = emb.set_thumbnail("./sources/unknown_music.png")
    try:
        message = await ctx.respond(res.emb,components=View.build())
        await View.start(message)  # Start listening for interactions
    except:
        try:
            message = await ctx.respond(res.emb,components=View.build())
            await View.start(message)  # Start listening for interactions
        except:
            await ctx.respond(gs.text("generic_player_error",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

    @tasks.task(s=0.5,auto_start=True,max_consecutive_failures=float('inf'),wait_before_execution=True)
    async def sync_player():
        node = await lavalink.get_guild_node(ctx.guild_id)
        if not node or not node.queue:
            res.emb = hikari.Embed(title=f"{gs.text('not_playing',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id))}",description=f"Yet...")
        try:
            if res.emb.title != node.queue[0].title and res.emb.title != None:
                res.emb = hikari.Embed(title=f"{node.queue[0].title}",description=f"{node.queue[0].author}")
                res.emb.set_thumbnail(pythumb.Thumbnail(node.queue[0].uri).fetch())
                await message.edit(res.emb,components=View.build())
        except IndexError or AttributeError:
            res.emb = hikari.Embed(title=f"There's nothing playing!",description=f"Yet...")
        except:
            pass

def load(bot: lightbulb.BotApp):
    bot.add_plugin(music)
    lavalink.set_user_id(bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

def unload(bot):
    bot.remove_plugin(music)