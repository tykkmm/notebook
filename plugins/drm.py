from fileinput import filename
from pyrogram import filters, Client as ace
from main import LOGGER, prefixes
from pyrogram.types import Message
from main import Config
import os
import subprocess
import tgcrypto
import shutil
import sys
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient


@ace.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("drm", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/THUMB/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    inputData = await bot.ask(m.chat.id, "**Send**\n\nMPD\nNAME\nQUALITY\nCAPTION")
    mpd, raw_name, Q, CP = inputData.text.split("\n")
    name = f"{TgClient.parse_name(raw_name)} ({Q}p)"
    print(mpd, name, Q)

    keys = ""
    inputKeys = await bot.ask(m.chat.id, "**Send Key**")
    keys = inputKeys.text
    print(keys)

    BOT = TgClient(bot, m, path)
    Thumb = await BOT.thumb()
    prog  = await bot.send_message(m.chat.id, f"**Downloading Drm Video!** - [{name}]({mpd})")

#    cmd1 = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo.{resl}/bestvideo.2/bestvideo" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
    cmd1 = f'yt-dlp -k --allow-unplayable-formats -f "bestvideo.3/bestvideo.2/bestvideo" --fixup never "{mpd}" --external-downloader aria2c --external-downloader-args "-x 16 -s 16 -k 1M" -o "{path}/{name}.mp4" --exec echo'
    cmd2 = f'yt-dlp -k --allow-unplayable-formats -f ba --fixup never "{mpd}" --external-downloader aria2c --external-downloader-args "-x 16 -s 16 -k 1M" -o "{path}/{name}.m4a" --exec echo'
    os.system(cmd1)
    os.system(cmd2)
    avDir = os.listdir(path)
    print(avDir)
    print("Decrypting")
    
    cmd3 = f'mp4decrypt --key {keys} --show-progress "{path}/{name}.mp4" "{path}/video.mp4"'
    os.system(cmd3)
    os.remove(f'{path}/{name}.mp4')
    cmd4 = f'mp4decrypt --key {keys} --show-progress "{path}/{name}.m4a" "{path}/audio.m4a"'
    os.system(cmd4)
    os.remove(f'{path}/{name}.m4a')
    
    cmd5 = f'ffmpeg -i "{path}/video.mp4" -i "{path}/audio.m4a" -c copy "{path}/{name}.mp4"'
    os.system(cmd5)
    os.remove(f"{path}/video.mp4")
    os.remove(f"{path}/audio.m4a")
    filename = f"{path}/{name}.mp4"
    cc = f"{name}.mp4\n\n**Description:-**\n{CP}"
        # await DownUP.sendVideo(bot, m, filename, cc, Thumb, name, prog, path)
    UL = Upload_to_Tg(bot=bot, m=m, file_path=filename, name=name,
                            Thumb=Thumb, path=path, show_msg=prog, caption=cc)
    await UL.upload_video()
    print("Done")
    await prog.delete(True)

    if os.path.exists(tPath):
        shutil.rmtree(tPath)
    shutil.rmtree(path)
    await m.reply_text("Done")
