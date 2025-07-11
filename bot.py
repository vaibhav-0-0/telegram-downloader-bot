import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from youtube_downloader import get_formats, download_audio, download_video

BOT_TOKEN = "8031548324:AAGf9tjY6LqavlWIJqlZas1IneKP3PdHIBE"

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send `/youtube <link>` to download video or MP3.", parse_mode="Markdown")


async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    parts = msg.split()

    if len(parts) < 2:
        await update.message.reply_text("❗ Please provide a YouTube link.\n\nExample:\n`/youtube https://youtu.be/abc123`", parse_mode="Markdown")
        return

    url = parts[1].strip()
    context.user_data["video_url"] = url

    formats = get_formats(url)
    if not formats:
        await update.message.reply_text("⚠️ No supported video formats found.")
        return

    buttons = []
    added = set()

    for f in formats:
        size_mb = round((f['filesize'] or 0) / (1024 * 1024), 1)
        label = f"{f['resolution']} ({f['ext']}) ~ {size_mb}MB"

        if label not in added:
            buttons.append([InlineKeyboardButton(label, callback_data=f"{f['format_id']}")])
            added.add(label)

    buttons.append([InlineKeyboardButton("🎵 MP3", callback_data="mp3")])
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("📥 Choose format to download:", reply_markup=reply_markup)


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    format_id = query.data
    url = context.user_data.get("video_url")

    if not url:
        await query.edit_message_text("⚠️ Session expired. Send `/youtube <link>` again.", parse_mode="Markdown")
        return

    await query.edit_message_text("⏬ Downloading... Please wait...")

    user_id = query.from_user.id
    output_name = f"file_{user_id}"

    if format_id == "mp3":
        filepath = download_audio(url, output_name=output_name)
    else:
        filepath = download_video(url, format_id, output_name=output_name)

    if not filepath or not os.path.exists(filepath):
        await context.bot.send_message(chat_id=user_id, text="❌ Failed to download file.")
        return

    try:
        if filepath.endswith(".mp3"):
            await context.bot.send_audio(chat_id=user_id, audio=open(filepath, "rb"))
        else:
            await context.bot.send_video(chat_id=user_id, video=open(filepath, "rb"), supports_streaming=True)
    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"⚠️ Error sending file: {e}")

    # Clean up downloaded file
    try:
        os.remove(filepath)
    except:
        pass

    # Clear stored link
    context.user_data.pop("video_url", None)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
