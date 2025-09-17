"""
Unit tests for error handling in EitaaYar client
"""

import unittest
from unittest.mock import Mock, patch
from eitaayar import Client, Response


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = Client("test_token", enable_logging=False)

    def test_error_type_detection(self):
        """Test error type detection in responses"""
        test_cases = [
            # (error_message, expected_error_type)
            ("method not found", "METHOD_NOT_FOUND"),
            ("invalid token", "INVALID_TOKEN"),
            ("chat not found", "CHAT_NOT_FOUND"),
            ("request timeout", "TIMEOUT"),
            ("network error", "NETWORK_ERROR"),
            ("not implemented", "METHOD_NOT_IMPLEMENTED"),
            ("file upload failed", "FILE_ERROR"),
            ("message too long", "MESSAGE_ERROR"),
            ("unknown error", None),  # Should return None for unknown errors
        ]
        
        for error_msg, expected_type in test_cases:
            with self.subTest(error_msg=error_msg):
                response = Response({
                    "ok": False,
                    "error": error_msg
                }, enable_logging=False)
                
                self.assertEqual(response.error_type, expected_type)

    @patch('eitaayar.requests.post')
    def test_network_error_handling(self, mock_post):
        """Test network error handling"""
        mock_post.side_effect = Exception("Network connection failed")
        
        response = self.client.get_me()
        
        self.assertFalse(response.ok)
        self.assertIn("Network connection failed", response.error)
        self.assertEqual(response.error_type, "NETWORK_ERROR")

    @patch('eitaayar.requests.post')
    def test_timeout_error_handling(self, mock_post):
        """Test timeout error handling"""
        from requests.exceptions import Timeout
        mock_post.side_effect = Timeout("Request timed out")
        
        response = self.client.get_me()
        
        self.assertFalse(response.ok)
        self.assertIn("Request timeout", response.error)
        self.assertEqual(response.error_type, "TIMEOUT")

    def test_raise_for_status(self):
        """Test raise_for_status method"""
        success_response = Response({"ok": True}, enable_logging=False)
        error_response = Response({
            "ok": False,
            "error": "Test error",
            "error_code": 500,
            "error_type": "TEST_ERROR"
        }, enable_logging=False)
        
        # Should not raise for successful response
        success_response.raise_for_status()
        
        # Should raise for error response
        with self.assertRaises(Exception) as context:
            error_response.raise_for_status()
        
        self.assertIn("Test error", str(context.exception))
        self.assertIn("500", str(context.exception))
        self.assertIn("TEST_ERROR", str(context.exception))


class TestDocumentFallback(unittest.TestCase):
    """Test document send fallback functionality"""

    @patch('eitaayar.requests.post')
    def test_send_document_fallback(self, mock_post):
        """Test document send fallback when method not found"""
        client = Client("test_token", enable_logging=False)
        
        # Mock first response (method not found)
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "ok": False,
            "error": "method not found",
            "error_code": 404
        }
        
        # Mock second response (fallback message success)
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "ok": True,
            "result": {
                "message_id": 1001,
                "text": "📁 فایل: test.txt"
            }
        }
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        response = client.send_document(
            chat_id=12345,
            file=b"test content",
            filename="test.txt",
            caption="Test caption"
        )
        
        self.assertTrue(response.ok)
        self.assertEqual(response.message_id, 1001)
        # Verify that fallback was used (two calls to post)
        self.assertEqual(mock_post.call_count, 2)


if __name__ == "__main__":
    unittest.main()