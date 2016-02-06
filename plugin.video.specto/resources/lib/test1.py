
import re,urllib,urlparse


from libraries import cleantitle
from libraries import client

result = """
<li><a class="search-for zme-autocomplete-activeItem" href="search/mad max">Search "mad max</a></li><br><li><a href="http://watch1080p.com/watch/mad-max-fury-road_ieo7a/"><img width="35" height="45" class="search-img" alt="" src="https://lh3.googleusercontent.com/-h_jfa8GsOvs/Vi1cle3xPkI/AAAAAAAAA9U/Qb60eTDlcKw/s317/image.jpg"><strong>Mad Max: Fury Road</strong><br><br class="clr"></a></li>
"""
#print(">>>Result - 1<<<",result)

result = client.parseDOM(result, 'li')
t1 =client.parseDOM(result[1], 'a' ,ret='href')
print(">>>Result - 2<<<",t1)
print(">>>",client.parseDOM(result[1], 'a' ,ret='href'))
print(">>>",re.sub('<.+?>|</.+?>','', client.parseDOM(result[1], 'a')[0]))

t2 = re.compile('//.+?(/.+)').findall(t1[0])
print("s",t2)