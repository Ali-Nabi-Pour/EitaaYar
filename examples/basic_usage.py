import asyncio
from eitaayar import Client, about

def sync_example():
    """نمونه استفاده همزمان"""
    print("🔧 مثال استفاده همزمان")
    
    # ایجاد کلاینت
    client = Client(
        token="YOUR_BOT_TOKEN",  # جایگزین کنید با توکن واقعی
        enable_logging=True,
        log_level="INFO"
    )
    
    # دریافت اطلاعات ربات
    print("\n🤖 دریافت اطلاعات ربات:")
    me = client.get_me()
    if me.ok:
        print(f"   نام: {me.result.first_name} {me.result.last_name}")
        print(f"   یوزرنیم: @{me.result.username}")
        print(f"   آیدی: {me.result.id}")
    else:
        print(f"   خطا: {me.error}")
    
    # ارسال پیام
    print("\n✉️ ارسال پیام:")
    response = client.send_message(
        chat_id=10872172,  # جایگزین کنید با چت آیدی واقعی
        text="این یک پیام تست از کتابخانه ایتایار است! 🚀",
        title="پیام تست"
    )
    
    if response.ok:
        print(f"   ✅ پیام ارسال شد! آیدی: {response.message_id}")
        print(f"   تاریخ: {response.date}")
        print(f"   متن: {response.text}")
    else:
        print(f"   ❌ خطا در ارسال پیام: {response.error}")
    
    client.disable_logging()

async def async_example():
    """نمونه استفاده غیرهمزمان"""
    print("\n⚡ مثال استفاده غیرهمزمان")
    
    async with Client(
        token="YOUR_BOT_TOKEN",  # جایگزین کنید با توکن واقعی
        enable_logging=True
    ) as client:
        # ارسال پیام
        response = await client.send_message_async(
            chat_id=10872172,  # جایگزین کنید با چت آیدی واقعی
            text="این یک پیام تست async است! ⚡"
        )
        
        if response.ok:
            print("   ✅ پیام async ارسال شد!")
        else:
            print(f"   ❌ خطا: {response.error}")

if __name__ == "__main__":
    # نمایش اطلاعات کتابخانه
    about()
    
    # اجرای مثال‌ها
    sync_example()
    
    # اجرای مثال async
    asyncio.run(async_example())
    
    print("\n🎉 تمام مثال‌ها با موفقیت اجرا شدند!")