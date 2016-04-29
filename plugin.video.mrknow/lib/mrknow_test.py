import urllib
import requests, re

src='http://iklub.net/c+sm.html'
r = requests.get(src)
print('srcIklub: %s' % r.text)
marian = re.compile(
    'eval\(unescape\(\'([^\']+)\'\)\);\s.*eval\(unescape\(\'([^\']+)\'\).*\'([^\']+)\'.*?unescape\(\'([^\']+)\'\)\);').findall(
    r.text)
print('Malina: %s ' % urllib.unquote(marian[0][0]))
mysplit = re.compile('s\.split\("([^"]+)"').findall(urllib.unquote(marian[0][0]))[0]
myadd = re.compile('unescape\(tmp\[1\] \+ "([^"]+)"\)').findall(urllib.unquote(marian[0][0]))[0]
myadd2 = re.compile('charCodeAt\(i\)\)\+(.*?)\)\;').findall(urllib.unquote(marian[0][0]))[0]

print("myadd", myadd,int(myadd2), marian[0][0])
mystring = urllib.unquote(marian[0][2])
ile = mystring.split(str(mysplit));
k = ile[1] + str(myadd)
print("Ile", ile[1], k)
alina = []
# for y in k:
#    print("y",y)

for i in range(0, len(mystring)):
    aa = ord(mystring[i])
    bb = int(k[i % len(k)])
    alina.append((bb ^ aa) + int(myadd2))

malina = ''.join(map(chr, alina))
print('Malina: %s ' % malina)
