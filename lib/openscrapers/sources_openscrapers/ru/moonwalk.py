# -*- coding: utf-8 -*-

"""
    Covenant Add-on

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
import json
import urlparse

from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


def moonwalk(link, ref, season, episode):
    try:
        if season and episode:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(link).query))
            q.update({'season': season, 'episode': episode})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            link = link.replace('?' + urlparse.urlparse(link).query, '') + '?' + q

        trans = __get_moonwalk_translators(link, ref)
        trans = trans if trans else [(link, '')]

        urls = []
        for i in trans:
            urls += __get_moonwalk(i[0], ref, info=i[1])
        return urls
    except:
        return []

def __get_moonwalk_translators(url, ref):
    try:
        r = client.request(url, referer=ref)

        r = dom_parser.parse_dom(r, 'select', attrs={'id': 'translator'})
        r = dom_parser.parse_dom(r, 'option', req='value')
        r = [(i.attrs['value'], i.content, i.attrs.get('selected')) for i in r]

        sel_trans = [i[0] for i in r if i[2]][0]

        return [(url.replace(sel_trans, i[0]), i[1]) for i in r]
    except:
        return []


def __get_moonwalk(url, ref, info=''):
    try:
        host = urlparse.urlparse(url)
        host = '%s://%s' % (host.scheme, host.netloc)

        r = client.request(url, referer=ref, output='extended')

        headers = r[3]
        headers.update({'Cookie': r[2].get('Set-Cookie')})
        r = r[0]

        csrf = re.findall('name="csrf-token" content="(.*?)"', r)[0]
        story = re.findall('''["']X-CSRF-Token["']\s*:\s*[^,]+,\s*["']([\w\-]+)["']\s*:\s*["'](\w+)["']''', r)[0]
        headers.update({'X-CSRF-Token': csrf, story[0]: story[1]})

        for i in re.findall('window\[(.*?)\]', r):
            r = r.replace(i, re.sub('''["']\s*\+\s*["']''', '', i))

        varname, post_url = re.findall('''var\s*(\w+)\s*=\s*["'](.*?/all/?)["']\s*;''', r)[0]
        jsid = re.findall('''\.post\(\s*%s\s*,\s*([^(\);)]+)''' % varname, r)[0]

        jsdata = re.findall('(?:var\s*)?%s\s*=\s*({.*?})' % re.escape(jsid), r, re.DOTALL)[0]
        jsdata = re.sub(r'([\{\s,])(\w+)(:)', r'\1"\2"\3', jsdata)
        jsdata = re.sub(r'''(?<=:)\s*\'''', ' "', jsdata)
        jsdata = re.sub(r'''(?<=\w)\'''', '"', jsdata)
        jsdata = re.sub(''':\s*\w+\s*\?[^,}]+''', ': 0', jsdata)
        jsdata = re.sub(''':\s*[a-zA-Z]+[^,}]+''', ': 0', jsdata)
        jsdata = json.loads(jsdata)

        mw_key = re.findall('''var\s*mw_key\s*=\s*["'](\w+)["']''', r)[0]
        newatt = re.findall('''%s\[["']([^=]+)["']\]\s*=\s*["']([^;]+)["']''' % re.escape(jsid), r)[0]
        newatt = [re.sub('''["']\s*\+\s*["']''', '', i) for i in newatt]

        jsdata.update({'mw_key': mw_key, newatt[0]: newatt[1]})

        r = client.request(urlparse.urljoin(host, post_url), post=jsdata, headers=headers, XHR=True)
        r = json.loads(r).get('mans', {}).get('manifest_m3u8')

        r = client.request(r, headers=headers)

        r = [(i[0], i[1]) for i in re.findall('#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(\d+).*?(http.*?(?:\.abst|\.f4m|\.m3u8)).*?', r, re.DOTALL) if i]
        r = [(source_utils.label_to_quality(i[0]), i[1] + '|%s' % urllib.urlencode(headers)) for i in r]
        r = [{'quality': i[0], 'url': i[1], 'info': info} for i in r]

        return r
    except:
        return []
