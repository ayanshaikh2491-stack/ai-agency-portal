from api_client import ask_ai
result = ask_ai([{"role": "user", "content": "hello"}])
print(result)