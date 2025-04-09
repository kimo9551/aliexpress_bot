# bot.py

import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from aliexpress_api import extract_product_id, get_aliexpress_product_details

TELEGRAM_TOKEN = '7312484235:AAE6RX6JpK5DIDAZi1_J2by86tENS1-DzsM'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط منتج من AliExpress لتحليله.")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    product_id = extract_product_id(text)
    if product_id:
        await update.message.reply_text("⏳ يتم تحليل الرابط...")
        data = get_aliexpress_product_details(product_id)
        if data and 'result' in data:
            result = data['result']
            msg = f"""
📣 سعر المنتج بدون تخفيض: {result.get('originalPrice', 'غير متوفر')}$
💵 سعر التخفيض بالعملات: {result.get('salePrice', 'غير متوفر')}$
💵 سعر السوبر ديلز: {result.get('targetSalePrice', 'غير متوفر')}$
💵 سعر العرض المحدود: {result.get('discount', 'غير متوفر')}$
💵 سعر التخفيض المحتمل: {result.get('discount', 'غير متوفر')}$

🛍 نسبة التخفيض بالعملات: {result.get('discount', 'غير متوفر')}%
🏪 اسم المتجر: {result.get('shopName', 'غير متوفر')}
🌟 التقييم الإيجابي للمتجر: {result.get('shopPositiveRate', 'غير متوفر')}%
✈️ شركة الشحن: {result.get('shippingService', 'غير متوفر')}
✈️ عمولة الشحن: {result.get('freight', 'غير متوفر')}$
            """
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("⚠️ لم أتمكن من جلب بيانات المنتج.")
    else:
        await update.message.reply_text("⚠️ الرابط غير صحيح. تأكد من إرساله من AliExpress.")


async def main():
    # إعداد البوت
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # إعداد Webhook لـ Render
    port = int(os.environ.get("PORT", 8443))
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"

    await app.start()
    await app.bot.set_webhook(webhook_url)
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="",
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
