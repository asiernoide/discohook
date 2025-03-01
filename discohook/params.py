from .file import File
from .view import View
from .embed import Embed
from typing import Optional, List, Any


MISSING = Any


def merge_fields(field: Optional[Any], fields: Optional[List[Any]]) -> List[Any]:
    tmp = []
    if field and field is not MISSING:
        tmp.append(field)
    if fields and fields is not MISSING:
        tmp.extend(fields)
    return tmp


def handle_send_params(
    content: Optional[str] = None,
    *,
    embed: Optional[Embed] = None,
    embeds: Optional[List[Embed]] = None,
    view: Optional[View] = None,
    tts: Optional[bool] = False,
    file: Optional[File] = None,
    files: Optional[List[File]] = None,
    ephemeral: Optional[bool] = False,
    suppress_embeds: Optional[bool] = False,
):
    payload = {}
    flag_value = 0
    embeds = merge_fields(embed, embeds)
    files = merge_fields(file, files)
    if ephemeral:
        flag_value |= 1 << 6
    if suppress_embeds:
        flag_value |= 1 << 2
    if content:
        payload["content"] = str(content)
    if tts:
        payload["tts"] = True
    if embeds:
        payload["embeds"] = [embed.to_dict() for embed in embeds]
    if view:
        payload["components"] = view.components
    if files:
        payload["attachments"] = [
            {
                "id": i,
                "filename": file.name,
                "ephemeral": file.spoiler,
                "description": file.description,
            }
            for i, file in enumerate(files)
        ]
    if flag_value:
        payload["flags"] = flag_value
    return payload


def handle_edit_params(
    content: Optional[str] = MISSING,
    *,
    embed: Optional[Embed] = MISSING,
    embeds: Optional[List[Embed]] = MISSING,
    view: Optional[View] = MISSING,
    tts: Optional[bool] = MISSING,
    file: Optional[File] = MISSING,
    files: Optional[List[File]] = MISSING,
    suppress_embeds: Optional[bool] = MISSING,
):
    payload = {}
    if embed is None:
        payload["embeds"] = []
    if embeds is None:
        payload["embeds"] = []
    if view is None:
        payload["components"] = []
    if file is None:
        payload["attachments"] = []
    if files is None:
        payload["attachments"] = []
    embeds = merge_fields(embed, embeds)
    files = merge_fields(file, files)
    if content is not MISSING:
        payload["content"] = content
    if tts is not MISSING:
        payload["tts"] = tts
    if embeds:
        payload["embeds"] = [embed.to_dict() for embed in embeds]
    if view is not MISSING:
        payload["components"] = view.components if view else []
    if files:
        payload["attachments"] = [
            {
                "id": i,
                "filename": file.name,
                "ephemeral": file.spoiler,
                "description": file.description,
            }
            for i, file in enumerate(files)
        ]
    if suppress_embeds is not MISSING:
        payload["flags"] = 1 << 2

    return payload
