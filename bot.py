#    This file is part of the ForveSub distribution (https://github.com/xditya/ForceSub).
#    Copyright (c) 2021 Adiya
#    
#    This program is free software: you can redistribute it and/or modify  
#    it under the terms of the GNU General Public License as published by  
#    the Free Software Foundation, version 3.
# 
#    This program is distributed in the hope that it will be useful, but 
#    WITHOUT ANY WARRANTY; without even the implied warranty of 
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
#    General Public License for more details.
# 
#    License can be found in < https://github.com/xditya/ForceSub/blob/main/License> .

import logging
import asyncio
import string
import random
from telethon.utils import get_display_name
import re
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

appid = apihash = bottoken = None
# start the bot
print("Starting...")
try:
    apiid = config("API_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
    xchannel = config("CHANNEL")
    welcome_msg = config("WELCOME_MSG")
    welcome_not_joined = config("WELCOME_NOT_JOINED")
    on_join = config("ON_JOIN", cast=bool)
    on_new_msg = config("ON_NEW_MSG", cast=bool)
except:
    print("ഏതോ ഒന്നിനെ  കളഞ്ഞു പോയെ 😓.")
    print("ഞാൻ പോണേ...🏃‍♂️")
    exit()

if (apiid != None and apihash!= None and bottoken != None):
    try:
        BotzHub = TelegramClient('BotzHub', apiid, apihash).start(bot_token=bottoken)
    except Exception as e:
        print(f"എന്തോ എവിടെയോ തകരാർ!\n{str(e)}")
        print("ഞാൻ പോണേ...🏃‍♂️")
        exit()
else:
    print("ഏതോ ഒന്നിനെ  കളഞ്ഞു പോയെ 😓.")
    print("ഞാൻ പോണേ...🏃‍♂️")
    exit()

channel = xchannel.replace("@", "")

# join check
async def get_user_join(id):
    ok = True
    try:
        await BotzHub(GetParticipantRequest(channel=channel, participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok


@BotzHub.on(events.ChatAction())
async def _(event):
    if on_join is False:
        return
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        title = chat.title if chat.title else "this chat"
        pp = await BotzHub.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        if last:
            fullname = f"{name} {last}"
        else:
            fullname = name
        uu = user.username
        if uu:
            username = f"@{uu}"
        else:
            username = mention
        x = await get_user_join(user.id)
        if x is True:
            msg = welcome_msg.format(mention=mention, title=title, fullname=fullname, username=username, name=name, last=last, channel=f"@{channel}")
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
        else:
            msg = welcome_not_joined.format(mention=mention, title=title, fullname=fullname, username=username, name=name, last=last, channel=f"@{channel}")
            butt = [Button.url("Channel", url=f"https://t.me/{channel}"), Button.inline("അഴിച്ചു വിട് 🐣", data=f"unmute_{user.id}")]
            await BotzHub.edit_permissions(event.chat.id, user.id, until_date=None, send_messages=False)
        
        await event.reply(msg, buttons=butt)


@BotzHub.on(events.NewMessage(incoming=True))
async def mute_on_msg(event):
    if event.is_private:
        return
    if on_new_msg is False:
        return
    x = await get_user_join(event.sender_id)
    temp = await BotzHub(GetFullUserRequest(event.sender_id))
    if x is False:
        if temp.user.bot:
            return
        nm = temp.user.first_name
        try:
            await BotzHub.edit_permissions(event.chat.id, event.sender_id, until_date=None, send_messages=False)
        except Exception as e:
            print(str(e))
            return
        await event.reply(f"പൂയ് {nm}, നീ നമ്മുടെ ചാനൽ സബ്സ്ക്രൈബ് ചെയ്തട്ടില്ല 🔕. അതില് ജോയിൻ അയേച്ചും വാ 🔔 , എന്നിട്ട് താഴെ അഴിച്ചു വിട് ബട്ടൺ അമർത്തി നോക്ക്.. ഇന്നാ നമ്മുടെ ചാനൽ ലിങ്ക് 🔗 @{channel} ", buttons=[[Button.url("Channel", url=f"https://t.me/{channel}")], [Button.inline("അഴിച്ചു വിട് 🐣", data=f"unmute_{event.sender_id}")]])


@BotzHub.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def _(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid == event.sender_id:
        x = await get_user_join(uid)
        nm = (await BotzHub(GetFullUserRequest(uid))).user.first_name
        if x is False:
            await event.answer(f"എടാ നീ ചാനലിൽ ചേർന്നില്ലെടാ! 🥺 @{channel} ", cache_time=0, alert=True)
        elif x is True:
            try:
                await BotzHub.edit_permissions(event.chat.id, uid, until_date=None, send_messages=True)
            except Exception as e:
                print(str(e))
                return
            msg = f"Welcome to {(await event.get_chat()).title}, {nm}!\nGood to see you here!"
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
            await event.edit(msg, buttons=butt)
    else:
        await event.answer("എടാ നീ  പറഞ്ഞോ നീ നുമ്മടെ സബ്സ്ക്രൈബ്ർ അല്ലെ 🌚", cache_time=0, alert=True)

@BotzHub.on(events.NewMessage(pattern="/start"))
async def strt(event):
    await event.reply(f"ഞാനൊരു പാവം സബ്സ്ക്രൈബ്ർ ബോട്ട്\n 
                      
               
                      𝔰𝔲𝔟𝔰𝔠𝔯𝔦𝔟𝔢𝔯 𝔟𝔬𝔱 🔔
                      
                      ", buttons=[Button.url("പടച്ചവൻ🌱", url=f"https://t.me/slogan_98"), Button.url("നിർമാണ പത്രം📜", url="https://www.google.com/search?q=ente+kayyil+onnula")])

    
print("എന്റെ ഹൃദയം നിനക്കായ്‌ തുടിക്കുന്നു...!")
BotzHub.run_until_disconnected()
