import aiohttp
import asyncio
from .cog import Cog
from .command import *
from fastapi import FastAPI
from functools import wraps
from .handler import handler
from .enums import AppCmdType
from .modal import Modal
from .user import User, ClientUser
from .permissions import Permissions
from .command import ApplicationCommand
from .component import Button, SelectMenu
from typing import Optional, List, Dict, Union, Callable


class Client(FastAPI):
    root_url = "https://discord.com/api/v10"

    def __init__(
            self,
            application_id: Union[int, str],
            public_key: str,
            token: str,
            *,
            commands: List[ApplicationCommand] = None,
            route: str = '/interactions',
            express_debug: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._session: aiohttp.ClientSession = None
        self.user: ClientUser = None
        self.owner: User = None
        self.token = token
        self.public_key = public_key
        self.application_id = application_id
        self.express_debug = express_debug
        self.ui_factory: Optional[Dict[str, Union[Button, Modal, SelectMenu]]] = {}
        self._qualified_commands: List[ApplicationCommand] = commands or []
        self.application_commands: Dict[str, ApplicationCommand] = {}
        self.cached_inter_tokens: Dict[str, str] = {}
        self.add_route(route, handler, methods=['POST'], include_in_schema=False)

    def _load_component(self, component: Union[Button, Modal, SelectMenu]):
        self.ui_factory[component.custom_id] = component

    def _load_inter_token(self, interaction_id: str, token: str):
        self.cached_inter_tokens[interaction_id] = token

    def command(
            self,
            name: str,
            description: str = None,
            *,
            options: List[Option] = None,
            permissions: List[Permissions] = None,
            dm_access: bool = True,
            guild_id: int = None,
            category: AppCmdType = AppCmdType.slash,
    ):
        command = ApplicationCommand(
            name=name,
            description=description,
            options=options,
            permissions=permissions,
            dm_access=dm_access,
            guild_id=guild_id,
            category=category
        )

        def decorator(coro: Callable):
            @wraps(coro)
            def wrapper(*_, **__):
                if asyncio.iscoroutinefunction(coro):
                    command._callback = coro
                    self._qualified_commands.append(command)
                    return command
            return wrapper()
        return decorator

    def load_commands(self, *commands: ApplicationCommand):
        self._qualified_commands.extend(commands)
    
    async def delete_command(self, command_id: str, guild_id: int = None):
        if not guild_id:
            url = f"/api/v10/applications/{self.application_id}/commands/{command_id}"
        else:
            url = f"/api/v10/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}"
        await self._session.delete(url)
    
    async def __init_session(self):
        if not self.token:
            raise ValueError("Token is not provided")
        headers = {"Authorization": f"Bot {self.token}"}
        self._session = aiohttp.ClientSession(base_url="https://discord.com", headers=headers)
    
    async def __cache_client(self):
        data = await (await self._session.get(f"/api/v10/oauth2/applications/@me")).json()
        self.user = ClientUser(data)
        self.owner = self.user.owner
    
    async def __sync_cmds(self):
        for command in self._qualified_commands:
            if command.guild_id:
                url = f"/api/v10/applications/{self.application_id}/guilds/{command.guild_id}/commands"
            else:
                url = f"/api/v10/applications/{self.application_id}/commands"
            resp = await (await self._session.post(url, json=command.json())).json()
            try:
                command.id = resp['id']
            except KeyError:
                raise ValueError(str(resp))
            else:
                self.application_commands[command.id] = command

    async def __call__(self, scope, receive, send):
        if self.root_path:
            scope["root_path"] = self.root_path
        await self.__init_session()
        await self.__cache_client()
        await self.__sync_cmds()
        self._qualified_commands.clear()
        await super().__call__(scope, receive, send)

    def add_cog(self, cog: Cog):
        if isinstance(cog, Cog):
            self.load_commands(*cog.private_commands)

    def load_cog(self, path: str):
        import importlib
        importlib.import_module(path).setup(self)
