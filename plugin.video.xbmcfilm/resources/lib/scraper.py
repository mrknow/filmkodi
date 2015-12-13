import	urllib2 
import	re
from	time import localtime, strftime, gmtime
from	BeautifulSoup import BeautifulStoneSoup,BeautifulSoup, NavigableString
import collections


def geturl(url):
	#, headers = {"Accept-Encoding":"gzip"}
	print "getting: %s" % url
	return  urllib2.urlopen(urllib2.Request(url)).read().decode('iso-8859-1', 'ignore').encode('ascii', 'ignore')

def jsonc(st):
	for i,o in (
		('true', 'True'),
		('false', 'False')
	):
		st = st.replace(i,o)
	return eval(st)


class MenuItems(object):
	def __init__(self):
		self.base				= 'http://www.sbs.com.au/ondemand/'
		self.main_txt			= re.sub(r'^[^=]+=','', geturl(self.base + 'js/video-menu'))
		self.main				= jsonc(self.main_txt)
		if 0:
			import pprint
			pprint.pprint(self.main)
		self.cache				= {}
		self.cache[tuple([])]	= {"url"		: None, "children" : self.__menu([], self.main.values())}
		print self.main

	def __menu(self, parent, items):
		out = []
		if isinstance(items, dict):
			items = items.values()
			
		for item in items:
			if "name" in item:
				name		= tuple(list(parent) + [item["name"]])
				children	= item.get("children", [])
				if "url" in item:
					url			= "http://www.sbs.com.au%s" % (re.sub(r'%([0-9,A-F,a-f]{2})', lambda m : chr(int(m.group(1),16)), item["url"].replace("\\", "")))

					if children:
						self.cache[name]				= {"url"	:  None, "children" : 	self.__menu(name, children)}
						alli 							= tuple(list(name) + ["All Items"])
						self.cache[alli]				= {"url"	: url, "children" : []}
						self.cache[name]["children"]	= [alli] + self.cache[name]["children"]
					else:
						self.cache[name]				= {"url"	:  url, "children" : []}
				
					out.append(name)
				else:
					print ("!!", item)

		return out


	def menu_main(self, *args):
		if not len(args):
			args = [[]]

		return self.cache[tuple(args[0])]


	def menu_shows(self, st):
		print st
		for entry in sorted(jsonc(geturl(st))["entries"], key = lambda x: x["title"]):
			hours, remainder = divmod(int(entry["media$content"][0]['plfile$duration']), 3600)
			minutes, seconds = divmod(remainder, 60)
			#entry["description"], entry['plmedia$defaultThumbnailUrl']
			
			rec  =  {
				"title" 		: entry["title"],
				"thumbnail"		: entry["plmedia$defaultThumbnailUrl"],
				"url"			: 'http://www.sbs.com.au/ondemand/video/%s' % entry["id"].split('/')[-1],
				"info"			: {
					"Country "	: entry.get("pl1$countryOfOrigin", "?"),
					"plot"		: entry["description"],
					"duration"	: "%s:%s:%s" % (hours, minutes, seconds),
					"date"		: strftime("%d.%m.%Y",gmtime(entry["pubDate"]/1000)),
					"genre"		: "%s,%s" % (entry.get("pl1$countryOfOrigin", "?"), entry["media$keywords"]),
				}
			}
			try:
				rec["info"]["mpaa"]		= entry["media$ratings"][0]['rating']
			except Exception,e:
				rec["info"]["mpaa"]		= '?'
			yield rec

	def menu_play(self, lk):
		print lk
		contents = geturl(lk)
		out = {}
		fmt = None
		for mtch in re.findall(r'^[ \t]+player.releaseUrl = "(.*)";', contents, re.MULTILINE):
			contents2 =  geturl(mtch)
			print contents2
			soup = BeautifulSoup(contents2)
			
			if contents2.find('.flv') > -1:
				fmt = '.flv'			
				for item in soup.findAll('video'):
					out[int(item["system-bitrate"])] = item["src"]
			else:
				fmt = '.mp4'
				vals = {}
				if str(soup).find('akamaihd') <= -1:
					for item in soup.findAll('video'):
						out[int(item["system-bitrate"])] = item["src"]
				else:
					for item in soup.findAll('video'):
						splts = item["src"].rsplit("/", 1)
						hd, (tl, rate) = splts[:-1], splts[-1].rsplit("K.",1)[0].rsplit("_", 1)
						hd = "/".join(hd)	
						if (hd,tl) not in vals:
							vals[hd,tl] = set([])
						vals[hd,tl].add(rate)
				
					for (hd,tl),rts in vals.iteritems():
						for idx, rt in enumerate(sorted(rts, key = lambda x: int(x))):
							out[int(rt) * 1000] = "%s/%s_,%s,K.mp4.csmil/bitrate=%s?v=2.5.14&fp=WIN%%%%2011,1,102,55&r=HJHYK&g=SOENISYOINXG&seek=0" % (hd,tl, ",".join(sorted(rts, key = lambda e: int(e))), idx)
					
		return out, fmt

	def menu_tree(self, node, out):
		for i in self.menu_main(node)["children"]:
			out.append(i)
			self.menu_tree(i, out)
		return out

if __name__ == "__main__":
	from  pprint import PrettyPrinter, pprint

	m = MenuItems()
	print "#" * 20
	menues = []
	m.menu_tree([], menues)
	PrettyPrinter(indent=1).pprint(menues)
	print "#" * 30
	leafs = [i for i in menues if not m.menu_main(i)["children"]]
	print "#" * 30
	shows = list(m.menu_shows(m.menu_main(leafs[30])["url"]))
	PrettyPrinter(indent=1).pprint(shows)
	print "#" * 30
	PrettyPrinter(indent=1).pprint(m.menu_play(shows[2]["url"]))
else:
	SCRAPER = MenuItems()
