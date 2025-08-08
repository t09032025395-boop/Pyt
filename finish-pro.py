import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7956549242:AAE5j8LGRJw6Uj3PCtFaEfdrKDRAwSZoTTI'

# لیست کاربران انتخاب شده بر اساس user_id
selected_users = set()

# کلمات پاسخ ربات
responses = [
    "کص ننت",
    "ننه کون تاقار",
    "ننه پلنگ",
    "ننت از افق کوروش بیشتر مشتری داره",
    "ننه هفتی",
    "ننه اوب نژاد",
    "کیریم تو تمام نژادت",
    "نسلتو گاییدم",
    "نسل و نسبت و گاییدم",
    "ننه کص زیبا",
    "ننه بیوتیفول"
]

async def is_user_admin(update: Update, user_id: int) -> bool:
    """بررسی می‌کند آیا کاربر ادمین گروه است یا خیر"""
    chat = update.effective_chat
    if chat.type not in ['group', 'supergroup']:
        return False
    admins = await update.effective_chat.get_administrators()
    return any(admin.user.id == user_id for admin in admins)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر پیام ریپلای به کسی بود و متن this is بود، آن کاربر را به لیست اضافه می‌کند"""
    if not update.message.reply_to_message or not update.message.text:
        return
    user_id = update.message.from_user.id
    if not await is_user_admin(update, user_id):
        return
    if update.message.text.strip().lower() == "this is":
        target_user_id = update.message.reply_to_message.from_user.id
        selected_users.add(target_user_id)
        await update.message.reply_text("کاربر به لیست اضافه شد.")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر پیام ریپلای به کسی بود و متن this is not بود، آن کاربر را از لیست حذف می‌کند"""
    if not update.message.reply_to_message or not update.message.text:
        return
    user_id = update.message.from_user.id
    if not await is_user_admin(update, user_id):
        return
    if update.message.text.strip().lower() == "this is not":
        target_user_id = update.message.reply_to_message.from_user.id
        if target_user_id in selected_users:
            selected_users.remove(target_user_id)
            await update.message.reply_text("کاربر از لیست حذف شد.")

async def respond_to_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر پیام ارسال شده توسط کاربری است که در لیست است جواب مناسبی ارسال می‌کند."""
    user_id = update.message.from_user.id
    if user_id in selected_users:
        response = random.choice(responses)
        await update.message.reply_text(response)

async def send_multiple_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر کاربر روی یک نفر ریپلای کند و یک متن با تعداد بنویسد، ربات به همان تعداد پیام ارسال می‌کند."""
    if not update.message.reply_to_message or not update.message.text:
        return
    parts = update.message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return
    count = int(parts[1])
    message_text = parts[0]
    
    for _ in range(count):
        await update.message.reply_text(message_text)

async def allow_user_if_admin_replied(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر ادمین روی یک کاربر عادی ریپلای کند و متن apply را بنویسد، آن کاربر هم می‌تواند از ربات استفاده کند."""
    if not update.message.reply_to_message or not update.message.text:
        return
    user_id = update.message.from_user.id
    if await is_user_admin(update, user_id) and update.message.text.strip().lower() == "apply":
        target_user_id = update.message.reply_to_message.from_user.id
        selected_users.add(target_user_id)
        await update.message.reply_text("کاربر به لیست اضافه شد و می‌تواند از ربات استفاده کند.")

async def not_apply_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """اگر ادمین روی یک کاربر عادی ریپلای کند و متن not apply را بنویسد، آن کاربر از لیست حذف می‌شود."""
    if not update.message.reply_to_message or not update.message.text:
        return
    user_id = update.message.from_user.id
    if await is_user_admin(update, user_id) and update.message.text.strip().lower() == "not apply":
        target_user_id = update.message.reply_to_message.from_user.id
        if target_user_id in selected_users:
            selected_users.remove(target_user_id)
            await update.message.reply_text("کاربر از لیست حذف شد و نمی‌تواند از ربات استفاده کند.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("ربات فعال شد و منتظر دستورات شماست.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # handler برای add_user با فیلتر خاص
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & filters.Regex('^this is$'), add_user))
    # handler برای remove_user با فیلتر خاص
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & filters.Regex('^this is not$'), remove_user))
    # handler برای ارسال پیام‌های متعدد
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, send_multiple_messages))
    # handler برای اجازه دادن به کاربر عادی اگر ادمین روی او ریپلای کند
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & filters.Regex('^apply$'), allow_user_if_admin_replied))
    # handler برای حذف کاربر از لیست با دستور not apply
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY & filters.Regex('^not apply$'), not_apply_user))

    # handler برای پاسخ به پیام کاربران اضافه شده در لیست
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_selected))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
