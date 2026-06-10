# Testing Guide for Beginners

## What is Testing?

Testing is simply checking that your code works as expected. Instead of manually clicking through your app and checking if things work, you write code that automatically checks it for you.

### Why Test?

1. **Catch bugs early** - Tests find bugs before your users do
2. **Confidence** - Make changes without breaking things
3. **Documentation** - Tests show how your code should work
4. **Interview requirement** - Employers want to see you know how to test

## What is Pytest?

Pytest is a Python testing framework. It makes writing tests easy and readable.

### Installing Pytest

```bash
pip install pytest pytest-flask
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output (shows test names)
pytest -v

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_login_get

# Run with print statements visible
pytest -v -s

# Stop on first failure
pytest -x

# Show detailed output on failure
pytest -vv
```

## Understanding the Test Structure

### Test File: `tests/test_users.py`

Each test function follows this pattern:

```python
def test_something(client, db_session):
    # 1. ARRANGE - Set up test data
    user = create_test_user()
    
    # 2. ACT - Run the code you're testing
    response = client.post('/login', json={...})
    
    # 3. ASSERT - Check the result
    assert response.status_code == 200
```

### What are Fixtures?

Fixtures are reusable setup functions. They're defined in `conftest.py`.

**Common fixtures we use:**

- `app` - Creates a test Flask app with in-memory database
- `client` - Simulates a browser for making HTTP requests
- `db_session` - Gives access to the test database
- `test_user` - Creates a test user automatically
- `auth_headers` - Creates authentication headers with JWT token

**Why fixtures?**
- Don't repeat setup code in every test
- Tests are cleaner and easier to read
- Changes to setup happen in one place

## Test Database vs Real Database

**Important:** Tests use a SEPARATE in-memory database. This means:

- ✅ Tests don't mess up your real data
- ✅ Tests are fast (no file I/O)
- ✅ Each test starts fresh (database is empty)
- ✅ Changes are rolled back after each test

## Understanding Mocking (Beginner Friendly)

### What is Mocking?

Mocking is replacing a real component with a fake one for testing.

**Example:** Your code sends emails. In tests, you don't want to actually send emails. So you "mock" the email function to just pretend to send emails.

### When to Mock?

Mock when you want to:
- Avoid side effects (sending emails, calling external APIs)
- Make tests faster
- Test error conditions (simulate API failures)
- Isolate what you're testing

### Simple Mock Example

```python
from unittest.mock import patch

# This replaces the real function with a fake one
@patch('routes.common.send_to_group')
def test_notification_sends(mock_send):
    # Call your function
    result = some_function()
    
    # Check that the mocked function was called
    assert mock_send.called
```

### Don't Worry About Complex Mocking Yet!

For now, focus on:
1. Testing your routes with the test database
2. Testing happy paths (when things work)
3. Testing error cases (wrong password, duplicate user, etc.)

You can add mocking later when you need it.

## Reading Test Output

### Success Output:
```
tests/test_users.py::test_login_get PASSED
tests/test_users.py::test_login_success PASSED
...
========================= 10 passed in 2.5s =========================
```

### Failure Output:
```
tests/test_users.py::test_login_wrong_credentials FAILED
========================= FAILURES =========================
________________ test_login_wrong_credentials ________________
    assert response.status_code == 401
AssertionError: assert 200 == 401
```

This means:
- Test expected status code 401
- But got 200 instead
- Something is wrong with your error handling

## Writing Your Own Tests

### Step 1: Identify what to test

Look at your route and ask:
- What should happen when it works? (happy path)
- What should happen with invalid input? (error cases)
- What should happen with missing data? (edge cases)

### Step 2: Write the test

```python
def test_my_new_route(client, db_session):
    # Arrange: Create test data
    # ...
    
    # Act: Call your route
    response = client.get('/my-route')
    
    # Assert: Check result
    assert response.status_code == 200
```

### Step 3: Run the test

```bash
pytest tests/test_my_file.py::test_my_new_route -v
```

### Step 4: Fix if it fails

If the test fails:
1. Read the error message
2. Check your code
3. Fix the code or fix the test
4. Run again

## Common Test Patterns

### Testing GET requests:
```python
response = client.get('/some-route')
assert response.status_code == 200
data = json.loads(response.data)
assert "key" in data
```

### Testing POST requests:
```python
response = client.post('/some-route', json={'key': 'value'})
assert response.status_code == 200
```

### Testing errors:
```python
response = client.post('/login', json={'wrong': 'data'})
assert response.status_code == 401  # or 400, 403, etc.
data = json.loads(response.data)
assert "error" in data
```

### Testing authenticated routes:
```python
def test_protected_route(client, auth_headers):
    response = client.get('/protected', headers=auth_headers)
    assert response.status_code == 200
```

## Interview Talking Points

When asked about testing, you can say:

1. **"I use pytest for testing. It's simple and readable."**
2. **"I write integration tests that use a test database to check my routes work correctly."**
3. **"I use fixtures to set up test data, so I don't repeat code."**
4. **"I test both success cases and error cases."**
5. **"Tests give me confidence when making changes to the codebase."**

## Next Steps

1. ✅ Run the existing tests: `pytest -v`
2. ✅ Read through `test_users.py` to understand the patterns
3. ✅ Try adding a new test for a route you wrote
4. ✅ Learn mocking when you need to test external services
5. ✅ Add tests for your other routes (incidents, GIS, etc.)

## Resources

- Pytest documentation: https://docs.pytest.org/
- Flask testing: https://flask.palletsprojects.com/en/latest/testing/
- Python unittest.mock: https://docs.python.org/3/library/unittest.mock.html

## Don't Be Frustrated!

Testing is a skill that takes time to learn. The fact that you're adding tests now shows you're improving. Interviewers appreciate this effort!

Start simple, focus on the basics, and gradually learn more advanced concepts like mocking.
