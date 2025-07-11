import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube_downloader import get_formats, download_audio, download_video

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Welcome to the Downloader Bot!\nSend /youtube <link> to download.")

async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("❌ Please provide a YouTube link.")
            return

        url = context.args[0]
        formats = get_formats(url)

        if not formats:
            await update.message.reply_text("❌ No video/audio formats found.")
            return

        buttons = []
        for fmt in formats:
            label = f"{fmt['type']} {fmt['quality']} ({fmt['ext']}, {fmt['filesize']})"
            buttons.append(label)

        await update.message.reply_text("🎬 Available Formats:\n" + "\n".join(buttons))

        await update.message.reply_text("⏬ Sending best format...")

        # Example: send highest res MP4 or fallback to audio
        for fmt in formats:
            if fmt["type"] == "video" and fmt["ext"] == "mp4":
                file_path = download_video(url, fmt["format_id"])
                await update.message.reply_video(video=open(file_path, "rb"))
                os.remove(file_path)
                return

        # If no video found, try audio
        for fmt in formats:
            if fmt["type"] == "audio":
                file_path = download_audio(url, fmt["format_id"])
                await update.message.reply_audio(audio=open(file_path, "rb"))
                os.remove(file_path)
                return

    except Exception as e:
        print(f"❌ Error in youtube_command: {e}")
        await update.message.reply_text("⚠️ Failed to download. Try again later.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("youtube", youtube_command))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
