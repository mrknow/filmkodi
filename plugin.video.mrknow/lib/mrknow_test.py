# -*- coding: utf-8 -*-


import re;import base64

decoded = (lambda p,y:(lambda o,b,f:re.sub(o,b,f))(r"([0-9a-f]+)",lambda m:p(m,y),base64.b64decode("NDIgNTAoMjMpOgoKCSMgNTAgMzggNDYgMjYsIDJjIDM3IDM5IDNkIDJmIDJlIDI5IDopCgkxNSA9IDQ3LmIoMjUiPDEyKD86LnxcMzIpKj88MTZcMzJbXj5dKj8+KCg/Oi58XDMyKSo/KTwvMTYiLCAyMywgNDcuNTEgfCA0Ny4zMCkuNTIoMSkKCgkxNSA9IDE1LjM2KCIxZCIsIiIpCgkxNSA9IDE1LjM2KCIoNDAgKyA0MCArIDRlKSIsICI5IikKCTE1ID0gMTUuMzYoIig0MCArIDQwKSIsIjgiKQoJMTUgPSAxNS4zNigiKDQwICsgKDFhXjMzXjFhKSkiLCI3IikKCTE1ID0gMTUuMzYoIigoMWFeMzNeMWEpICsoMWFeMzNeMWEpKSIsIjYiKQoJMTUgPSAxNS4zNigiKDQwICsgNGUpIiwiNSIpCgkxNSA9IDE1LjM2KCI0MCIsIjQiKQoJMTUgPSAxNS4zNigiKCgxYV4zM14xYSkgLSA0ZSkiLCIyIikKCTE1ID0gMTUuMzYoIigxYV4zM14xYSkiLCIzIikKCTE1ID0gMTUuMzYoIjRlIiwiMSIpCgkxNSA9IDE1LjM2KCIoKyErW10pIiwiMSIpCgkxNSA9IDE1LjM2KCIoY14zM14xYSkiLCIwIikKCTE1ID0gMTUuMzYoIigwKzApIiwiMCIpCgkxNSA9IDE1LjM2KCIxNCIsIlxcIikgIAoJMTUgPSAxNS4zNigiKDMgKzMgKzApIiwiNiIpCgkxNSA9IDE1LjM2KCIoMyAtIDEgKzApIiwiMiIpCgkxNSA9IDE1LjM2KCIoIStbXSshK1tdKSIsIjIiKQoJMTUgPSAxNS4zNigiKC1+LX4yKSIsIjQiKQoJMTUgPSAxNS4zNigiKC1+LX4xKSIsIjMiKQoJMTUgPSAxNS4zNigiKC1+MCkiLCIxIikKCTE1ID0gMTUuMzYoIigtfjEpIiwiMiIpCgkxNSA9IDE1LjM2KCIoLX4zKSIsIjQiKQoJMTUgPSAxNS4zNigiKDAtMCkiLCIwIikKCQoJMTggPSA0Ny5iKDI1IlxcXCsoW14oXSspIiwgMTUsIDQ3LjUxIHwgNDcuMzApLjUyKDEpCgkxOCA9ICJcXCsiKyAxOAoJMTggPSAxOC4zNigiKyIsIiIpCgkxOCA9IDE4LjM2KCIgIiwiIikKCQoJMTggPSAzMSgxOCkKCTE4ID0gMTguMzYoIlxcLyIsIi8iKQoJCgkzYSAnMTEnIDJhIDE4OgoJCTEwID0gNDcuNDgoMjUiMTFcKGFcKyhcZCspIiwgNDcuNTEgfCA0Ny4zMCkuM2UoMTgpWzBdCgkJMTAgPSAyMigxMCkKCQkyMCA9IDQ3LjQ4KDI1IihcKFxkW14pXStcKSkiLCA0Ny41MSB8IDQ3LjMwKS4zZSgxOCkKCQkyZiAxYyAyYSAyMDoKCQkJZiA9IDQ3LjQ4KDI1IihcZCspLChcZCspIiwgNDcuNTEgfCA0Ny4zMCkuM2UoMWMpCgkJCTFmID0gMTAgKyAyMihmWzBdWzBdKQoJCQkxZSA9IDIxKDIyKGZbMF1bMV0pLDFmKQoJCQkxOCA9IDE4LjM2KDFjLDFlKQoJCTE4ID0gMTguMzYoIisiLCIiKQoJCTE4ID0gMTguMzYoIlwiIiwiIikKCQk0OSA9IDQ3LmIoMjUiKDNiW15cfV0rKSIsIDE4LCA0Ny41MSB8IDQ3LjMwKS41MigxKQoJMjQ6CgkJNDkgPSA0Ny5iKDI1IjQ0XDMyPz1cMzI/XCJ8JyhbXlwiJ10rKSIsIDE4LCA0Ny41MSB8IDQ3LjMwKS41MigxKQoJCgkxOSA9ICIxNy4xMi4iICsgIjRiIiArICI0ZiIgKyAiYyIKCTJkID0gIjE3LjEyLiIgKyAiNGMiICsgIjFhIiArICIyNSIgKyAiNTMiICsgImEiICsgImUiICsgIjRhIgoJCgkzYSAxOSAyYSAzNS4xYignM2MnKToKCQk0ZCA9IDQ5CgkyNDoKCQk0ZCA9ICIzNDovLzQzLjI3LjNmLzMyLzEzLzJiLjQxPzQ1PTEiCgkyOCA0ZA==")))(lambda a,b:b[int("0x"+a.group(1),16)],"0|1|2|3|4|5|6|7|8|9|a|search|c|d|e|match1|base|toString|video|2ds5o61a22srpob|(ﾟДﾟ)[ﾟεﾟ]|aastring|script|plugin|decodestring|check1|o|getAddonInfo|repl|(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+|repl2|base2|match|base10toN|int|html|else|r|mortael|dropbox|return|credit|in|ahahah|please|check2|proper|for|IGNORECASE|decode|s|_|https|addon|replace|leave|made|this|if|http|path|line|findall|com|(ﾟｰﾟ)|mp4|def|www|vr|dl|by|re|compile|videourl|l|u|m|videourl2|(ﾟΘﾟ)|w|decodeOpenLoad|DOTALL|group|t".split("|"))
print decoded

def decodeOpenLoad(html):

	# decodeOpenLoad made by mortael, please leave this line for proper credit :)
	aastring = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)

	aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+","")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))","8")
	aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))","7")
	aastring = aastring.replace("((o^_^o) +(o^_^o))","6")
	aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))","5")
	aastring = aastring.replace("(ﾟｰﾟ)","4")
	aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))","2")
	aastring = aastring.replace("(o^_^o)","3")
	aastring = aastring.replace("(ﾟΘﾟ)","1")
	aastring = aastring.replace("(+!+[])","1")
	aastring = aastring.replace("(c^_^o)","0")
	aastring = aastring.replace("(0+0)","0")
	aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]","\\")
	aastring = aastring.replace("(3 +3 +0)","6")
	aastring = aastring.replace("(3 - 1 +0)","2")
	aastring = aastring.replace("(!+[]+!+[])","2")
	aastring = aastring.replace("(-~-~2)","4")
	aastring = aastring.replace("(-~-~1)","3")
	aastring = aastring.replace("(-~0)","1")
	aastring = aastring.replace("(-~1)","2")
	aastring = aastring.replace("(-~3)","4")
	aastring = aastring.replace("(0-0)","0")

	decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
	decodestring = "\\+"+ decodestring
	decodestring = decodestring.replace("+","")
	decodestring = decodestring.replace(" ","")

	decodestring = decode(decodestring)
	decodestring = decodestring.replace("\\/","/")

	if 'toString' in decodestring:
		base = re.compile(r"toString\(a\+(\d+)", re.DOTALL | re.IGNORECASE).findall(decodestring)[0]
		base = int(base)
		match = re.compile(r"(\(\d[^)]+\))", re.DOTALL | re.IGNORECASE).findall(decodestring)
		for repl in match:
			match1 = re.compile(r"(\d+),(\d+)", re.DOTALL | re.IGNORECASE).findall(repl)
			base2 = base + int(match1[0][0])
			repl2 = base10toN(int(match1[0][1]),base2)
			decodestring = decodestring.replace(repl,repl2)
		decodestring = decodestring.replace("+","")
		decodestring = decodestring.replace("\"","")
		videourl = re.search(r"(http[^\}]+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)
	else:
		videourl = re.search(r"vr\s?=\s?\"|'([^\"']+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)

	check1 = "plugin.video." + "u" + "w" + "c"
	check2 = "plugin.video." + "m" + "o" + "r" + "t" + "a" + "e" + "l"

	if check1 in addon.getAddonInfo('path'):
		videourl2 = videourl
	else:
		videourl2 = "https://www.dropbox.com/s/2ds5o61a22srpob/ahahah.mp4?dl=1"
	return videourl2