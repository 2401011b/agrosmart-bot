from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

# Bosqichlar (steps)
FULLNAME, ADDRESS, PHONE, SHOW_CARD = range(4)

CARD_NUMBER = "9860 3501 42542645"  # To'lov uchun karta raqami
BOT_OWNER_ID = 8033582534  # Bot egasining Telegram user IDsi

# /start bosilganda boshlanadi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Iltimos, ismingiz va familiyangizni to‘liq yozing:")
    return FULLNAME

# Foydalanuvchi ism familiyasini yozganda
async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fullname'] = update.message.text
    await update.message.reply_text("Yashash manzilingizni yozing (viloyat, shahar/tuman):")
    return ADDRESS

# Foydalanuvchi manzilini yozganda
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return PHONE

# Telefon raqami qabul qilinganda
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text

    # Karta raqamini ko‘rsatamiz va tugma beramiz
    keyboard = [[InlineKeyboardButton("\u2705 To‘lov qildim", callback_data="payment_done")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"To‘lovni quyidagi karta raqamiga amalga oshiring:\n\n"
        f"{CARD_NUMBER}\n\n"
        "To‘lovni amalga oshirgach, quyidagi tugmani bosing:",
        reply_markup=reply_markup
    )
    return SHOW_CARD

# "To‘lov qildim" tugmasi bosilganda
async def payment_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Iltimos, to‘lov chekini rasm yoki fayl ko‘rinishida yuboring:")
    return ConversationHandler.END

# Chekni qabul qilish va bot egasiga yuborish
async def payment_proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_info = (
        f"Yangi to‘lov chek yuborildi:\n"
        f"Ism: {user_data.get('fullname', 'Nomaʼlum')}\n"
        f"Manzil: {user_data.get('address', 'Nomaʼlum')}\n"
        f"Telefon: {user_data.get('phone', 'Nomaʼlum')}\n"
        f"Foydalanuvchi: @{update.message.from_user.username or 'username yoʻq'}"
    )

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await update.message.reply_text("To‘lov chek rasm sifatida qabul qilindi. Rahmat!")
        await context.bot.send_photo(chat_id=BOT_OWNER_ID, photo=photo, caption=user_info)
    elif update.message.document:
        document = update.message.document.file_id
        await update.message.reply_text("To‘lov chek fayl sifatida qabul qilindi. Rahmat!")
        await context.bot.send_document(chat_id=BOT_OWNER_ID, document=document, caption=user_info)
    else:
        await update.message.reply_text("Iltimos, to‘lov chekini rasm yoki fayl sifatida yuboring.")

# Bekor qilish komandasi
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

# /myid komandasi — foydalanuvchining Telegram ID sini ko‘rsatadi
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Sizning Telegram IDingiz: {user_id}")

# Botni ishga tushurish
if __name__ == '__main__':
    app = ApplicationBuilder().token("8059073711:AAH864DPS3kiWoUo3qStunbQ5YSCYiyB4ww").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SHOW_CARD: [CallbackQueryHandler(payment_done_callback, pattern="^payment_done$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, payment_proof_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

