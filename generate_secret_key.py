import secrets

def generate_secret_key(length: int = 32) -> str:
    return secrets.token_hex(length)

secret_key = generate_secret_key()

with open(".env", "w") as f:
    f.write(f"SECRET_KEY={secret_key}\n")

print(f"Secret Key generated and saved to .env: {secret_key}")