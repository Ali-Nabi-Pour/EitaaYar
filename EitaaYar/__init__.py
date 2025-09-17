import aiohttp
import requests
import json
import logging
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

__version__ = "1.0"

# امضای دیجیتال کتابخانه - توسعه‌دهنده: علی نبی پور
LIBRARY_SIGNATURE = {
    "name": "EitaaYar Python Client",
    "version": __version__,
    "developer": "Ali NabiPour",
    "email": "noyan.joun.89@gmail.com",
    "website": "https://github.com/Ali-Nabi-Pour/Eitaayar",
    "license": "MIT License",
    "message": "با ❤️ توسعه داده شده برای جامعه برنامه‌نویسان ایران",
    "persian_message": "قدرت گرفته از پایتون و عشق به کد زدن!",
    "signature": "Developed with passion for the Iranian developer community"
}

# ایجاد لاگر اصلی اما بدون تنظیمات پیش‌فرض
logger = logging.getLogger('eitaayar.client')
logger.propagate = False
logger.addHandler(logging.NullHandler())

# نمایش امضا هنگام import
print(f"✨ {LIBRARY_SIGNATURE['name']} v{LIBRARY_SIGNATURE['version']}")
print(f"📧 {LIBRARY_SIGNATURE['developer']} - {LIBRARY_SIGNATURE['email']}")
print(f"🌐 {LIBRARY_SIGNATURE['website']}")
print(f"💝 {LIBRARY_SIGNATURE['persian_message']}")
print("-" * 50)


@dataclass
class User:
    """User information model."""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name or ''} (@{self.username})".strip()


@dataclass
class Chat:
    """Chat information model."""
    id: int
    type: str
    username: Optional[str] = None

    def __str__(self) -> str:
        return f"Chat {self.id} ({self.type})"


@dataclass
class Message:
    """Message information model."""
    message_id: int
    from_user: User
    chat: Chat
    date: datetime
    text: Optional[str] = None
    caption: Optional[str] = None

    @property
    def timestamp(self) -> int:
        """Return timestamp as integer."""
        return int(self.date.timestamp())

    def __str__(self) -> str:
        return f"Message {self.message_id} from {self.from_user} at {self.date}"


class Response:
    """
    Response object for API calls with dot notation access.
    """
    
    def __init__(self, data: Dict[str, Any], enable_logging: bool = True):
        self._data = data
        self.ok = data.get('ok', False)
        self._enable_logging = enable_logging
        
        # اضافه کردن امضا به پاسخ
        self._data['_library_signature'] = {
            "name": LIBRARY_SIGNATURE["name"],
            "version": LIBRARY_SIGNATURE["version"],
            "developer": LIBRARY_SIGNATURE["developer"]
        }
        
        # Parse result if available
        try:
            self.result = self._parse_result(data.get('result')) if data.get('result') else None
            if self.result and self._enable_logging:
                logger.debug("Successfully parsed response result")
        except Exception as e:
            self.result = None
            self._parse_error = str(e)
            if self._enable_logging:
                logger.warning(f"Failed to parse response result: {e}")
        
        # Store error if any
        self.error = data.get('error')
        self.error_code = data.get('error_code')
        self.error_type = self._detect_error_type()
        
        if self.error and self._enable_logging:
            logger.warning(f"API response contains error: {self.error} (code: {self.error_code})")
    
    def _detect_error_type(self) -> Optional[str]:
        """تشخیص نوع خطا بر اساس پاسخ API"""
        if not self.ok:
            error_desc = str(self.error or '').lower()
            
            if "method not found" in error_desc:
                return "METHOD_NOT_FOUND"
            elif "invalid token" in error_desc or "unauthorized" in error_desc:
                return "INVALID_TOKEN"
            elif "chat not found" in error_desc or "chat_id" in error_desc:
                return "CHAT_NOT_FOUND"
            elif "timeout" in error_desc:
                return "TIMEOUT"
            elif "network" in error_desc or "connection" in error_desc:
                return "NETWORK_ERROR"
            elif "not implemented" in error_desc:
                return "METHOD_NOT_IMPLEMENTED"
            elif "file" in error_desc or "document" in error_desc:
                return "FILE_ERROR"
            elif "text" in error_desc or "message" in error_desc:
                return "MESSAGE_ERROR"
                
        return None
    
    def _parse_result(self, result_data: Dict[str, Any]) -> Any:
        """Parse result data into appropriate objects."""
        try:
            # Check if it's a message response
            if 'message_id' in result_data:
                if self._enable_logging:
                    logger.debug("Parsing message response")
                return self._parse_message(result_data)
            
            # Check if it's user info (getMe)
            elif 'id' in result_data and 'is_bot' in result_data:
                if self._enable_logging:
                    logger.debug("Parsing user response")
                return self._parse_user(result_data)
            
            # Return as-is for other types
            if self._enable_logging:
                logger.debug("Returning raw result data")
            return result_data
        except Exception as e:
            if self._enable_logging:
                logger.error(f"Failed to parse result: {e}")
            raise ValueError(f"Failed to parse result: {e}") from e
    
    def _parse_user(self, user_data: Dict[str, Any]) -> User:
        """Parse user data into User object."""
        try:
            user = User(
                id=user_data.get('id', 0),
                is_bot=user_data.get('is_bot', False),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name'),
                username=user_data.get('username')
            )
            if self._enable_logging:
                logger.debug(f"Parsed user: {user}")
            return user
        except Exception as e:
            if self._enable_logging:
                logger.error(f"Failed to parse user data: {e}")
            raise ValueError(f"Failed to parse user data: {e}") from e
    
    def _parse_message(self, message_data: Dict[str, Any]) -> Message:
        """Parse message data into Message object."""
        try:
            # Parse from_user
            from_data = message_data.get('from', {})
            from_user = User(
                id=from_data.get('id', 0),
                is_bot=from_data.get('is_bot', False),
                first_name=from_data.get('first_name', ''),
                last_name=from_data.get('last_name'),
                username=from_data.get('username')
            )
            
            # Parse chat
            chat_data = message_data.get('chat', {})
            chat = Chat(
                id=chat_data.get('id', 0),
                type=chat_data.get('type', ''),
                username=chat_data.get('username')
            )
            
            # Parse date
            date_ts = message_data.get('date')
            date_obj = datetime.fromtimestamp(date_ts) if date_ts else datetime.now()
            
            message = Message(
                message_id=message_data.get('message_id', 0),
                from_user=from_user,
                chat=chat,
                date=date_obj,
                text=message_data.get('text'),
                caption=message_data.get('caption')
            )
            
            if self._enable_logging:
                logger.debug(f"Parsed message: ID={message.message_id}")
            return message
        except Exception as e:
            if self._enable_logging:
                logger.error(f"Failed to parse message data: {e}")
            raise ValueError(f"Failed to parse message data: {e}") from e
    
    def __getattr__(self, name: str) -> Any:
        """Allow dot notation access to result properties."""
        try:
            if self.result and hasattr(self.result, name):
                return getattr(self.result, name)
            elif name in self._data:
                return self._data[name]
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        except AttributeError:
            if self._enable_logging:
                logger.warning(f"Attribute not found: {name}")
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access."""
        try:
            return self._data.get(key)
        except KeyError:
            if self._enable_logging:
                logger.warning(f"Key not found: {key}")
            raise KeyError(f"Key '{key}' not found in response")
    
    def __bool__(self) -> bool:
        """Boolean evaluation based on success."""
        return self.ok
    
    def __str__(self) -> str:
        """String representation."""
        if self.ok:
            return f"Response(ok=true, result={self.result})"
        else:
            return f"Response(ok=false, error={self.error}, error_type={self.error_type})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Return raw response data as dictionary."""
        return self._data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with default."""
        return self._data.get(key, default)
    
    @property
    def library_info(self) -> Dict[str, str]:
        """Get library signature information."""
        return self._data.get('_library_signature', {})
    
    def raise_for_status(self):
        """Raise exception if response contains error."""
        if not self.ok:
            error_msg = f"API Error: {self.error}"
            if self.error_code:
                error_msg += f" (code: {self.error_code})"
            if self.error_type:
                error_msg += f" (type: {self.error_type})"
            raise Exception(error_msg)


class Client:
    """
    Client for interacting with the eitaayar.ir API.
    
    ✨ Developed with passion by Ali NabiPour
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://eitaayar.ir/api",
        timeout: int = 30,
        enable_logging: bool = False,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Initialize the client with your API token.

        :param token: Your API token from eitaayar.ir
        :param base_url: Base URL for the API (default: https://eitaayar.ir/api)
        :param timeout: Timeout for requests in seconds (default: 30)
        :param enable_logging: Enable logging system (default: False)
        :param log_level: Logging level (default: logging.INFO)
        :param log_file: Custom log file path (optional)
        :param user_agent: Custom User-Agent string (optional)
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._enable_logging = enable_logging
        self.user_agent = user_agent or f"{LIBRARY_SIGNATURE['name']}/{LIBRARY_SIGNATURE['version']}"
        
        # اضافه کردن هدرهای سفارشی با امضا
        self.default_headers = {
            'User-Agent': self.user_agent,
            'X-Library-Name': LIBRARY_SIGNATURE['name'],
            'X-Library-Version': LIBRARY_SIGNATURE['version'],
            'X-Developer': LIBRARY_SIGNATURE['developer'],
            'X-Developed-With': 'Love for Python and Iranian Developers'
        }
        
        # تنظیمات لاگر در صورت فعال بودن
        if enable_logging:
            self._setup_logging(log_level, log_file)
            self._log(logging.INFO, f"Client initialized with base_url: {base_url}")
            self._log(logging.DEBUG, f"Token: {token[:10]}...")
            self._log(logging.INFO, f"Library: {LIBRARY_SIGNATURE['name']} v{LIBRARY_SIGNATURE['version']}")

    def _setup_logging(self, log_level: int, log_file: Optional[str] = None) -> None:
        """Setup logging configuration."""
        # حذف همه هندلرهای قبلی
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # تنظیم سطح لاگر
        logger.setLevel(log_level)
        
        # ایجاد فرمت‌تر
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # هندلر کنسول
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
        
        # هندلر فایل اگر مشخص شده
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                file_handler.setLevel(log_level)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not create log file {log_file}: {e}")

    def _log(self, level: int, message: str, *args, **kwargs):
        """Helper method for conditional logging."""
        if self._enable_logging:
            logger.log(level, message, *args, **kwargs)

    async def _aiohttp_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make an asynchronous HTTP request to the API.
        """
        if self._session is None:
            try:
                self._session = aiohttp.ClientSession(headers=self.default_headers)
                self._log(logging.DEBUG, "aiohttp session created with custom headers")
            except Exception as e:
                self._log(logging.ERROR, f"Failed to create aiohttp session: {e}")
                return Response({"ok": False, "error": f"Failed to create session: {e}"}, self._enable_logging)

        url = f"{self.base_url}/{self.token}/{method}"
        self._log(logging.INFO, f"Making async request to: {method}")
        self._log(logging.DEBUG, f"URL: {url}")
        self._log(logging.DEBUG, f"Params: {params}")
        self._log(logging.DEBUG, f"Data: {data}")

        try:
            headers = {**self.default_headers}
            
            if files:
                self._log(logging.DEBUG, "Request contains files")
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, str(value))
                
                for key, file_info in files.items():
                    if isinstance(file_info, tuple):
                        form_data.add_field(
                            key, 
                            file_info[1], 
                            filename=file_info[0],
                            content_type=file_info[2] if len(file_info) > 2 else None
                        )
                    else:
                        form_data.add_field(key, file_info)
                
                async with self._session.post(
                    url, data=form_data, timeout=self.timeout, headers=headers
                ) as response:
                    try:
                        raw_response = await response.json()
                        self._log(logging.INFO, f"Async request completed: {method} - Status: {response.status}")
                        self._log(logging.DEBUG, f"Response: {raw_response}")
                        return Response(raw_response, self._enable_logging)
                    except json.JSONDecodeError as e:
                        self._log(logging.ERROR, f"Invalid JSON response from {method}: {e}")
                        return Response({"ok": False, "error": f"Invalid JSON response: {e}", "error_code": 500}, self._enable_logging)
            else:
                headers['Content-Type'] = 'application/json'
                async with self._session.post(
                    url, json=data, params=params, timeout=self.timeout, headers=headers
                ) as response:
                    try:
                        raw_response = await response.json()
                        self._log(logging.INFO, f"Async request completed: {method} - Status: {response.status}")
                        self._log(logging.DEBUG, f"Response: {raw_response}")
                        return Response(raw_response, self._enable_logging)
                    except json.JSONDecodeError as e:
                        self._log(logging.ERROR, f"Invalid JSON response from {method}: {e}")
                        return Response({"ok": False, "error": f"Invalid JSON response: {e}", "error_code": 500}, self._enable_logging)
        except aiohttp.ClientError as e:
            self._log(logging.ERROR, f"Network error in async request {method}: {e}")
            return Response({"ok": False, "error": f"Network error: {e}", "error_code": 503}, self._enable_logging)
        except asyncio.TimeoutError:
            self._log(logging.ERROR, f"Timeout in async request {method}")
            return Response({"ok": False, "error": "Request timeout", "error_code": 408}, self._enable_logging)
        except Exception as e:
            self._log(logging.ERROR, f"Unexpected error in async request {method}: {e}")
            return Response({"ok": False, "error": f"Unexpected error: {e}", "error_code": 500}, self._enable_logging)

    def _requests_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Make a synchronous HTTP request to the API.
        """
        url = f"{self.base_url}/{self.token}/{method}"
        self._log(logging.INFO, f"Making sync request to: {method}")
        self._log(logging.DEBUG, f"URL: {url}")
        self._log(logging.DEBUG, f"Params: {params}")
        self._log(logging.DEBUG, f"Data: {data}")

        try:
            headers = {**self.default_headers}
            
            if files:
                self._log(logging.DEBUG, "Request contains files")
                response = requests.post(
                    url,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                    headers=headers
                )
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(
                    url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
            
            self._log(logging.INFO, f"Sync request completed: {method} - Status: {response.status_code}")
            self._log(logging.DEBUG, f"Response text: {response.text[:200]}...")
            
            try:
                response_data = response.json()
                self._log(logging.DEBUG, f"Response JSON: {response_data}")
                return Response(response_data, self._enable_logging)
            except json.JSONDecodeError as e:
                self._log(logging.ERROR, f"Invalid JSON response from {method}: {e}")
                return Response({"ok": False, "error": f"Invalid JSON response: {e}", "error_code": 500}, self._enable_logging)
                
        except requests.exceptions.RequestException as e:
            self._log(logging.ERROR, f"Network error in sync request {method}: {e}")
            return Response({"ok": False, "error": f"Network error: {e}", "error_code": 503}, self._enable_logging)
        except requests.exceptions.Timeout:
            self._log(logging.ERROR, f"Timeout in sync request {method}")
            return Response({"ok": False, "error": "Request timeout", "error_code": 408}, self._enable_logging)
        except Exception as e:
            self._log(logging.ERROR, f"Unexpected error in sync request {method}: {e}")
            return Response({"ok": False, "error": f"Unexpected error: {e}", "error_code": 500}, self._enable_logging)

    async def get_me_async(self) -> Response:
        """
        Get information about the API (asynchronous).
        
        :return: Response object with API information
        """
        self._log(logging.INFO, "Getting bot info (async)")
        return await self._aiohttp_request("getMe")

    def get_me(self) -> Response:
        """
        Get information about the API (synchronous).
        
        :return: Response object with API information
        """
        self._log(logging.INFO, "Getting bot info (sync)")
        return self._requests_request("getMe")

    async def send_message_async(
        self,
        chat_id: Union[int, str],
        text: str,
        title: Optional[str] = None,
        disable_notification: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
        date: Optional[int] = None,
        pin: Optional[int] = None,
        auto_delete_after_views: Optional[int] = None,
    ) -> Response:
        """
        Send a text message (asynchronous).

        :param chat_id: Unique identifier for the target chat or username
        :param text: Text of the message to be sent
        :param title: Message title (optional)
        :param disable_notification: Send message silently (optional)
        :param reply_to_message_id: ID of the original message (optional)
        :param date: Date and time to send message (Unix timestamp, optional)
        :param pin: Pin the message after sending (optional)
        :param auto_delete_after_views: Auto-delete after views count (optional)
        :return: Response object with message result
        """
        self._log(logging.INFO, f"Sending message to chat {chat_id} (async)")
        self._log(logging.DEBUG, f"Message text: {text[:50]}...")
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "title": title,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "date": date,
            "pin": pin,
            "auto_delete_after_views": auto_delete_after_views,
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        return await self._aiohttp_request("sendMessage", data=data)

    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        title: Optional[str] = None,
        disable_notification: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
        date: Optional[int] = None,
        pin: Optional[int] = None,
        auto_delete_after_views: Optional[int] = None,
    ) -> Response:
        """
        Send a text message (synchronous).

        :param chat_id: Unique identifier for the target chat or username
        :param text: Text of the message to be sent
        :param title: Message title (optional)
        :param disable_notification: Send message silently (optional)
        :param reply_to_message_id: ID of the original message (optional)
        :param date: Date and time to send message (Unix timestamp, optional)
        :param pin: Pin the message after sending (optional)
        :param auto_delete_after_views: Auto-delete after views count (optional)
        :return: Response object with message result
        """
        self._log(logging.INFO, f"Sending message to chat {chat_id} (sync)")
        self._log(logging.DEBUG, f"Message text: {text[:50]}...")
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "title": title,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "date": date,
            "pin": pin,
            "auto_delete_after_views": auto_delete_after_views,
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        return self._requests_request("sendMessage", data=data)

    async def send_document_async(
        self,
        chat_id: Union[int, str],
        file: Any,
        caption: Optional[str] = None,
        title: Optional[str] = None,
        disable_notification: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
        date: Optional[int] = None,
        pin: Optional[int] = None,
        auto_delete_after_views: Optional[int] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Response:
        """
        Send a document/file (asynchronous).

        :param chat_id: Unique identifier for the target chat or username
        :param file: File to send (file object, bytes, or file path)
        :param caption: Document caption (optional)
        :param title: Message title (optional)
        :param disable_notification: Send message silently (optional)
        :param reply_to_message_id: ID of the original message (optional)
        :param date: Date and time to send message (Unix timestamp, optional)
        :param pin: Pin the message after sending (optional)
        :param auto_delete_after_views: Auto-delete after views count (optional)
        :param filename: Name of the file (optional)
        :param content_type: Content type of the file (optional)
        :return: Response object with message result
        """
        self._log(logging.INFO, f"Sending document to chat {chat_id} (async)")
        
        # ابتدا بررسی می‌کنیم که متد وجود دارد یا نه
        test_response = await self._aiohttp_request("sendDocument", data={"chat_id": chat_id})
        
        if not test_response.ok and test_response.error_type == "METHOD_NOT_FOUND":
            self._log(logging.WARNING, "sendDocument method not found, using fallback")
            return await self._send_document_fallback(chat_id, file, caption, filename)
        
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "title": title,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "date": date,
            "pin": pin,
            "auto_delete_after_views": auto_delete_after_views,
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        files = {"file": (filename, file, content_type)} if file else None
        
        return await self._aiohttp_request("sendDocument", data=data, files=files)

    def send_document(
        self,
        chat_id: Union[int, str],
        file: Any,
        caption: Optional[str] = None,
        title: Optional[str] = None,
        disable_notification: Optional[int] = None,
        reply_to_message_id: Optional[int] = None,
        date: Optional[int] = None,
        pin: Optional[int] = None,
        auto_delete_after_views: Optional[int] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Response:
        """
        Send a document/file (synchronous).

        :param chat_id: Unique identifier for the target chat or username
        :param file: File to send (file object, bytes, or file path)
        :param caption: Document caption (optional)
        :param title: Message title (optional)
        :param disable_notification: Send message silently (optional)
        :param reply_to_message_id: ID of the original message (optional)
        :param date: Date and time to send message (Unix timestamp, optional)
        :param pin: Pin the message after sending (optional)
        :param auto_delete_after_views: Auto-delete after views count (optional)
        :param filename: Name of the file (optional)
        :param content_type: Content type of the file (optional)
        :return: Response object with message result
        """
        self._log(logging.INFO, f"Sending document to chat {chat_id} (sync)")
        
        # ابتدا بررسی می‌کنیم که متد وجود دارد یا نه
        test_response = self._requests_request("sendDocument", data={"chat_id": chat_id})
        
        if not test_response.ok and test_response.error_type == "METHOD_NOT_FOUND":
            self._log(logging.WARNING, "sendDocument method not found, using fallback")
            return self._send_document_fallback_sync(chat_id, file, caption, filename)
        
        data = {
            "chat_id": chat_id,
            "caption": caption,
            "title": title,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "date": date,
            "pin": pin,
            "auto_delete_after_views": auto_delete_after_views,
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        files = {"file": (filename, file, content_type)} if file else None
        
        return self._requests_request("sendDocument", data=data, files=files)

    async def _send_document_fallback(
        self,
        chat_id: Union[int, str],
        file: Any,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Response:
        """Fallback method when sendDocument is not available (async)."""
        self._log(logging.INFO, "Using fallback method for file upload (async)")
        
        # ایجاد یک پیام با اطلاعات فایل
        file_info = f"📁 فایل: {filename or 'unknown'}"
        if caption:
            file_info += f"\n📝 توضیحات: {caption}"
        
        file_info += "\n\n❌ امکان ارسال فایل مستقیم وجود ندارد. لطفاً از روش‌های دیگر استفاده کنید."
        
        return await self.send_message_async(chat_id, file_info)

    def _send_document_fallback_sync(
        self,
        chat_id: Union[int, str],
        file: Any,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Response:
        """Fallback method when sendDocument is not available (sync)."""
        self._log(logging.INFO, "Using fallback method for file upload (sync)")
        
        # ایجاد یک پیام با اطلاعات فایل
        file_info = f"📁 فایل: {filename or 'unknown'}"
        if caption:
            file_info += f"\n📝 توضیحات: {caption}"
        
        file_info += "\n\n❌ امکان ارسال فایل مستقیم وجود ندارد. لطفاً از روش‌های دیگر استفاده کنید."
        
        return self.send_message(chat_id, file_info)

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            try:
                await self._session.close()
                self._log(logging.DEBUG, "aiohttp session closed")
            except Exception as e:
                self._log(logging.ERROR, f"Failed to close aiohttp session: {e}")
            finally:
                self._session = None

    def enable_logging(self, level: int = logging.INFO, log_file: Optional[str] = None) -> None:
        """Enable logging system dynamically."""
        self._enable_logging = True
        self._setup_logging(level, log_file)
        self._log(logging.INFO, "Logging system enabled")
        self._log(logging.INFO, f"Library: {LIBRARY_SIGNATURE['name']} v{LIBRARY_SIGNATURE['version']}")

    def disable_logging(self) -> None:
        """Disable logging system."""
        self._enable_logging = False
        # حذف همه هندلرها
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.addHandler(logging.NullHandler())

    def get_library_info(self) -> Dict[str, str]:
        """Get library signature information."""
        return LIBRARY_SIGNATURE.copy()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception as e:
                if self._enable_logging:
                    logger.error(f"Failed to close session in __exit__: {e}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.close()
        except Exception as e:
            if self._enable_logging:
                logger.error(f"Failed to close session in __aexit__: {e}")


def about() -> None:
    """Display information about the library."""
    print("=" * 60)
    print(f"📚 {LIBRARY_SIGNATURE['name']}")
    print(f"🔄 Version: {LIBRARY_SIGNATURE['version']}")
    print(f"👨‍💻 Developer: {LIBRARY_SIGNATURE['developer']}")
    print(f"📧 Email: {LIBRARY_SIGNATURE['email']}")
    print(f"🌐 Website: {LIBRARY_SIGNATURE['website']}")
    print(f"📜 License: {LIBRARY_SIGNATURE['license']}")
    print(f"💌 Message: {LIBRARY_SIGNATURE['message']}")
    print(f"🇮🇷 {LIBRARY_SIGNATURE['persian_message']}")
    print("=" * 60)


# وقتی کتابخانه import میشه، اطلاعات نمایش داده بشه
about()

# Export اصلی‌های کتابخانه
__all__ = ['Client', 'Response', 'User', 'Chat', 'Message', 'about', 'LIBRARY_SIGNATURE']