"""
Telegram bot implementation using Aiogram 3.
"""
import os
import django
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leads_management.settings')
django.setup()

from django.conf import settings
from leads.models import Lead, Seller
from kpi.models import SellerKPISummary
from datetime import datetime, timedelta


# States for bot interactions
class LeadStates(StatesGroup):
    waiting_for_status_update = State()


# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def get_seller_by_telegram_id(telegram_id: int):
    """Get seller by Telegram ID."""
    try:
        return Seller.objects.get(telegram_id=telegram_id, is_active=True)
    except Seller.DoesNotExist:
        return None


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    seller = get_seller_by_telegram_id(message.from_user.id)
    
    if not seller:
        await message.answer(
            "❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz. "
            "Kirish uchun administratoringiz bilan bog'laning."
        )
        return
    
    welcome_text = (
        f"👋 Xush kelibsiz, {seller.user.get_full_name() or seller.user.username}!\n\n"
        "📊 Lidlar Boshqaruvi Boti\n\n"
        "Mavjud buyruqlar:\n"
        "/leads - Lidlaringizni ko'rish\n"
        "/new_leads - Yangi lidlarni ko'rish\n"
        "/stats - Statistikaningizni ko'rish\n"
        "/kpi - KPI xulosangizni ko'rish\n"
        "/help - Yordam xabarni ko'rsatish"
    )
    await message.answer(welcome_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = (
        "📋 Mavjud Buyruqlar:\n\n"
        "/start - Botni ishga tushirish\n"
        "/leads - Barcha lidlaringizni ko'rish\n"
        "/new_leads - Faqat yangi lidlarni ko'rish\n"
        "/stats - Statistikaningizni ko'rish\n"
        "/kpi - KPI xulosangizni ko'rish\n"
        "/help - Yordam xabarni ko'rsatish\n\n"
        "Lid holatini yangilash uchun lid ustiga bosing."
    )
    await message.answer(help_text)


@dp.message(Command("leads"))
async def cmd_leads(message: Message):
    """Show seller's leads."""
    seller = get_seller_by_telegram_id(message.from_user.id)
    
    if not seller:
        await message.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    leads = Lead.objects.filter(seller=seller).order_by('-created_at')[:20]
    
    if not leads.exists():
        await message.answer("📭 Sizda hali lidlar yo'q.")
        return
    
    text = f"📋 Sizning Lidlaringiz ({leads.count()} ko'rsatilgan):\n\n"
    
    for lead in leads:
        status_emoji = {
            'new': '🆕',
            'contacted': '📞',
            'qualified': '✅',
            'converted': '💰',
            'lost': '❌',
        }.get(lead.status, '📄')
        
        text += (
            f"{status_emoji} <b>{lead.name}</b>\n"
            f"Holat: {lead.get_status_display()}\n"
        )
        if lead.phone:
            text += f"Telefon: {lead.phone}\n"
        if lead.email:
            text += f"Email: {lead.email}\n"
        text += f"Yaratilgan: {lead.created_at.strftime('%Y-%m-%d')}\n\n"
    
    # Create inline keyboard for lead actions
    keyboard = []
    for lead in leads[:10]:  # Limit to 10 buttons
        keyboard.append([
            InlineKeyboardButton(
                text=f"{lead.name[:20]}...",
                callback_data=f"lead_{lead.id}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
    
    await message.answer(text, parse_mode='HTML', reply_markup=reply_markup)


@dp.message(Command("new_leads"))
async def cmd_new_leads(message: Message):
    """Show seller's new leads."""
    seller = get_seller_by_telegram_id(message.from_user.id)
    
    if not seller:
        await message.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    leads = Lead.objects.filter(seller=seller, status='new').order_by('-created_at')[:20]
    
    if not leads.exists():
        await message.answer("✅ Sizda yangi lidlar yo'q. Ajoyib ish!")
        return
    
    text = f"🆕 Yangi Lidlar ({leads.count()}):\n\n"
    
    for lead in leads:
        text += (
            f"<b>{lead.name}</b>\n"
        )
        if lead.phone:
            text += f"📞 {lead.phone}\n"
        if lead.email:
            text += f"📧 {lead.email}\n"
        text += f"Yaratilgan: {lead.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    await message.answer(text, parse_mode='HTML')


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show seller's statistics."""
    seller = get_seller_by_telegram_id(message.from_user.id)
    
    if not seller:
        await message.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    # Calculate statistics
    total_leads = Lead.objects.filter(seller=seller).count()
    new_leads = Lead.objects.filter(seller=seller, status='new').count()
    contacted_leads = Lead.objects.filter(seller=seller, status='contacted').count()
    converted_leads = Lead.objects.filter(seller=seller, status='converted').count()
    
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_leads = Lead.objects.filter(
        seller=seller,
        created_at__gte=week_ago
    ).count()
    
    text = (
        f"📊 Sizning Statistikangiz\n\n"
        f"Jami Lidlar: {total_leads}\n"
        f"🆕 Yangi: {new_leads}\n"
        f"📞 Bog'langan: {contacted_leads}\n"
        f"💰 Aylantirilgan: {converted_leads}\n"
        f"📈 Aylanish Darajasi: {conversion_rate:.1f}%\n"
        f"📅 Oxirgi 7 Kun: {recent_leads} lid"
    )
    
    await message.answer(text)


@dp.message(Command("kpi"))
async def cmd_kpi(message: Message):
    """Show seller's KPI summary."""
    seller = get_seller_by_telegram_id(message.from_user.id)
    
    if not seller:
        await message.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    # Get current month summary
    current_month = datetime.now().date().replace(day=1)
    try:
        summary = SellerKPISummary.objects.get(seller=seller, month=current_month)
        text = (
            f"📊 Sizning KPI Xulosangiz ({summary.month.strftime('%B %Y')})\n\n"
            f"💰 Jami Bonus: ${summary.total_bonus}\n"
            f"⚠️ Jami Jarima: ${summary.total_penalty}\n"
            f"💵 Sof Miqdor: ${summary.net_amount}\n\n"
            f"📈 Ko'rsatkichlar:\n"
            f"Jami Lidlar: {summary.total_leads}\n"
            f"Aylantirilgan: {summary.converted_leads}\n"
            f"Aylanish Darajasi: {summary.conversion_rate:.1f}%"
        )
    except SellerKPISummary.DoesNotExist:
        text = (
            f"📊 Sizning KPI Xulosangiz\n\n"
            "Ushbu oy uchun KPI ma'lumotlari hali mavjud emas. "
            "Hisob-kitoblar avtomatik ravishda amalga oshiriladi."
        )
    
    await message.answer(text)


@dp.callback_query(F.data.startswith("lead_"))
async def handle_lead_callback(callback_query, state: FSMContext):
    """Handle lead selection callback."""
    seller = get_seller_by_telegram_id(callback_query.from_user.id)
    
    if not seller:
        await callback_query.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    lead_id = int(callback_query.data.split("_")[1])
    
    try:
        lead = Lead.objects.get(id=lead_id, seller=seller)
    except Lead.DoesNotExist:
        await callback_query.answer("❌ Lid topilmadi.")
        return
    
    # Show lead details and status update options
    text = (
        f"📋 Lid Tafsilotlari\n\n"
        f"Ism: {lead.name}\n"
        f"Holat: {lead.get_status_display()}\n"
    )
    if lead.phone:
        text += f"Telefon: {lead.phone}\n"
    if lead.email:
        text += f"Email: {lead.email}\n"
    if lead.company:
        text += f"Kompaniya: {lead.company}\n"
    if lead.notes:
        text += f"Eslatmalar: {lead.notes}\n"
    text += f"\nYaratilgan: {lead.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    # Create status update keyboard
    keyboard = [
        [
            InlineKeyboardButton(text="🆕 Yangi", callback_data=f"status_{lead.id}_new"),
            InlineKeyboardButton(text="📞 Bog'langan", callback_data=f"status_{lead.id}_contacted"),
        ],
        [
            InlineKeyboardButton(text="✅ Sifatli", callback_data=f"status_{lead.id}_qualified"),
            InlineKeyboardButton(text="💰 Aylantirilgan", callback_data=f"status_{lead.id}_converted"),
        ],
        [
            InlineKeyboardButton(text="❌ Yo'qotilgan", callback_data=f"status_{lead.id}_lost"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback_query.message.edit_text(text, parse_mode='HTML', reply_markup=reply_markup)
    await callback_query.answer()


@dp.callback_query(F.data.startswith("status_"))
async def handle_status_update(callback_query, state: FSMContext):
    """Handle lead status update."""
    seller = get_seller_by_telegram_id(callback_query.from_user.id)
    
    if not seller:
        await callback_query.answer("❌ Siz sotuvchi sifatida ro'yxatdan o'tmagansiz.")
        return
    
    parts = callback_query.data.split("_")
    lead_id = int(parts[1])
    new_status = parts[2]
    
    try:
        lead = Lead.objects.get(id=lead_id, seller=seller)
        lead.status = new_status
        
        if new_status == 'contacted' and not lead.contacted_at:
            from django.utils import timezone
            lead.contacted_at = timezone.now()
        elif new_status == 'converted' and not lead.converted_at:
            from django.utils import timezone
            lead.converted_at = timezone.now()
        
        lead.save()
        
        await callback_query.answer(f"✅ Holat {lead.get_status_display()} ga yangilandi")
        
        # Update message
        text = (
            f"📋 Lid Tafsilotlari\n\n"
            f"Ism: {lead.name}\n"
            f"Holat: {lead.get_status_display()} ✅\n"
        )
        if lead.phone:
            text += f"Telefon: {lead.phone}\n"
        if lead.email:
            text += f"Email: {lead.email}\n"
        text += f"\nYangilangan: {lead.updated_at.strftime('%Y-%m-%d %H:%M')}"
        
        await callback_query.message.edit_text(text, parse_mode='HTML')
        
    except Lead.DoesNotExist:
        await callback_query.answer("❌ Lid topilmadi.")


def start_bot():
    """Start the Telegram bot."""
    import asyncio
    
    async def main():
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Error in bot polling: {e}")
            raise
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error starting bot: {e}")
        raise

