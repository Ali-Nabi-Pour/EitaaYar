"""
مثال مدیریت خطا در کتابخانه ایتایار
"""

from eitaayar import Client

def error_handling_example():
    """نمونه مدیریت خطا"""
    print("🐛 مثال مدیریت خطا")
    
    client = Client(
        token="invalid_token",  # توکن نامعتبر
        enable_logging=True
    )
    
    # تست با توکن نامعتبر
    print("\n🔒 تست با توکن نامعتبر:")
    response = client.get_me()
    
    if not response.ok:
        print(f"   نوع خطا: {response.error_type}")
        print(f"   کد خطا: {response.error_code}")
        print(f"   پیام خطا: {response.error}")
    
    # تست ارسال به چت نامعتبر
    print("\n💬 تست ارسال به چت نامعتبر:")
    response = client.send_message(
        chat_id=-999999999,  # چت آیدی نامعتبر
        text="تست چت نامعتبر"
    )
    
    if not response.ok:
        print(f"   نوع خطا: {response.error_type}")
        print(f"   کد خطا: {response.error_code}")
        print(f"   پیام خطا: {response.error}")
    
    client.disable_logging()

if __name__ == "__main__":
    error_handling_example()