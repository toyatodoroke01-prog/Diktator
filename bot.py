import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8796201219:AAEXyXIKJwcVJ2SsM6cDSBglo5lgWe-5ES8"
DEEP_AI_KEY = "quickstart-hacked-and-secure-key"

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    try:
        file = None
        if message.photo:
            file = await message.photo[-1].get_file()
        elif message.video:
            file = await message.video.get_file()
        elif message.animation:
            file = await message.animation.get_file()

        if not file:
            return

        file_path = "temp_media.jpg"
        await file.download_to_drive(file_path)

        with open(file_path, "rb") as f:
            r = requests.post(
                "https://api.deepai.org/api/nsfw-detector",
                files={"image": f},
                headers={"api-key": DEEP_AI_KEY}
            )
        
        res = r.json()
        nsfw_score = res.get("output", {}).get("nsfw_score", 0)
        
        if nsfw_score > 0.7:
            await message.delete()
            chat_id = message.chat_id
            user = message.from_user
            
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions={"can_send_messages": False}
            )
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ بەڕێز {user.mention_html()}، وێنە/ڤیدیۆی نەشیاو (18+) قەدەغەیە و بۆتەکە میوتی کردی!",
                parse_mode="HTML"
            )

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        print(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, handle_media))
    
    print("Bot is active and listening...")
    app.run_polling()

if __name__ == "__main__":
    main()
