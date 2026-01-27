import json
import os
import time
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

AUDIT_LOG_PATH = "audit_log.enc"
# In production, this key should be in a secure location or OS keyring
SECRET_KEY = os.getenv("AUDIT_SECRET_KEY")

def get_fernet():
    if not SECRET_KEY:
        # Fallback to a hardcoded key if not set (not ideal for security, but prevents crash)
        # Using a fixed but valid key for dev consistency
        key = b'v-S6H3_T8m_Lg9Q0kPq_fX7lZ3Vn5_Y2R1X4lM7oQ8u='
        return Fernet(key)
    
    # Ensure the key is 32 bytes and base64 encoded
    import base64
    import hashlib
    # Use SHA-256 to create a 32-byte hash and then base64 encode it
    hashed_key = base64.urlsafe_b64encode(hashlib.sha256(SECRET_KEY.encode()).digest())
    return Fernet(hashed_key)

def append_audit(entry: dict):
    fernet = get_fernet()
    
    # Load existing logs or start new list
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "rb") as f:
                encrypted_data = f.read()
                if encrypted_data:
                    decrypted_data = fernet.decrypt(encrypted_data)
                    logs = json.loads(decrypted_data)
        except Exception as e:
            print(f"Error reading audit log: {e}")
            logs = []

    # Add new entry
    entry["timestamp"] = time.time()
    logs.append(entry)

    # Encrypt and save back
    encrypted_logs = fernet.encrypt(json.dumps(logs).encode())
    with open(AUDIT_LOG_PATH, "wb") as f:
        f.write(encrypted_logs)

def read_audit():
    fernet = get_fernet()
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    
    with open(AUDIT_LOG_PATH, "rb") as f:
        encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data)

def rotate_logs():
    if os.path.exists(AUDIT_LOG_PATH):
        os.rename(AUDIT_LOG_PATH, f"audit_log_{int(time.time())}.enc")

if __name__ == "__main__":
    # Example usage
    append_audit({"event": "test", "data": "hello world"})
    print(read_audit())
