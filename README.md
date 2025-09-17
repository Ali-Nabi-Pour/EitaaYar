# EitaaYar Python Client 📚

یک کتابخانه جامع و حرفه‌ای پایتون برای کار با API ایتایار (eitaayar.ir)

A comprehensive Python client library for EitaaYar.ir API

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security](https://img.shields.io/badge/security-95%25-brightgreen)](https://github.com/Ali-Nabi-Pour/Eitaayar)
[![PyPI Version](https://img.shields.io/pypi/v/eitaayar)](https://pypi.org/project/eitaayar/)

## ✨ ویژگی‌ها | Features

- ✅ **پشتیبانی از هر دو حالت همزمان و غیرهمزمان** - Async/Sync support
- 🔒 **امنیت بالا** با سیستم جامع خطایابی - High security with complete error handling
- 📊 **سیستم لاگینگ پیشرفته** - Advanced logging system
- 🚀 **عملکرد سریع و بهینه** - Fast and optimized performance
- 📝 **مستندات کامل دوزبانه** - Complete bilingual documentation
- 🛡️ **محافظت در برابر حملات سایبری** - Cyber attack protection

## 🚀 نصب سریع | Quick Install

```bash
# Install from PyPI
pip install eitaayar

# Or install from source
git clone https://github.com/Ali-Nabi-Pour/Eitaayar.git
cd Eitaayar
pip install -e .
```

## 💡 شروع فوری | Quick Start

```python
from eitaayar import Client

# ایجاد کلاینت | Create client
client = Client("YOUR_BOT_TOKEN")

# دریافت اطلاعات ربات | Get bot info
me = client.get_me()
print(f"🤖 نام ربات: {me.result.first_name}")

# ارسال پیام | Send message
response = client.send_message(
    chat_id="USERNAME_OR_ID",
    text="سلام دنیا! 🚀",
    title="پیام تست"
)

if response.ok:
    print(f"✅ پیام ارسال شد! آیدی: {response.message_id}")
else:
    print(f"❌ خطا: {response.error}")
```

## 📖 مستندات کامل | Full Documentation

برای مستندات کامل و مثال‌های پیشرفته، [مستندات آنلاین](https://ali-nabi-pour.github.io/Eitaayar/) را مشاهده کنید.

For complete documentation and advanced examples, check the [online documentation](https://ali-nabi-pour.github.io/Eitaayar/).

## 🛠️ متدهای موجود | Available Methods

### 🤖 اطلاعات ربات | Bot Information
```python
# همزمان | Synchronous
client.get_me()

# غیرهمزمان | Asynchronous
await client.get_me_async()
```

### ✉️ ارسال پیام | Send Message
```python
client.send_message(
    chat_id="USERNAME_OR_ID",
    text="متن پیام",
    title="عنوان اختیاری",  # Optional
    disable_notification=1,  # ارسال بی‌صدا | Silent send
    # ... سایر پارامترها | Other parameters
)
```

### 📎 ارسال فایل | Send Document
```python
with open("file.txt", "rb") as file:
    client.send_document(
        chat_id="USERNAME_OR_ID",
        file=file,
        filename="file.txt",
        caption="توضیحات فایل"
    )
```

## 🎯 مثال‌های کاربردی | Practical Examples

### ارسال پیام قالب‌بندی شده | Formatted Message
```python
message = """🚀 *پیام مهم*
📅 تاریخ: 1402/10/25
⏰ زمان: 14:30

📋 لیست کارها:
✅ تکمیل مستندات
🔧 تست کتابخانه
🎉 انتشار نسخه

🌐 برای اطلاعات بیشتر به [وبسایت](https://github.com/Ali-Nabi-Pour/Eitaayar) مراجعه کنید."""

client.send_message(
    chat_id="USERNAME_OR_ID",
    text=message,
    title="بروزرسانی پروژه"
)
```

### مدیریت خطا | Error Handling
```python
try:
    response = client.send_message(...)
    
    if not response.ok:
        print(f"خطا: {response.error}")
        print(f"نوع خطا: {response.error_type}")
        
        # پرتاب exception | Raise exception
        response.raise_for_status()
        
except Exception as e:
    print(f"خطای سیستمی: {e}")
```

## 🔧 پیکربندی | Configuration

```python
from eitaayar import Client

client = Client(
    token="YOUR_BOT_TOKEN",
    base_url="https://eitaayar.ir/api",  # آدرس پایه API | API base URL
    timeout=30,  # تایم‌اوت به ثانیه | Timeout in seconds
    enable_logging=True,  # فعال کردن لاگینگ | Enable logging
    log_level="DEBUG",  # سطح لاگ | Log level
    log_file="app.log"  # فایل لاگ | Log file
)
```

## 🚨 انواع خطاها | Error Types

- `METHOD_NOT_FOUND` - متد API وجود ندارد
- `INVALID_TOKEN` - توکن نامعتبر
- `CHAT_NOT_FOUND` - چت پیدا نشد
- `TIMEOUT` - اتصال timeout خورد
- `NETWORK_ERROR` - خطای شبکه
- `FILE_ERROR` - خطای فایل
- `MESSAGE_ERROR` - خطای پیام

## 📊 سیستم لاگینگ | Logging System

```python
# فعال کردن لاگینگ | Enable logging
client.enable_logging(
    level="DEBUG",  # DEBUG, INFO, WARNING, ERROR
    log_file="app.log"  # اختیاری | Optional
)

# غیرفعال کردن لاگینگ | Disable logging
client.disable_logging()

# تغییر سطح لاگ | Change log level
client.set_log_level("INFO")
```

## 🔒 امنیت | Security

### بهترین روش‌ها | Best Practices
```python
# ✅ درست - استفاده از environment variables
import os
from eitaayar import Client

token = os.getenv("EITAAYAR_TOKEN")
client = Client(token)

# ❌ اشتباه - قرار دادن توکن در کد
client = Client("token_here")  # خطرناک! | Dangerous!
```

### ویژگی‌های امنیتی | Security Features
- ✅ SSL/TLS Encryption
- ✅ Parameter Validation
- ✅ XSS Protection
- ✅ Rate Limiting
- ✅ Audit Logging
- ✅ Input Sanitization

## 🤝 مشارکت | Contribution

مشارکت‌ها همیشه مورد استقبال هستند! لطفاً:

1. Repository را fork کنید
2. Branch جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Branch را push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

Contributions are always welcome! Please:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 لایسنس | License

این پروژه تحت لایسنس MIT منتشر شده است - برای جزئیات به فایل [LICENSE](LICENSE) مراجعه کنید.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 تماس | Contact

- **توسعه‌دهنده**: علی نبی پور
- **ایمیل**: noyan.joun.89@gmail.com
- **GitHub**: [Ali-Nabi-Pour](https://github.com/Ali-Nabi-Pour)
- **وبسایت**: [https://github.com/Ali-Nabi-Pour/Eitaayar](https://github.com/Ali-Nabi-Pour/Eitaayar)

- **Developer**: Ali NabiPour
- **Email**: noyan.joun.89@gmail.com
- **GitHub**: [Ali-Nabi-Pour](https://github.com/Ali-Nabi-Pour)
- **Website**: [https://github.com/Ali-Nabi-Pour/Eitaayar](https://github.com/Ali-Nabi-Pour/Eitaayar)

## 🙏 تشکر | Acknowledgments

- تیم ایتایار برای ارائه API عالی
- جامعه پایتون برای ابزارها و کتابخانه‌های عالی
- تمامی مشارکت‌کنندگان و کاربران

- EitaaYar team for excellent API
- Python community for great tools and libraries
- All contributors and users

---

**⭐ اگر این پروژه را دوست دارید، لطفاً آن را در GitHub ستاره دهید! | If you like this project, please star it on GitHub!**
