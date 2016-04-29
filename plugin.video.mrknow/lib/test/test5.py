import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES,AES_CBC

class AESCipher(object):

    def __init__(self, key): 
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


#from Plugins.Extensions.IPTVPlayer.libs.crypto.cipher.aes_cbc import AES_CBC
from hashlib import md5
import binascii


def CryptoJS_AES_decrypt(encrypted, password, key_length=32):
    def derive_key_and_iv(password, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length + iv_length]

    bs = 16
    salt = encrypted[len('Salted__'):bs]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES_CBC(key=key, keySize=32)
    return cipher.decrypt(encrypted[bs:], iv)

ct="AtlECKf6jf4+BQXns+RUsZXybu2pLizxWDavCf+Z+Ck="
iv="d4c5eebe0039dfed03c262f34aa110ef"
s="9c43d5350eb986e8"

password="number-one"

streamUrl = byteify(json.loads(window['streamUrl']))
ciphertext = base64.b64decode(streamUrl['ct'])
iv = a2b_hex(streamUrl['iv'])
salt = a2b_hex(streamUrl['s'])

url = self.cryptoJS_AES_decrypt(ciphertext, 'number-one', salt)
baseUrl = byteify(json.loads(url))
url = baseUrl + "/stream/get?id=" + window['streamId'] + "&token=" + window['streamToken']