#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.
import asyncio

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from config import BANNED_USERS, MUSIC_BOT_NAME, adminlist, lyrical
from strings import get_command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import db
from YukkiMusic.utils.database import get_authuser_names, get_cmode
from YukkiMusic.utils.decorators import (ActualAdminCB, AdminActual,
                                         language)
from YukkiMusic.utils.formatters import alpha_to_int

### Multi-Lang Commands
RELOAD_COMMAND = get_command("RELOAD_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")
KOMUTLAR_COMMAND = get_command("KOMUTLAR_COMMAND")


@app.on_message(
    filters.command(RELOAD_COMMAND)
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id
        admins = await app.get_chat_members(
            chat_id, filter="administrators"
        )
        authusers = await get_authuser_names(chat_id)
        adminlist[chat_id] = []
        for user in admins:
            if user.can_manage_voice_chats:
                adminlist[chat_id].append(user.user.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[chat_id].append(user_id)
        await message.reply_text(_["admin_20"])
    except:
        await message.reply_text(
            "Admin Listesi yeniden yüklenemedi. Bot'un sohbetinizde yönetici olduğundan emin olun."
        )


@app.on_message(
    filters.command(RESTART_COMMAND)
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(
        f"Lütfen bekleyiniz. {MUSIC_BOT_NAME} Yeniden Başlatılıyor.."
    )
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await Yukki.stop_stream(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            await app.get_chat(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await Yukki.stop_stream(chat_id)
        except:
            pass
    return await mystic.edit_text(
        "Başarıyla yeniden başlatıldı.Tekrardan Kullanabilirsiniz.."
    )


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(
    filters.regex("stop_downloading") & ~BANNED_USERS
)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.message_id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer(
            "İndirme zaten Tamamlandı.", show_alert=True
        )
    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            "İndirme zaten Tamamlandı veya İptal Edildi.",
            show_alert=True,
        )
    if not task.done():
        try:
            task.cancel()
            try:
                lyrical.pop(message_id)
            except:
                pass
            await CallbackQuery.answer(
                "İndirme İptal Edildi", show_alert=True
            )
            return await CallbackQuery.edit_message_text(
                f"İndirme Tarafından {CallbackQuery.from_user.mention} İptal Edildi"
            )
        except:
            return await CallbackQuery.answer(
                "İndirme durdurulamadı.", show_alert=True
            )
    await CallbackQuery.answer(
        "Çalışan görev tanınmadı", show_alert=True
    )

@app.on_message(
    filters.command(KOMUTLAR_COMMAND)
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)    
async def mesaj(client, message: Message):
  await message.reply("Botun Komutları:\n\n➥ /oynat - Şarkı oynatır.\n\n✦ /oynat komutu aynı zamanda canlı yayında destekler.(örnek: /oynat kralfm canlı)\n\n➥ /vplay - Video Oynatır.\n✦ /vplay komutu aynı zamanda canlı yayınıda destekler.(örnek: /vplay kralfm canlı)\n➥ /devam - Akışı devam ettirir.\n➥ /durdur - Akışı duraklatır.\n➥ /son - Akışı Sonlandırır.\n➥ /atla - Diğer parça ya atlar.\n✦ atla komutu aynı zamanda sıraya aldığınız istediğiniz parçaya atlar.( Örnek : /atla 3 -  3. Parçaya atlar )\n\n➥ /ilerial - Oynatılan parçayı ileri alır.\n✦(örneğin: /ilerial 30 - parçayı 30 saniye ileri alır)\n\n➥ /gerial - Oynatılan parçayı geri alır.\n✦(örneğin: /gerial 30 - parçayı 30 saniye geriye alır)\n\n➥ /karistir - Sıraya alınan Parçaları karışık oynatır.\n➥ /tekrarla - oynatılan parçayı istediğiniz kadar tekrar eder.\n✦(örneğin: /tekrarla 4 - Parçayı 4 kez tekrarlar.)\n\n➥/bul {şarkı - video ismi veya linki} - komutunu kullanarak şarkı veya video indirebilirsiniz. Ve ayrıca kalitesini seçerek:)\n\n➥ /yetkiver - Grubunuzda yetkisiz üyeye yetki vererek botu kullandırabilirsiz.\n➥ /yetkial - Grubunuzdaki botu kullanan yetkisiz üyeden bot yetkisini alır.\n➥ /yetkilistesi - Komutunu kullanarak Bottan yetkili olan üyelerinizi Görebilirsiniz.\n➥ /oynatmodu - Botun kullanım ayarlarını yapabilirsiniz.\n➥ /restart - komutunu kullanarak admin listenizi güncelleyebilirsiniz.")
