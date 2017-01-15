"""
flashx.tv urlresolver plugin
Copyright (C) 2015 tknorris

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import re
import urlparse
import urllib
from lib import jsunpack
from lib import unwise
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import ResolverError

SORT_KEY = {'High': 3, 'Middle': 2, 'Low': 1}
net = common.Net()

BAD_ETAGS = ["580eabc0-40ac3a", "582e7b99-9cd574b"]
MIN_CONTENT = 1024 * 1024 * 5


def get_media_url(url):
    try:
        hostname = urlparse.urlparse(url).hostname
        media_id = re.search('embed.php\?c=(.*)', url).group(1)
        headers = {'User-Agent': common.IE_USER_AGENT}
        html = net.http_GET(url, headers=headers).content
        adblock_check(html, headers)
        headers.update({'Referer': url})
        for js_url in get_js_url(html):
            js = get_js(js_url, headers, hostname)
            js = unwise.unwise_process(js)
            adblock_check(js, headers)
            xhr_check(js, headers)

        html = cleanse_html(html)
        for match in re.finditer('''href=['"]([^'"]+)''', html):
            playvid_url = match.group(1)
            if '-%s.' % (media_id) in playvid_url:
                headers.update({'Referer': url})
                html = net.http_GET(playvid_url, headers=headers).content
                common.log_utils.log(html)
                html = cleanse_html(html)
                headers['Referer'] = playvid_url

        sources = []
        spans = get_span_ids(html, media_id)
        for match in re.finditer('<script[^>]*>\s*(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            if not spans or any(span_id in js_data for span_id in spans):
                js_sources = helpers.parse_sources_list(js_data)
                sources += js_sources

        d = {}
        for source in sources: d[source[1]] = d.setdefault(source[1], 0) + 1
        common.log_utils.log(sources)
        sources = [source for source in sources if d[source[1]] == 1]
        common.log_utils.log(sources)
        sources = [source for source in sources if
                   not any([x in source[1].lower() for x in ('/movie.mp4', '/trailer.mp4', '://cdn.flashx.tv')])]
        common.log_utils.log(sources)
        sources = [source for source in sources if check_headers(source, headers)]
        common.log_utils.log(sources)
        try:
            sources.sort(key=lambda x: SORT_KEY.get(x[0], 0), reverse=True)
        except:
            pass
        source = helpers.pick_source(sources)
        return source + helpers.append_headers(headers)

    except Exception as e:
        common.log_utils.log_debug('Exception during flashx resolve parse: %s' % e)
        raise

    raise ResolverError('Unable to resolve flashx link. Filelink not found.')


def cleanse_html(html):
    for match in re.finditer('<!--.*?(..)-->', html, re.DOTALL):
        if match.group(1) != '//': html = html.replace(match.group(0), '')

    html = re.sub('''<(div|span)[^>]+style=["'](visibility:\s*hidden|display:\s*none);?["']>.*?</\\1>''', '', html,
                  re.I | re.DOTALL)
    return html


def get_span_ids(html, media_id):
    spans = []
    pattern = '''<img[^>]+src=['"][^"']+%s.jpe?g''' % (media_id)
    for span in get_dom(html, 'span'):
        match = re.search('''<span[^>]+id=['"]([^'"]+)[^>]+>(.*)''', span, re.I | re.DOTALL)
        if match:
            if re.search(pattern, match.group(2), re.I | re.DOTALL):
                spans.append(match.group(1))

    return spans


def get_dom(html, tag):
    start_str = '<%s' % (tag.lower())
    end_str = '</%s' % (tag.lower())

    results = []
    html = html.lower()
    while html:
        start = html.find(start_str)
        end = html.find(end_str, start)
        pos = html.find(start_str, start + 1)
        while pos < end and pos != -1:
            tend = html.find(end_str, end + len(end_str))
            if tend != -1: end = tend
            pos = html.find(start_str, pos + 1)

        if start == -1 and end == -1:
            break
        elif start > -1 and end > -1:
            result = html[start:end]
        elif end > -1:
            result = html[:end]
        elif start > -1:
            result = html[start:]
        else:
            break

        results.append(result)
        html = html[start + len(start_str):]

    return results


def adblock_check(js, headers):
    match = re.search('''!=\s*null.*?get\(['"]([^'"]+).*?\{([^:]+)\s*:\s*['"]([^'"]+)''', js, re.DOTALL)
    if match:
        fx_url, fx_param, fx_value = match.groups()
        fx_url = resolve_url(
            urlparse.urljoin('https://www.flashx.tv', fx_url) + '?' + urllib.urlencode({fx_param: fx_value}))
        common.log_utils.log('fxurl: %s' % (fx_url))
        _html = net.http_GET(fx_url, headers=headers).content


def xhr_check(js, headers):
    match = re.search('''request\.open\(\s*["']([^'"]+)"\s*,\s*['"]([^'"]+)''', js, re.DOTALL)
    if match:
        _method, xhr_url = match.groups()
        common.log_utils.log('xhr url: %s' % (xhr_url))
        _html = net.http_GET(xhr_url, headers=headers).content


def check_headers(source, headers):
    try:
        response = net.http_HEAD(source[1], headers=headers)
        res_headers = response.get_headers(as_dict=True)
        common.log_utils.log(res_headers)
        if res_headers.get('Etag', '').strip('"') not in BAD_ETAGS and int(
                res_headers.get('Content-Length', 0)) >= MIN_CONTENT:
            return True
    except Exception as e:
        common.log_utils.log('Adding failed source: %s' % (e), common.log_utils.LOGWARNING)
        return True
    return False


def get_js_url(html):
    urls = []
    for match in re.finditer('''<script[^>]*src\s*=\s*(["'])(.*?)\\1''', html, re.I):
        js_url = match.group(2).strip()
        js_url = re.sub('''['"]''', '', js_url)
        if '/' not in js_url:
            js_url = js_url.strip('+')
            pattern = '''var\s+%s\s*=\s*(['"])(.*?)\\1''' % (js_url)
            match = re.search(pattern, html)
            if match:
                js_url = match.group(2)
        urls.append(js_url)
    return urls


def get_js(js_url, headers, hostname):
    js = ''
    if js_url.startswith('//'):
        js_url = 'https:' + js_url
    elif not js_url.startswith('http'):
        base_url = 'https://' + hostname
        js_url = urlparse.urljoin(base_url, js_url)

    common.log_utils.log('Getting JS: |%s| - |%s|' % (js_url, headers))
    try:
        js = net.http_GET(js_url, headers=headers).content
    except:
        js = ''
    return js


def resolve_url(url):
    parts = list(urlparse.urlsplit(url))
    segments = parts[2].split('/')
    segments = [segment + '/' for segment in segments[:-1]] + [segments[-1]]
    resolved = []
    for segment in segments:
        if segment in ('../', '..'):
            if resolved[1:]:
                resolved.pop()
        elif segment not in ('./', '.'):
            resolved.append(segment)
    parts[2] = ''.join(resolved)
    return urlparse.urlunsplit(parts)