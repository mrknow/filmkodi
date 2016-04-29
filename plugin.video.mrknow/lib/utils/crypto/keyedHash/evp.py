# -*- coding: iso-8859-1 -*-

def EVP_BytesToKey(md, data, salt, keyLength, ivLength, count):
    assert(data)
    assert(keyLength > 0)
    assert(ivLength >= 0)
    if salt:
        assert(len(salt) == 8)
    assert(count >= 1)

    key = iv = hashed = ''

    while 1:
        m = md()
        if hashed:
            m.update(hashed)
        m.update(data)
        if salt:
            m.update(salt)
        hashed = m.digest()

        for i in xrange(count-1):
            m = md()
            m.update(hashed)
            hashed = m.digest()

        keyNeeds = keyLength - len(key)
        tmp = hashed
        if keyNeeds > 0:
            key += tmp[:keyNeeds]
            tmp = tmp[keyNeeds:]
        ivNeeds = ivLength - len(iv)
        if tmp and (ivNeeds > 0):
            iv += tmp[:ivNeeds]

        if keyNeeds == ivNeeds == 0:
            break

    return key, iv