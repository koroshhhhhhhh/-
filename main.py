"""SoundCloud Telegram bot - entry point and settings.

Edit the settings below (or set the same names as environment variables on Railway).
"""
import asyncio
import logging
import os
import shutil
import subprocess
import sys
import tempfile

# =========================== SETTINGS ===========================
BOT_TOKEN = "8967532142:AAETFSGENeEvSPJxHqhMDFvvQhkYLx02rjQ"                           # <- put your bot token here (from @BotFather)

MAX_CONCURRENT_JOBS = 3                  # downloads running at the same time (the rest wait in a queue)
MAX_JOBS_PER_USER = 2                    # active downloads allowed per user
MAX_PLAYLIST_TRACKS = 0                  # 0 = no limit (private chats)
MAX_PLAYLIST_TRACKS_GROUP = 0            # 0 = no limit (groups)
MAX_FILE_MB = 49                         # Telegram Bot API upload limit is 50 MB
BOT_API_URL = ""                         # optional self-hosted Bot API server (then set MAX_FILE_MB up to ~1900)
INSTAGRAM_COOKIES_FILE = ""                # path to a Netscape cookies.txt of an Instagram account (needed for stories and many posts)
AUTO_UPDATE_YTDLP = True                 # upgrade yt-dlp to the latest version on every start
LOG_LEVEL = "INFO"
# ================================================================


def update_ytdlp() -> None:
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "--quiet",
             "--disable-pip-version-check", "yt-dlp[default]", "gallery-dl"],
            timeout=180, check=False,
        )
    except Exception as exc:  # the bot still works with the version baked into the image
        logging.getLogger("main").warning("yt-dlp update skipped: %s", exc)


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", LOG_LEVEL).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    token = (BOT_TOKEN or os.getenv("BOT_TOKEN") or "").strip()  # main.py first, env var as fallback
    if not token:
        sys.exit("Bot token is empty: write it in BOT_TOKEN at the top of main.py.")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg was not found in PATH.")

    if AUTO_UPDATE_YTDLP:
        update_ytdlp()

    cookies = os.getenv("INSTAGRAM_COOKIES_FILE") or INSTAGRAM_COOKIES_FILE
    cookies_text = os.getenv("INSTAGRAM_COOKIES")  # alternative: paste the file content in a variable
    if cookies_text:
        cookies = os.path.join(tempfile.gettempdir(), "ig_cookies.txt")
        with open(cookies, "w", encoding="utf-8") as f:
            f.write(cookies_text.replace("\\n", "\n"))
    if cookies and not os.path.isfile(cookies):
        logging.getLogger("main").warning("Instagram cookies file not found: %s", cookies)
        cookies = ""

    from bot import Settings, run  # imported after the update so the new yt-dlp is used

    asyncio.run(run(Settings(
        token=token,
        max_concurrent_jobs=MAX_CONCURRENT_JOBS,
        max_jobs_per_user=MAX_JOBS_PER_USER,
        max_file_mb=MAX_FILE_MB,
        bot_api_url=BOT_API_URL,
        max_playlist_tracks=MAX_PLAYLIST_TRACKS,
        max_playlist_tracks_group=MAX_PLAYLIST_TRACKS_GROUP,
        instagram_cookies=cookies or "",
    )))


if __name__ == "__main__":
    main()
