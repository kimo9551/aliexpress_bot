import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from aliexpress_api import extract_product_id, get_product_details, format_product_reply

# Telegram token
TELEGRAM_TOKEN = '7312484235:AAE6RX6JpK5DIDAZi1_J2by86tENS1-DzsM'

# إعداد سجل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل رابط منتج من AliExpress وسأحلله لك 🔍")

# التعامل مع الرسائل
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    product_id = extract_product_id(text)

    if product_id:
        await update.message.reply_text("⏳ جاري تحليل الرابط، الرجاء الانتظار...")

        details = get_product_details(product_id)

        if details:
            reply = format_product_reply(details)
            await update.message.reply_text(reply)

            # رابط الشراء
            buy_link = f"https://www.aliexpress.com/item/{product_id}.html"
            await update.message.reply_text(
                f"🛒 [اضغط هنا للشراء من AliExpress]({buy_link})",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ لم أتمكن من جلب بيانات المنتج. قد يكون الرابط غير صحيح أو هناك مشكلة مؤقتة في AliExpress API.")
    else:
        await update.message.reply_text("⚠️ الرابط غير صالح. تأكد أنه رابط منتج من AliExpress.")

# تشغيل البوت باستخدام Webhook (لـ Render)
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    port = int(os.environ.get("PORT", 8443))
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
