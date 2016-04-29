import M2Crypto
import base64

class GenericError(Exception):
    def __init__(self, message=None, errno=0):
        Exception.__init__(self)
        self.message = message
        self.errno   = errno

class CryptoError(GenericError):
    def __init__(self, message=None, errno=0):
        GenericError.__init__(self, message, errno)

class MyCrypto():
    def __init__(self,aesKey ='',aesIv='',aesSalt =''):
        self.aesKey = aesKey
        self.aesIv = aesIv
        self.aesSalt = aesSalt

    def aesEncrypt(self, message):
        try:
            cipher = self.__aesGetCipher(self.ENCRYPT)
            encMessage = cipher.update(message)
            return encMessage + cipher.final()
        except M2Crypto.EVP.EVPError as evpe:
            raise CryptoError(str(evpe))

    def aesDecrypt(self, message,op=0):
        try:
            cipher = self.__aesGetCipher(op)
            decMessage = cipher.update(message)
            return decMessage + cipher.final()
        except M2Crypto.EVP.EVPError as evpe:
            raise CryptoError(str(evpe))

    def __aesGetCipher(self, op):
        return M2Crypto.EVP.Cipher(alg='aes_128_cbc', key=self.aesKey, iv=self.aesIv, salt=self.aesSalt, d='md5', op=op)

import binascii
ct="AtlECKf6jf4+BQXns+RUsZXybu2pLizxWDavCf+Z+Ck="
iv="d4c5eebe0039dfed03c262f34aa110ef"
s="9c43d5350eb986e8"
password="number-one"

ala= MyCrypto(binascii.hexlify('number-one'),iv,s)
print ala.aesDecrypt(base64.b64decode(ct),1)

print "dupa"
#print ct.decode('base64')
#print base64.b64decode(ct)

#print binascii.unhexlify('number-one')
#print binascii.hexlify('number-one')