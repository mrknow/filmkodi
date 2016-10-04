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
import xbmcgui
from urlresolver import common
from urlresolver.resolver import ResolverError

def get_hidden(html, form_id=None):
    hidden = {}
    if form_id:
        pattern = '''<form [^>]*id\s*=\s*['"]?%s['"]?[^>]*>(.*?)</form>'''
    else:
        pattern = '''<form[^>]*>(.*?)</form>'''
        
    for form in re.finditer(pattern, html, re.DOTALL | re.I):
        for field in re.finditer('''<input [^>]*type=['"]?hidden['"]?[^>]*>''', form.group(1)):
            match = re.search('''name\s*=\s*['"]([^'"]+)''', field.group(0))
            match1 = re.search('''value\s*=\s*['"]([^'"]*)''', field.group(0))
            if match and match1:
                hidden[match.group(1)] = match1.group(1)
            
    common.log_utils.log_debug('Hidden fields are: %s' % (hidden))
    return hidden

def pick_source(sources, auto_pick=True):
    if len(sources) == 1:
        return sources[0][1]
    elif len(sources) > 1:
        if auto_pick:
            return sources[0][1]
        else:
            result = xbmcgui.Dialog().select('Choose the link', [source[0] for source in sources])
            if result == -1:
                raise ResolverError('No link selected')
            else:
                return sources[result][1]
    else:
        raise ResolverError('No Video Link Found')
