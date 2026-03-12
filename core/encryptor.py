"""
SILA DATA HACK 2026 - Data Encryptor
Usalama wa data - Encryption na decryption
"""

import hashlib
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging

logger = logging.getLogger(__name__)

class DataEncryptor:
    """
    Kisimbaji Data - Inalinda data kwa encryption
    """
    
    def __init__(self, enabled=True, key=None, password="SILA-SECRET-KEY-2026"):
        self.enabled = enabled
        self.key = self._generate_key(password) if enabled else None
        self.cipher = Fernet(self.key) if self.key else None
        
    def _generate_key(self, password):
        """Tengeneza key kutoka kwa password"""
        try:
            # Tumia PBKDF2 kutoa key thabiti
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'sila_salt_2026',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
        except Exception as e:
            logger.error(f"Kosa katika key generation: {e}")
            return Fernet.generate_key()
    
    def encrypt_data(self, data):
        """Simba data"""
        if not self.enabled or not self.cipher:
            return data
            
        try:
            # Geuza data kuwa string
            if isinstance(data, dict):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
                
            # Simba
            encrypted = self.cipher.encrypt(data_str.encode())
            
            return {
                '_encrypted': True,
                'data': base64.urlsafe_b64encode(encrypted).decode('utf-8'),
                'timestamp': data.get('timestamp') if isinstance(data, dict) else None
            }
            
        except Exception as e:
            logger.error(f"Kosa katika encrypt_data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data):
        """Fungua data iliyosimbwa"""
        if not self.enabled or not self.cipher:
            return encrypted_data
            
        try:
            # Angalia kama ni data iliyosimbwa
            if isinstance(encrypted_data, dict) and encrypted_data.get('_encrypted'):
                encrypted_bytes = base64.urlsafe_b64decode(encrypted_data['data'])
                decrypted = self.cipher.decrypt(encrypted_bytes)
                data = json.loads(decrypted.decode())
                return data
                
        except Exception as e:
            logger.error(f"Kosa katika decrypt_data: {e}")
            
        return encrypted_data
    
    def hash_string(self, text):
        """Tengeneza hash ya string"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def verify_integrity(self, data, original_hash):
        """Thibitisha data haijabadilishwa"""
        current_hash = self.hash_string(json.dumps(data))
        return current_hash == original_hash
