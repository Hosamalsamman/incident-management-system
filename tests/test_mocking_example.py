"""
test_mocking_example.py - Simple Mocking Examples for Beginners
================================================================

This file shows basic mocking concepts in a simple, beginner-friendly way.

What is Mocking?
----------------
Mocking is replacing a real function/object with a "fake" one for testing.

Why Mock?
---------
1. Avoid side effects (don't send real emails, don't call real APIs)
2. Make tests faster (no waiting for external services)
3. Test error conditions (simulate API failures)
4. Isolate what you're testing (test YOUR code, not external services)

When to Mock?
-------------
- External API calls (Firebase, email services, payment gateways)
- Database operations (sometimes)
- File system operations
- Time-dependent code

When NOT to Mock?
-----------------
- Your own business logic
- Simple functions that don't have side effects
- When integration testing is better
"""

from unittest.mock import patch, MagicMock
import pytest


# ===== EXAMPLE 1: Mocking a Simple Function =====

def send_email(to, subject, body):
    """This would normally send a real email"""
    print(f"Sending email to {to}: {subject}")
    # In real code, this would call an email API
    return "email_sent"


def test_send_email_mocked():
    """
    Test that send_email is called correctly without actually sending emails.
    
    This is useful because:
    - We don't want to send real emails during tests
    - We want to verify the function was called with right arguments
    """
    
    # Patch the send_email function in the correct module
    with patch('tests.test_mocking_example.send_email') as mock_send:
        # Call the function that uses send_email
        result = send_email("test@example.com", "Test", "Body")
        
        # Verify it was called
        assert mock_send.called
        # Verify it was called with specific arguments
        mock_send.assert_called_once_with("test@example.com", "Test", "Body")


# ===== EXAMPLE 2: Mocking Return Values =====

def get_user_from_api(user_id):
    """This would normally call an external API"""
    # In real code: response = requests.get(f'https://api.example.com/users/{user_id}')
    # return response.json()
    return {"id": user_id, "name": "Real User"}


def test_get_user_with_mocked_api():
    """
    Test with a mocked API response.
    
    This is useful because:
    - We don't want to depend on external API being available
    - We can test different scenarios (success, failure, etc.)
    - Tests are faster (no network calls)
    """
    
    with patch('tests.test_mocking_example.get_user_from_api') as mock_api:
        # Make the mock return a specific value
        mock_api.return_value = {"id": 123, "name": "Mocked User"}
        
        # Call the function
        result = get_user_from_api(123)
        
        # Verify we got the mocked response
        assert result == {"id": 123, "name": "Mocked User"}
        assert mock_api.called


# ===== EXAMPLE 3: Mocking Exceptions =====

def risky_operation():
    """This might fail in real life"""
    # In real code, this could fail due to network, API limits, etc.
    raise ConnectionError("API is down")


def test_risky_operation_with_exception():
    """
    Test how your code handles failures.
    
    This is useful because:
    - You can test error handling without actually causing errors
    - You can simulate rare failure conditions
    """
    
    with patch('tests.test_mocking_example.risky_operation') as mock_risky:
        # Make the mock raise an exception
        mock_risky.side_effect = ConnectionError("API is down")
        
        # Try to call it and catch the exception
        with pytest.raises(ConnectionError) as exc_info:
            risky_operation()
        
        # Verify the exception message
        assert "API is down" in str(exc_info.value)


# ===== EXAMPLE 4: Mocking Firebase (Real-world Example) =====

def send_firebase_notification(tokens, title, body):
    """This would send a real Firebase notification"""
    # In real code: firebase_admin.messaging.send_each_for_multicast(...)
    print(f"Sending Firebase notification: {title}")
    return {"success_count": len(tokens), "failure_count": 0}


def test_firebase_notification_mocked():
    """
    Test Firebase notification without actually sending notifications.
    
    This is useful because:
    - You don't want to spam real users with test notifications
    - Firebase might have rate limits
    - Tests should be isolated from external services
    """
    
    with patch('tests.test_mocking_example.send_firebase_notification') as mock_firebase:
        # Mock the response
        mock_firebase.return_value = {"success_count": 5, "failure_count": 0}
        
        # Call the function
        result = send_firebase_notification(["token1", "token2"], "Test", "Body")
        
        # Verify it was called
        assert mock_firebase.called
        assert result["success_count"] == 5


# ===== EXAMPLE 5: Mocking in Your Project Context =====

# Here's how you would mock the Firebase messaging in your actual project:

def test_dispatch_notification_mocked():
    """
    Example of mocking the Firebase messaging in routes/common.py
    
    This shows how to mock the actual Firebase call in your project.
    """
    
    # Mock the firebase_admin.messaging module
    with patch('firebase_admin.messaging.send_each_for_multicast') as mock_send:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.success_count = 5
        mock_response.failure_count = 0
        mock_response.responses = [MagicMock(success=True) for _ in range(5)]
        mock_send.return_value = mock_response
        
        # Now you can test your dispatch_notification function
        # without actually sending Firebase notifications
        from routes.common import dispatch_notification
        dispatch_notification(["token1", "token2"], "Test", "Body")
        
        # Verify Firebase was called
        assert mock_send.called


# ===== KEY CONCEPTS SUMMARY =====

"""
Mocking Cheat Sheet:
--------------------

1. @patch('module.function') - Replace a function with a mock
2. mock.return_value = x - Make the mock return x when called
3. mock.side_effect = Exception() - Make the mock raise an exception
4. mock.called - Check if the mock was called
5. mock.assert_called_with(args) - Check if called with specific arguments
6. mock.call_count - Check how many times it was called

When to use mocking in YOUR project:
------------------------------------

✅ DO mock:
- Firebase notifications (firebase_admin.messaging)
- External API calls
- Email sending
- File operations (if testing logic, not actual files)

❌ DON'T mock:
- Your own route functions (test them directly)
- Database operations (use test database instead)
- Simple utility functions

Remember: Start with integration tests (like test_users.py), 
add mocking only when you need to test external dependencies.
"""

# ===== HOW TO RUN THESE EXAMPLES =====

"""
Run these examples to see mocking in action:

    pytest tests/test_mocking_example.py -v

Each test is independent and shows a different mocking concept.
Read the comments to understand what's happening.
"""
