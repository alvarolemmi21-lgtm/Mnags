import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from openai import OpenAI

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

STYLE = "anime manga style, cinematic lighting, detailed panels"

async def chapter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    story = " ".join(context.args)

    if not story:
        await update.message.reply_text("Use: /chapter your story")
        return

    await update.message.reply_text("Generating manga page... 📖🔥")

    result = client.images.generate(
        model="gpt-image-1",
        prompt=f"{story}, {STYLE}, manga page with multiple panels",
        size="1024x1024"
    )

    image_url = result.data[0].url
    await update.message.reply_photo(photo=image_url)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("chapter", chapter))

    app.run_polling()

if __name__ == "__main__":
    main()
