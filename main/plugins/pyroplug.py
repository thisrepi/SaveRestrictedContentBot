# Github.com/Vasusen-code

import asyncio, time, os

from .. import Bot, bot
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot
from telethon.tl.types import DocumentAttributeVideo

from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, FloodWait
from ethon.pyfunc import video_metadata
from telethon import events

def thumbnail(sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    else:
         return None
      
async def check(userbot, client, link):
    msg_id = 0
    try:
        msg_id = int(link.split("/")[-1])
    except ValueError:
        if '?single' in link:
            link_ = link.split("?single")[0]
            msg_id = int(link_.split("/")[-1])
        else:
            return False, "**Invalid Link!**"
    if 't.me/c/' in link:
        try:
            chat = int('-100' + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except ValueError:
            return False, "**Invalid Link!**"
        except Exception:
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception:
            return False, "Maybe bot is banned from the chat, or your link is invalid!"
            
async def get_msg(userbot, client, sender, edit_id, msg_link, i, bulk=False):
    edit = ""
    chat = ""
    msg_id = 0
    try:
        msg_id = int(msg_link.split("/")[-1])
    except ValueError:
        if '?single' in msg_link:
            link_ = msg_link.split("?single")[0]
            msg_id = int(link_.split("/")[-1])
        else:
            await client.edit_message_text(sender, edit_id, "**Invalid Link!**")
            return None
    if 't.me/c/' in msg_link:
        chat = int('-100' + str(msg_link.split("/")[-2]))
        file = ""
        try:
            msg = await userbot.get_messages(chat, msg_id)
            if msg.media:
                if 'web_page' in msg.media:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return None
            if not msg.media:
                if msg.text:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(sender, msg.text.markdown)
                    await edit.delete()
                    return None
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            file = await userbot.download_media(
                msg,
                progress=progress_for_pyrogram,
                progress_args=(
                    client,
                    "**DOWNLOADING:**\n",
                    edit,
                    time.time()
                )
            )
            await edit.edit('Preparing to Upload!')
            caption = str(file)
            if msg.caption is not None:
                caption = msg.caption
            if str(file).split(".")[-1] in ['mkv', 'mp4', 'webm', 'mpe4', 'mpeg']:
                if str(file).split(".")[-1] in ['webm', 'mkv', 'mpe4', 'mpeg']:
                    path = str(file).split(".")[0] + ".mp4"
                    os.rename(file, path) 
                    file = str(file).split(".")[0] + ".mp4"
                data = video_metadata(file)
                duration = data["duration"]
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                await userbot.send_video(
                    chat_id=sender,
                    video=file,
                    caption=caption,
                    supports_streaming=True,
                    duration=duration,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            elif str(file).split(".")[-1] in ['jpg', 'jpeg', 'png', 'webp']:
                await edit.edit("Uploading photo.")
                await bot.send_file(sender, file, caption=caption)
            else:
                thumb_path=thumbnail(sender)
                await userbot.send_document(
                    sender,
                    file, 
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            os.remove(file)
            await edit.delete()
            return None
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Have you joined the channel?")
            return None
        except FloodWait as fw:
            print(fw)
            if bulk is True:
                return int(fw.x) + 5
            else:
                await client.edit_message_text(sender, edit_id, f'Try again after {fw.x} seconds due to floodwait from telegram.')
                return None
        except Exception as e:
            print(e)
            await client.edit_message_text(sender, edit_id, f'Failed to save: `{e}`')
            if os.path.isfile(file) == True:
                os.remove(file)
            return None
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat =  msg_link.split("/")[-2]
        try:
            await client.copy_message(int(sender), chat, msg_id)
        except FloodWait as fw:
            print(fw)
            if bulk is True:
                return int(fw.x) + 5
            else:
                await client.edit_message_text(sender, edit_id, f'Try again after {fw.x} seconds due to floodwait from telegram.')
                return None
        except Exception as e:
            print(e)
            await client.edit_message_text(sender, edit_id, f'Failed to save: `{e}`')
            return None
        await edit.delete()
        return None
 
async def get_bulk_msg(userbot, client, sender, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    if 't.me' in link:
        if not 't.me/c/' in link:
            chat =  link.split("/")[-2]
            msg_id = link.split("/")[-1]
            await x.edit(f'cloning {chat}-{msg_id}')
        if 't.me/c/' in link:
            try:
                chat =  int('-100' + str(link.split("/")[-2]))
                msg_id = int(link.split("/")[-1])
                file = await userbot.get_messages(chat, ids=msg_id)
                if not file:
                    await x.edit("Mesaj Alınamadı!")
                    return
                if file and file.text:
                    try:
                        if not file.media:
                            await x.edit(file.text)
                            return
                        if not file.file.name:
                            await x.edit(file.text)
                            return
                    except:
                        if file.media.webpage:
                            await x.edit(file.text)
                            return
                name = file.file.name
                if not name:
                    if not file.file.mime_type:
                        await x.edit("Dosya İçin Ad Getirilemedi.")
                        return
                    else:
                        if 'mp4' or 'x-matroska' in file.file.mime_type:
                            name = f'{chat}' + '-' + f'{msg_id}' + '.mp4'
                await fast_download(name, file.document, userbot, edit, time.time(), '**İndiriliyor:**')
                await x.edit("Yüklemeye Hazırlanıyor.")
                if 'mp4' in file.file.mime_type:
                    metadata = video_metadata(name)
                    height = metadata["height"]
                    width = metadata["width"]
                    duration = metadata["duration"]
                    attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                    thumb = await screenshot(name, duration/2, event.sender_id)
                    caption = name
                    if file.text:
                        caption=file.text
                    uploader = await fast_upload(name, name, time.time(), event.client, edit, '**Yükleniyor:**')
                    await event.client.send_file(event.chat_id, uploader, caption=caption, thumb=thumb, attributes=attributes, force_document=False)
                    await x.delete()
                    os.remove(name)
                elif 'x-matroska' in file.file.mime_type:
                    metadata = video_metadata(name)
                    height = metadata["height"]
                    width = metadata["width"]
                    duration = metadata["duration"]
                    attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                    thumb = await screenshot(name, duration/2, event.sender_id)
                    caption = name
                    if file.text:
                        caption=file.text
                    uploader = await fast_upload(name, name, time.time(), event.client, edit, '**Yükleniyor:**')
                    await event.client.send_file(event.chat_id, uploader, caption=caption, thumb=thumb, attributes=attributes, force_document=False)
                    await x.delete()
                    os.remove(name)
                else:
                    caption = name
                    if file.text:
                        caption=file.text
                    thumb=None
                    if os.path.exists(f'{event.sender_id}.jpg'):
                        thumb = f'{event.sender_id}.jpg'
                    uploader = await fast_upload(name, name, time.time(), event.client, edit, '**Yükleniyor:**')
                    await event.client.send_file(event.chat_id, uploader, caption=caption, thumb=thumb, force_document=True)
                    await edit.delete()
                    os.remove(name)
            except Exception as e:
                print(e)
                if 'Peer'in str(e):
                    await x.edit("Kanal Bulunamadı, Katıldınız mı?")
                    return
                await x.edit("Başarısız, Tekrar Deneyin!")   
