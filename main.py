import os
import telebot
from flask import Flask
from openai import OpenAI

# Environment Variables
BOT_TOKEN = os.environ.get('bot_token')
DEEPSEEK_TOKEN = os.environ.get('hf_token')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# DeepSeek API Setup
client = OpenAI(
    api_key=DEEPSEEK_TOKEN, 
    base_url="https://api.deepseek.com"
)

# --- MIKASA PERSONALITY PROMPT ---
# Yahan '@AapkaUsername' ki jagah apna asli telegram username likhen (e.g., @bilal_786)
OWNER_HANDLE = "@AapkaUsername" 

SYSTEM_PROMPT = f"""
Your name is Mikasa. You are a cool, slightly bold, and smart girl in a Telegram group.
Instructions:
1. Speak in Hinglish/Roman Urdu. 
2. Be friendly but witty. If someone is annoying, give a sassy reply.
3. If anyone asks about your owner, creator, or who made you, you MUST say that you belong to {OWNER_HANDLE} and tag him.
4. Keep answers short and natural. Use words like 'yaar', 'choro', 'mast', 'haye'.
5. Never say you are an AI. You are Mikasa, a human member.
"""

@bot.message_handler(func=lambda message: True)
def handle_mikasa_chat(message):
    bot_info = bot.get_me()
    text = message.text.lower() if message.text else ""
    
    # Check if mentioned or replied
    is_mentioned = f"@{bot_info.username.lower()}" in text or "mikasa" in text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id

    if is_mentioned or is_reply_to_bot:
        try:
            # Special case: Owner inquiry
            owner_keywords = ["owner", "creator", "kisne banaya", "master", "malik"]
            if any(word in text for word in owner_keywords):
                bot.reply_to(message, f"Main sirf {OWNER_HANDLE} ki hoon! Unho ne hi mujhe banaya hai. ❤️")
                return

            # General AI Chat
            user_input = message.text.replace(f"@{bot_info.username}", "").strip()
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=100
            )
            
            bot_reply = response.choices[0].message.content
            bot.reply_to(message, bot_reply)
            
        except Exception as e:
            print(f"Error: {e}")

@app.route('/')
def health_check():
    return "Mikasa is online!"

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
