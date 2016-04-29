from base64 import b64encode, b64decode
from M2Crypto.EVP import Cipher

__all__ = ['encryptor', 'decryptor']

ENC=1
DEC=0

def build_cipher(key, iv, op=ENC):
    """"""""
    return Cipher(alg='aes_128_cbc', key=key, iv=iv, op=op)

def encryptor(key, iv=None):
    """"""
    # Decode the key and iv
    key = b64decode(key)
    if iv is None:
        iv = '\0' * 16
    else:
        iv = b64decode(iv)

   # Return the encryption function
    def encrypt(data):
        cipher = build_cipher(key, iv, ENC)
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
        v = b64encode(v)
        return v
    return encrypt

def decryptor(key, iv=None):
    """"""
    # Decode the key and iv
    key = b64decode(key)
    if iv is None:
        iv = '\0' * 16
    else:
        iv = b64decode(iv)

   # Return the decryption function
    def decrypt(data):
        data = b64decode(data)
        cipher = build_cipher(key, iv, DEC)
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
        return v
    return decrypt