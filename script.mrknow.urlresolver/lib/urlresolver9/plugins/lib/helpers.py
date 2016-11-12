"""
    URLResolver Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re
import urllib
import xbmcgui
import jsunpack
from urlparse import urlparse
from urlresolver9 import common
from urlresolver9.resolver import ResolverError

def get_hidden(html, form_id=None, index=None, include_submit=True):
    hidden = {}

    # remove comments
    r = re.compile('<!--.*?(?!//)--!*>', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    m = r.findall(html)
    if m:
        for comment in m:
            html = html.replace(comment, '')

    if form_id:
        pattern = '''<form [^>]*id\s*=\s*['"]?%s['"]?[^>]*>(.*?)</form>''' % (form_id)
    else:
        pattern = '''<form[^>]*>(.*?)</form>'''
        
    for i, form in enumerate(re.finditer(pattern, html, re.DOTALL | re.I)):
        if index is None or i == index:
            for field in re.finditer('''<input [^>]*type=['"]?hidden['"]?[^>]*>''', form.group(1)):
                match = re.search('''name\s*=\s*['"]([^'"]+)''', field.group(0))
                match1 = re.search('''value\s*=\s*['"]([^'"]*)''', field.group(0))
                if match and match1:
                    hidden[match.group(1)] = match1.group(1)
            
            if include_submit:
                match = re.search('''<input [^>]*type=['"]?submit['"]?[^>]*>''', form.group(1))
                if match:
                    name = re.search('''name\s*=\s*['"]([^'"]+)''', match.group(0))
                    value = re.search('''value\s*=\s*['"]([^'"]*)''', match.group(0))
                    if name and value:
                        hidden[name.group(1)] = value.group(1)

    common.log_utils.log_debug('Hidden fields are: %s' % (hidden))
    return hidden

def pick_source(sources, auto_pick=None):
    if auto_pick is None:
        #auto_pick = common.get_setting('auto_pick') == 'true'
        auto_pick = True
    if len(sources) == 1:
        return sources[0][1]
    elif len(sources) > 1:
        if auto_pick:
            return sources[0][1]
        else:
            result = xbmcgui.Dialog().select('Choose the link', [source[0] if source[0] else 'Uknown' for source in sources])
            if result == -1:
                raise ResolverError('No link selected')
            else:
                return sources[result][1]
    else:
        raise ResolverError('No Video Link Found')

def append_headers(headers):
    return '|%s' % '&'.join(['%s=%s' % (key, urllib.quote_plus(headers[key])) for key in headers])

def add_packed_data(html):
    for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
        try:
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace('\\', '')
            html += js_data
        except:
            pass

    return html

def parse_sources_list(html):
    sources = []
    match = re.search('''['"]?sources['"]?\s*:\s*\[(.*?)\]''', html, re.DOTALL)
    if match:
        sources = [(match[1], match[0].replace('\/', '/')) for match in re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL)]
    return sources

def parse_html5_source_list(html):
    label_attrib = 'type' if not re.search('''<source\s+src\s*=.*?data-res\s*=.*?/\s*>''', html) else 'data-res'
    sources = [(match[1], match[0].replace('\/', '/')) for match in re.findall('''<source\s+src\s*=\s*['"]([^'"]+)['"](?:.*?''' + label_attrib + '''\s*=\s*['"](?:video/)?([^'"]+)['"])''', html, re.DOTALL)]
    return sources

def parse_smil_source_list(smil):
    sources = []
    base = re.search('base\s*=\s*"([^"]+)', smil).groups()[0]
    for i in re.finditer('src\s*=\s*"([^"]+)(?:"\s*(?:width|height)\s*=\s*"([^"]+))?', smil):
        label = 'Unknown'
        if len(i.groups()) > 1:
            if i.group(2) is not None:
                label = i.group(2)
        sources += [(label, '%s playpath=%s' % (base, i.group(1)))]
    return sources

def scrape_sources(html, result_blacklist=None):
    def _parse_to_list(_html, regex):
        _blacklist = ['.jpg', '.jpeg', '.gif', '.png', '.js', '.css', '.htm', '.html', '.php',
                      '.srt', '.sub', '.xml', '.swf', '.vtt']
        if isinstance(result_blacklist, list):
            _blacklist = list(set(_blacklist + result_blacklist))
        matches = []
        for i in re.finditer(regex, _html, re.DOTALL):
            match = i.group(1)
            trimmed_path = urlparse(match).path.split('/')[-1]
            if ('://' not in match) or (not trimmed_path) or (any(match == m[1] for m in matches)) or \
                    (any(bl in trimmed_path.lower() for bl in _blacklist)):
                continue
            label = trimmed_path
            if len(i.groups()) > 1:
                if i.group(2) is not None:
                    label = i.group(2)
            matches.append(('%s' % label, match))
        if matches:
            common.log_utils.log_debug('Scrape sources |%s| found |%s|' % (regex, matches))
        return matches

    html = add_packed_data(html)

    source_list = _parse_to_list(html, '''video[^><]+src\s*=\s*['"]([^'"]+)''')
    source_list += _parse_to_list(html, '''source\s+src\s*=\s*['"]([^'"]+)''')
    source_list += _parse_to_list(html, '''["']?\s*file\s*["']?\s*[:=,]?\s*["']([^"']+)(?:[^}>\],]?["',]?\s*label\s*["']?\s*[:=]?\s*["']([^"']+))?''')
    source_list += _parse_to_list(html, '''["']?\s*url\s*["']?\s*[:=]\s*["']([^"']+)''')
    source_list += _parse_to_list(html, '''param\s+name\s*=\s*"src"\s*value\s*=\s*"([^"]+)''')

    source_list = list(set(source_list))
    try: source_list.sort(key=lambda x: int(x[0]), reverse=True)
    except:
        common.log_utils.log_debug('Scrape sources sort failed |int(x[0])|')
        try: source_list.sort(key=lambda x: int(x[0][:-1]), reverse=True)
        except:
            common.log_utils.log_debug('Scrape sources sort failed |int(x[0][:-1])|')
            try: source_list.sort(key=lambda x: x[0], reverse=True)
            except:
                common.log_utils.log_debug('Scrape sources sort failed |x[0]|')

    return source_list

def get_media_url(url, result_blacklist=None):
    if not isinstance(result_blacklist, list): result_blacklist = []
    result_blacklist = list(set(result_blacklist + ['.smil']))  # smil(not playable) contains potential sources, only blacklist when called from here
    net = common.Net()
    parsed_url = urlparse(url)
    headers = {'User-Agent': common.FF_USER_AGENT,
               'Referer': '%s://%s' % (parsed_url.scheme, parsed_url.hostname)}

    response = net.http_GET(url, headers=headers)
    response_headers = response.get_headers(as_dict=True)
    headers.update({'Referer': url})
    cookie = response_headers.get('Set-Cookie', None)
    if cookie:
        headers.update({'Cookie': cookie})
    html = response.content

    source_list = scrape_sources(html, result_blacklist)
    source = pick_source(source_list)
    return source + append_headers(headers)
