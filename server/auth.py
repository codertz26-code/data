"""
SILA DATA HACK 2026 - Authentication
Usalama na uthibitishaji
"""

import hashlib
import jwt
import datetime
import secrets
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class Authentication:
    """
    Mthibitishaji - Inasimamia access na usalama
    """
    
    def __init__(self, secret_key="SILA-SECRET-2026"):
        self.secret_key = secret_key
        self.tokens = {}
        
    def generate_token(self, username, expiry_hours=24):
        """
        Tengeneza token ya kuingia
        """
        try:
            payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours),
                'iat': datetime.datetime.utcnow(),
                'jti': secrets.token_hex(16)
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # Hifadhi token
            self.tokens[token] = {
                'username': username,
                'created': datetime.datetime.utcnow(),
                'expires': payload['exp']
            }
            
            return token
            
        except Exception as e:
            logger.error(f"Kosa katika generate_token: {e}")
            return None
    
    def verify_token(self, token):
        """
        Thibitisha token ni sahihi
        """
        try:
            if token.startswith('Bearer '):
                token = token[7:]
                
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Angalia kwenye cache
            if token in self.tokens:
                return True
                
            return False
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token imekwisha muda")
            return False
        except jwt.InvalidTokenError:
            logger.warning("Token si sahihi")
            return False
        except Exception as e:
            logger.error(f"Kosa katika verify_token: {e}")
            return False
    
    def revoke_token(self, token):
        """
        Batilisha token
        """
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def hash_password(self, password):
        """
        Tengeneza hash ya password
        """
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}${hash_obj.hexdigest()}"
    
    def verify_password(self, password, hashed):
        """
        Thibitisha password ni sahihi
        """
        try:
            salt, hash_value = hashed.split('$')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == hash_value
        except:
            return False
    
    def require_auth(self, handler_func):
        """
        Decorator kwa ajili ya endpoints zinazohitaji auth
        """
        @wraps(handler_func)
        def wrapper(self, *args, **kwargs):
            auth_header = self.headers.get('Authorization', '')
            if not self.server.auth.verify_token(auth_header):
                self.send_json_response(401, {'error': 'Haijathibitishwa'})
                return
            return handler_func(self, *args, **kwargs)
        return wrapper
