from .role import Role
from .channel import Channel
from .enums import ChannelType
from .emoji import PartialEmoji
from .permissions import Permissions
from typing import Dict, Any, TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .client import Client


class PartialGuild:
    """
    Represents a partial guild.
    """

    def __init__(self, guild_id: str, client: "Client"):
        self.id = guild_id
        self.client = client

    async def fetch_channels(self) -> List[Channel]:
        """
        Fetches all channels in the guild.

        Returns
        -------
        List[Channel]
        """
        resp = await self.client.http.fetch_guild_channels(self.id)
        data = await resp.json()
        return [Channel(c, self.client) for c in data]

    async def fetch_roles(self) -> List[Role]:
        """
        Fetches all roles in the guild.

        Returns
        -------
        List[Role]
        """
        resp = await self.client.http.fetch_guild_roles(self.id)
        data = await resp.json()
        return [Role(r, self.client) for r in data]

    async def create_channel(
        self,
        name: str,
        *,
        type: ChannelType = ChannelType.guild_text,
        topic: str = None,
        bitrate: int = None,
        user_limit: int = None,
        rate_limit_per_user: int = None,
        position: int = None,
        permission_overwrites: List[Dict[str, Any]] = None,
        parent_id: str = None,
        nsfw: bool = None,
        rtc_region: str = None,
        video_quality_mode: int = None,
        default_auto_archive_duration: int = None,
        default_reaction_emoji: PartialEmoji = None,
        available_tags: List[Dict[str, Any]] = None,
        default_sort_order: int = None,
    ) -> Channel:
        """
        Creates a channel in the guild. Requires the MANAGE_CHANNELS permission.

        Parameters
        ----------
        name: str
            Name of the channel (2-100 characters)
        type: ChannelType
            The type of channel
        topic: str
            Channel topic (0-1024 characters)
        bitrate: int
            The bitrate (in bits) of the voice channel (voice only)
        user_limit: int
            The user limit of the voice channel (voice only)
        rate_limit_per_user: int
            Amount of seconds a user has to wait before sending another message (0-21600)
            bots, as well as users with the permission manage_messages or manage_channel, are unaffected
        position: int
            Sorting position of the channel
        permission_overwrites: List[Dict[str, Any]]
            The channel's permission overwrites
        parent_id: str
            The id of the parent category for a channel (each parent category can contain up to 50 channels)
        nsfw: bool
            Whether the channel is nsfw
        rtc_region: str
            The id of the voice region
        video_quality_mode: int
            The camera video quality mode of the voice channel, 1 when not present
        default_auto_archive_duration: int
            The default duration for newly created threads, in minutes, to automatically archive the thread
            after recent activity, can be set to: 60, 1440, 4320, 10080
        default_reaction_emoji: PartialEmoji
            The default auto-emoji for newly created threads, custom guild emojis must be enabled
        available_tags: List[Dict[str, Any]]
            The channel tags used for public guilds
        default_sort_order: int
            The default sorting order for posts in a forum channel

        Returns
        -------
        :class:`Channel`
        """
        payload = {"name": name, "type": type.value}
        if topic:
            payload["topic"] = topic
        if bitrate:
            payload["bitrate"] = bitrate
        if user_limit:
            payload["user_limit"] = user_limit
        if rate_limit_per_user:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if position:
            payload["position"] = position
        if permission_overwrites:
            payload["permission_overwrites"] = permission_overwrites
        if parent_id:
            payload["parent_id"] = parent_id
        if nsfw:
            payload["nsfw"] = nsfw
        if rtc_region:
            payload["rtc_region"] = rtc_region
        if video_quality_mode:
            payload["video_quality_mode"] = video_quality_mode
        if default_auto_archive_duration:
            payload["default_auto_archive_duration"] = default_auto_archive_duration
        if default_reaction_emoji:
            payload["default_reaction_emoji"] = default_reaction_emoji
        if available_tags:
            payload["available_tags"] = available_tags
        if default_sort_order:
            payload["default_sort_order"] = default_sort_order
        resp = await self.client.http.create_guild_channel(self.id, payload)
        data = await resp.json()
        return Channel(data, self.client)

    async def edit_channel_position(
        self,
        channel_id: str,
        *,
        position: int,
        lock_permissions: bool = False,
        parent_id: Optional[str] = None,
    ):
        """
        Changes the position of the channel. Only available for guild channels.
        Parameters
        ----------
        channel_id: :class:`str`
            The id of the channel to move.
        position: :class:`int`
            The new position of the channel.
        lock_permissions:
            Whether to sync the permissions of the channel with the parent category.
        parent_id: Optional[:class:`str`]
            The id of the parent category to move the channel to.
            If not provided, the channel will be moved to the root.
        """
        payload = {"id": channel_id, "position": position, "lock_permissions": lock_permissions}
        if parent_id:
            payload["parent_id"] = parent_id
        await self.client.http.edit_guild_channel_position(self.id, payload)

    async def create_role(
            self,
            name: str,
            *,
            permissions: Optional[List[Permissions]] = None,
            color: int = 0,
            hoist: bool = False,
            mentionable: bool = False,
            icon_data_uri: str = None,
            unicode_emoji: str = None,

    ):
        payload = {"name": name}
        base_permissions = 0
        if permissions:
            for permission in permissions:
                base_permissions |= permission.value
        payload["permissions"] = base_permissions
        if color:
            payload["color"] = color
        if hoist:
            payload["hoist"] = hoist
        if mentionable:
            payload["mentionable"] = mentionable
        if icon_data_uri:
            payload["icon"] = icon_data_uri
        if unicode_emoji:
            payload["unicode_emoji"] = unicode_emoji
        resp = await self.client.http.create_guild_role(self.id, payload)
        data = await resp.json()
        return Role(data, self.client)


class Guild(PartialGuild):
    """
    Represents a Discord guild. Subclass of :class:`PartialGuild`.

    Attributes
    ----------
    id: :class:`str`
        The id of the guild.
    name: :class:`str`
        The name of the guild.
    icon: Optional[:class:`str`]
        The icon hash of the guild.
    icon_hash: Optional[:class:`str`]
        The icon hash of the guild.
    splash: Optional[:class:`str`]
        The splash hash of the guild.
    discovery_splash: Optional[:class:`str`]
        The discovery splash hash of the guild.
    owner: Optional[:class:`bool`]
        Whether the user is the owner of the guild.
    owner_id: :class:`str`
        The id of the owner of the guild.
    permissions: Optional[:class:`int`]
        The total permissions of the user in the guild (does not include channel overrides).
    afk_channel_id: Optional[:class:`str`]
        The id of the afk channel.
    afk_timeout: :class:`int`
        The afk timeout in seconds.
    widget_enabled: Optional[:class:`bool`]
        Whether the widget is enabled.
    widget_channel_id: Optional[:class:`str`]
        The id of the channel for the widget.
    verification_level: :class:`int`
        The verification level required for the guild.
    default_message_notifications: :class:`int`
        The default message notifications level.
    explicit_content_filter: :class:`int`
        The explicit content filter level.
    roles: List[:class:`Role`]
        The roles in the guild.
    emojis: List[:class:`Emoji`]
        The emojis in the guild.
    features: List[:class:`str`]
        The features of the guild.
    mfa_level: :class:`int`
        The mfa level required for the guild.
    application_id: Optional[:class:`str`]
        The application id of the guild creator if it is bot-created.
    system_channel_id: Optional[:class:`str`]
        The id of the system channel.
    system_channel_flags: :class:`int`
        The system channel flags.
    rules_channel_id: Optional[:class:`str`]
        The id of the rules channel.
    max_presences: Optional[:class:`int`]
        The maximum number of presences for the guild.
    max_members: :class:`int`
        The maximum number of members for the guild.
    vanity_url_code: Optional[:class:`str`]
        The vanity url code of the guild.
    description: Optional[:class:`str`]
        The description of the guild.
    banner: Optional[:class:`str`]
        The banner hash of the guild.
    premium_tier: :class:`int`
        The premium tier of the guild.
    premium_subscription_count: :class:`int`
        The number of boosts of the guild.
    preferred_locale: :class:`str`
        The preferred locale of the guild.
    public_updates_channel_id: Optional[:class:`str`]
        The id of the public updates channel.
    max_video_channel_users: Optional[:class:`int`]
        The maximum number of users in a video channel.
    approximate_member_count: Optional[:class:`int`]
        The approximate number of members in the guild.
    approximate_presence_count: Optional[:class:`int`]
        The approximate number of presences in the guild.
    welcome_screen: Optional[:class:`dict`]
        The welcome screen object of the guild.
    nsfw_level: :class:`int`
        The nsfw level of the guild.
    stickers: List[:class:`Sticker`]
        The stickers in the guild.
    premium_progress_bar_enabled: Optional[:class:`bool`]
        Whether the premium progress bar is enabled.
    """

    def __init__(self, data: Dict[str, Any], client: "Client"):
        super().__init__(data["id"], client)
        self.name = data["name"]
        self.icon = data.get("icon")
        self.icon_hash = data.get("icon_hash")
        self.splash = data.get("splash")
        self.discovery_splash = data.get("discovery_splash")
        self.owner = data.get("owner")
        self.owner_id = data["owner_id"]
        self.permissions = data.get("permissions")
        self.afk_channel_id = data.get("afk_channel_id")
        self.afk_timeout = data["afk_timeout"]
        self.widget_enabled = data.get("widget_enabled")
        self.widget_channel_id = data.get("widget_channel_id")
        self.verification_level = data["verification_level"]
        self.default_message_notifications = data["default_message_notifications"]
        self.explicit_content_filter = data["explicit_content_filter"]
        self.roles = data["roles"]
        self.emojis = data["emojis"]
        self.features = data["features"]
        self.mfa_level = data["mfa_level"]
        self.application_id = data.get("application_id")
        self.system_channel_id = data.get("system_channel_id")
        self.system_channel_flags = data["system_channel_flags"]
        self.rules_channel_id = data.get("rules_channel_id")
        self.max_presences = data.get("max_presences")
        self.max_members = data.get("max_members")
        self.vanity_url_code = data.get("vanity_url_code")
        self.description = data.get("description")
        self.banner = data.get("banner")
        self.premium_tier = data["premium_tier"]
        self.premium_subscription_count = data.get("premium_subscription_count")
        self.preferred_locale = data["preferred_locale"]
        self.public_updates_channel_id = data.get("public_updates_channel_id")
        self.max_video_channel_users = data.get("max_video_channel_users")
        self.approximate_member_count = data.get("approximate_member_count")
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.welcome_screen = data.get("welcome_screen")
        self.nsfw_level = data["nsfw_level"]
        self.stickers = data.get("stickers")
        self.premium_progress_bar_enabled = data["premium_progress_bar_enabled"]
