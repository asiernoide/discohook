from fastapi import Request
from .interaction import Interaction
from .command import *
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from fastapi.responses import JSONResponse, Response
from .cmdparse import (
    build_modal_params,
    build_slash_command_prams,
    build_context_menu_param,
    build_select_menu_values,
)
from .enums import (
    AppCmdType,
    InteractionType,
    MessageComponentType,
    InteractionCallbackType,
)
from .errors import NotImplemented


# noinspection PyProtectedMember
async def handler(request: Request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    try:
        key = VerifyKey(bytes.fromhex(request.app.public_key))
        key.verify(str(timestamp).encode() + await request.body(), bytes.fromhex(str(signature)))
    except BadSignatureError:
        return Response(content='BadSignature', status_code=401)
    
    data = await request.json()
    interaction = Interaction(data)
    interaction.client = request.app
    interaction.client.request = request
    try:
        if interaction.type == InteractionType.ping.value:
            return JSONResponse({'type': InteractionCallbackType.pong.value}, status_code=200)

        elif interaction.type == InteractionType.app_command.value:
            command: ApplicationCommand = request.app.application_commands.get(interaction._app_command_data.id)
            if not command:
                raise NotImplemented(data)
            if not (interaction.data['type'] == AppCmdType.slash.value):
                target_object = build_context_menu_param(interaction)
                if command.cog:
                    await command._callback(command.cog, interaction, target_object)
                    return request.app._populated_return
                else:
                    await command._callback(interaction, target_object)
                    return request.app._populated_return
                    
            if interaction.data.get('options') and (
                    interaction.data['options'][0].get('type') == AppCmdOptionType.subcommand.value):
                subcommand = command._subcommand_callbacks.get(interaction.data['options'][0]['name'])
                if command.cog:
                    args, kwargs = build_slash_command_prams(subcommand, interaction, 2)
                    await subcommand(command.cog, interaction, *args, **kwargs)
                    return request.app._populated_return
                else:
                    args, kwargs = build_slash_command_prams(subcommand, interaction)
                    await subcommand(interaction, *args, **kwargs)
                    return request.app._populated_return
                    
            if command.cog:
                args, kwargs = build_slash_command_prams(command._callback, interaction, 2)
                await command._callback(command.cog, interaction, *args, **kwargs)
                return request.app._populated_return
            else:
                args, kwargs = build_slash_command_prams(command._callback, interaction)
                await command._callback(interaction, *args, **kwargs)
                return request.app._populated_return

        elif interaction.type == InteractionType.component.value:
            custom_id = interaction.data['custom_id']
            component = request.app.ui_factory.get(custom_id, None)
            if not component:
                return JSONResponse({'error': 'component not found!'}, status_code=404)
            if interaction.data['component_type'] == MessageComponentType.button.value:
                await component._callback(interaction)
                if request.app._populated_return:
                    return request.app._populated_return
            if interaction.data['component_type'] == MessageComponentType.select_menu.value:
                await component._callback(interaction, build_select_menu_values(interaction))
                if request.app._populated_return:
                    return request.app._populated_return

        elif interaction.type == InteractionType.modal_submit.value:
            component = request.app.ui_factory.get(interaction.data['custom_id'], None)
            if not component:
                return JSONResponse({'error': 'component not found!'}, status_code=404)
            args, kwargs = build_modal_params(component._callback, interaction)
            await component._callback(interaction, *args, **kwargs)
            return request.app._populated_return
        elif interaction.type == InteractionType.autocomplete.value:
            command: ApplicationCommand = request.app.application_commands.get(interaction.data['id'])
            if not command:
                return JSONResponse({'error': 'command not found!'}, status_code=404)
            callback = command._autocomplete_callback
            option_name = interaction.data['options'][0]['name']
            option_value = interaction.data['options'][0]['value']
            if option_value:
                await callback(interaction, option_name, option_value)
                return request.app._populated_return
        else:
            return JSONResponse({'message': "unhandled interaction type"}, status_code=300)
    except Exception as e:
        if request.app._global_error_handler:
            await request.app._global_error_handler(e, data)
