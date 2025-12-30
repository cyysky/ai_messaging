from auth.utils import create_access_token, decode_token

token = create_access_token(1, 'test')
print("TOKEN:", token)

result = decode_token(token)
print("RESULT:", result)

if result is None:
    print("ERROR: decode_token returned None")
    # Debug
    from jose import jwt, JWTError
    from auth.utils import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Manual decode worked:", payload)
    except JWTError as e:
        print("JWT Error:", e)
else:
    print("SUCCESS: Token decoded successfully")
    print("Payload:", result)