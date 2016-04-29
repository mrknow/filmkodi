import sys
import hashlib
import string
import struct
import logging
#from utils import lazy_property

class lazy_property(object):

    """
    be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fget):
        self.func_name = fget.__name__
        self.fget = fget

    def __get__(self, obj, cls):
        if obj is None:
            return
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value

logger = logging.getLogger('crypto')


def random_string(length):
    import M2Crypto.Rand
    return M2Crypto.Rand.rand_bytes(length)


def get_table(key):
    m = hashlib.md5()
    m.update(key)
    s = m.digest()
    (a, b) = struct.unpack('<QQ', s)
    table = [c for c in string.maketrans('', '')]
    for i in xrange(1, 1024):
        table.sort(lambda x, y: int(a % (ord(x) + i) - a % (ord(y) + i)))
    encrypt_table = ''.join(table)
    decrypt_table = string.maketrans(encrypt_table, string.maketrans('', ''))
    return encrypt_table, decrypt_table


def EVP_BytesToKey(password, key_len, iv_len):
    # equivalent to OpenSSL's EVP_BytesToKey() with count 1
    # so that we make the same key and iv as nodejs version
    # TODO: cache the results
    m = []
    i = 0
    while len(''.join(m)) < (key_len + iv_len):
        md5 = hashlib.md5()
        data = password
        if i > 0:
            data = m[i - 1] + password
        md5.update(data)
        m.append(md5.digest())
        i += 1
    ms = ''.join(m)
    key = ms[:key_len]
    iv = ms[key_len:key_len + iv_len]
    return (key, iv)




class Crypto(object):

    METHOD_SUPPORTED = {
    'aes-128-cfb': (16, 16),
    'aes-128-cbc': (16, 16),
    'aes-192-cfb': (24, 16),
    'aes-256-cfb': (32, 16),
    'bf-cfb': (16, 8),
    'camellia-128-cfb': (16, 16),
    'camellia-192-cfb': (24, 16),
    'camellia-256-cfb': (32, 16),
    'cast5-cfb': (16, 8),
    'des-cfb': (8, 8),
    'idea-cfb': (16, 8),
    'rc2-cfb': (16, 8),
    'rc4': (16, 0),
    'seed-cfb': (16, 16),
    }

    method = None
    key = None
    encrypt_table = decrypt_table = None

    @classmethod
    def init_table(cls, key, method):
        cls.method = None if method == 'table' else method.lower()
        cls.key = key
        if cls.method:
            try:
                __import__('M2Crypto')
            except ImportError:
                logger.error(
                    'M2Crypto is required to use encryption other than default method')
                sys.exit(1)
        if method:
            cls.encrypt_table, cls.decrypt_table = get_table(key)
        else:
            try:
                # make an Encryptor to test if the settings if OK
                Crypto()
            except Exception as e:
                logger.error(e)
                sys.exit(1)

    def __init__(self):
        self.iv = None
        self.iv_sent = False
        self.cipher_iv = ''
        self.decipher = None
        self.cipher = None
        self.set_cihper()
        self.salt = None
        self.key = ''

    @lazy_property
    def cipher_len(self):
        return self.METHOD_SUPPORTED.get(self.method, None)

    @property
    def iv_len(self):
        return len(self.cipher_iv)

    def set_cihper(self):
        if self.method:
            self.cipher = self.get_cipher(iv=random_string(32), op=1)

    def get_cipher(self, iv=None, op=0):
        import M2Crypto.EVP
        password = self.key.encode('utf-8')
        method = self.method
        m = self.cipher_len
        print("m:",m,method,password)
        if m:
            key, iv_ = EVP_BytesToKey(password, m[0], m[1])
            print("A:",key,iv)
            if iv is None:
                iv = iv_[:m[1]]
            if op == 1:
                # this iv is for cipher, not decipher
                self.cipher_iv = iv[:m[1]]
            return M2Crypto.EVP.Cipher(method.replace('-', '_'),
                    key, iv, op, key_as_bytes=0, d='md5', salt=self.salt, i=1, padding=1)

        logger.error('method %s not supported' % method)
        sys.exit(1)

    def encrypt(self, buf):
        if len(buf) == 0:
            return buf
        if self.method is None:
            return string.translate(buf, self.encrypt_table)
        else:
            if self.iv_sent:
                return self.cipher.update(buf)
            else:
                self.iv_sent = True
                return self.cipher_iv + self.cipher.update(buf)

    def decrypt(self, buf):
        if len(buf) == 0:
            return buf
        if self.method is None:
            return string.translate(buf, self.decrypt_table)
        else:
            if self.decipher is None:
                decipher_iv_len = self.cipher_len[1]
                decipher_iv = buf[:decipher_iv_len]
                self.decipher = self.get_cipher(iv=decipher_iv)
                buf = buf[decipher_iv_len:]
                if len(buf) == 0:
                    return buf
            return self.decipher.update(buf)


def setup_table(key, method='table'):
    Crypto.init_table(key, method)


def new_crypto():
    return Crypto()
import base64

ct="AtlECKf6jf4+BQXns+RUsZXybu2pLizxWDavCf+Z+Ck="
iv="d4c5eebe0039dfed03c262f34aa110ef"
s="9c43d5350eb986e8"

password="number-one"
ala = new_crypto()
ala.init_table("number-one",'aes-128-cfb')
ala.iv = iv
ala.salt = s
ala.key = password
print ala.decrypt(base64.b64decode(ct))

print "dupa"