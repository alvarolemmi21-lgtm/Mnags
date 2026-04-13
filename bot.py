import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from openai import OpenAI

# ENV VARIABLES (Railway will provide these)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

STYLE_LIBRARY = {
    "anime": "anime style, detailed, cinematic lighting",
    "hero": "hero action manga style, dynamic poses, intense shading",
    "dark": "dark manga style, heavy shadows, dramatic mood",
    "cyber": "cyberpunk manga style, neon lights, futuristic city",
}

user_memory = {}

# ---------------- STORY BREAKDOWN ----------------
def build_chapter_plan(story):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Break into 4-6 manga pages. Label them Page 1, Page 2, etc."},
            {"role": "user", "content": story}
        ]
    )
    return res.choices[0].message.content


# ---------------- CHARACTER MEMORY ----------------
def get_or_create_character(user_id, story):
    if user_id in user_memory:
        return user_memory[user_id]

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Describe ONE main character (appearance, outfit, vibe)."},
            {"role": "user", "content": story}
        ]
    )

    character = res.choices[0].message.content
    user_memory[user_id] = character
    return character


# ---------------- PAGE PROMPT ----------------
def build_page_prompt(page_text, character, style):
    return f"""
Create a manga page with multiple panels.

MAIN CHARACTER:
{character}

PAGE:
{page_text}

STYLE:
{style}

Rules:
- 4 to 8 panels
- manga layout with borders
- expressive faces
- cinematic composition
"""


# ---------------- COMMAND ----------------
async def chapter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    story = " ".join(context.args)

    if not story:
        await update.message.reply_text("Use: /chapter your story")
        return

    await update.message.reply_text("Creating your manga chapter... 📖🔥")

    style = STYLE_LIBRARY["hero"]

    character = get_or_create_character(user_id, story)
    chapter_plan = build_chapter_plan(story)

    pages = chapter_plan.split("Page")

    for i, page in enumerate(pages[1:], start=1):
        prompt = build_page_prompt(page, character, style)

        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_url = result.data[0].url
        await update.message.reply_photo(photo=image_url, caption=f"Page {i}")


# ---------------- START ----------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("chapter", chapter))
    app.run_polling()


if __name__ == "__main__":
    main()
