import lightbulb
import hikari
import datetime
import guild_settings as gs

mod = lightbulb.Plugin("moderation")

#/ban
@mod.command()
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("reason", "Reason for the ban", required=False)
@lightbulb.option("user", "The user to ban.", type=hikari.User)
@lightbulb.command("ban", "Ban a user from the server.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ban(ctx: lightbulb.SlashContext) -> None:
    """Ban a user from the server with an optional reason."""
    if not ctx.guild_id:
        await ctx.respond(gs.text('only_server_command',gs.guild_language(ctx.guild_id)))
        return
    # Create a deferred response as the ban may take longer than 3 seconds
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    # Perform the ban
    await ctx.app.rest.ban_user(ctx.guild_id, ctx.options.user.id, reason=ctx.options.reason or hikari.UNDEFINED)
    # Provide feedback to the moderator
    await ctx.respond(f"{gs.text('banned').format(ctx.options.user.mention)}{ctx.options.reason or gs.text('no_reason_ban',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id))}")
    #await ctx.respond(f"Banned {ctx.options.user.mention}.\n**Reason:** {ctx.options.reason or 'No reason provided.'}")

#/purge
@mod.command()
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option("count", "The amount of messages to purge.", type=int, max_value=100, min_value=1)
@lightbulb.command("purge", "Purge a certain amount of messages from a channel.", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def purge(ctx: lightbulb.SlashContext, count: int) -> None:
    """Purge a certain amount of messages from a channel."""
    if not ctx.guild_id:
        await ctx.respond("This command can only be used in a server.")
        return
    # Fetch messages that are not older than 14 days in the channel the command is invoked in
    # Messages older than 14 days cannot be deleted by bots, so this is a necessary precaution
    messages = (
        await ctx.app.rest.fetch_messages(ctx.channel_id)
        .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
        .limit(count)
    )
    if messages:
        await ctx.app.rest.delete_messages(ctx.channel_id, messages)
        await ctx.respond(f"{gs.text('purged',gs.guild_language(ctx.guild_id)).format(len(messages))}")
    else:
        await ctx.respond(gs.text('too_old',gs.guild_language(ctx.guild_id)))

#/rename
@mod.command()
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.option("user","Who do you want to change the nickname?",type=hikari.User)
@lightbulb.option("nick","What do you want to call them?")
@lightbulb.command("rename","Changes an user's nickname")
@lightbulb.implements(lightbulb.SlashCommand)
async def rename(ctx: lightbulb.Context):
    user = ctx.options.user
    old_username = user.username
    nick = ctx.options.nick
    try:
        await ctx.app.rest.edit_member(user=user,guild=ctx.guild_id,nickname=nick)
        await ctx.respond(f"{gs.text('renamed_user',gs.guild_language(ctx.guild_id)).format(old_username,user.id)}")
        #await ctx.respond(f"User {old_username} was changed to <@{user.id}>",flags=hikari.MessageFlag.EPHEMERAL)
    except hikari.ForbiddenError:
        await ctx.respond(gs.text('no_permission_rename',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

#/server_language
@mod.command()
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("language",description="Which is this guild's main language?",choices=["English","Portuguese","Japanese"])
@lightbulb.command("server_language","Set the language for Xyn's responses")
@lightbulb.implements(lightbulb.SlashCommand)
async def server_lang(ctx:lightbulb.SlashContext) -> None:
    gs.set_language(ctx.guild_id, ctx.options.language)
    await ctx.respond(gs.text('set_language',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(ctx.options.language))

#/youtube_client
@mod.command()
@lightbulb.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("client",description="Which client do you want to use?",choices=["YouTube","Poketube"])
@lightbulb.command("youtube_client","Set the YouTube client used by Xyn's responses")
@lightbulb.implements(lightbulb.SlashCommand)
async def server_lang(ctx:lightbulb.SlashContext) -> None:
    gs.set(ctx.guild_id,"services","yt_client",ctx.options.client)
    await ctx.respond(gs.text('youtube_client',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)).format(ctx.options.client))

def load(bot: lightbulb.BotApp):
    bot.add_plugin(mod)

def unload(bot):
    bot.remove_plugin(mod)
