# -*- coding: utf-8 -*-
"""
    OpenScrapers Module

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

# Addon Name: OpenScrapers Module
# Addon id: script.module.openscrapers


import random
import re
import urllib
import urlparse

from openscrapers.modules import client
from openscrapers.modules import utils


def request(url, check, close=True, redirect=True, error=False, proxy=None, post=None, headers=None, mobile=False, XHR=False, limit=None, referer=None, cookie=None, compression=True, output='', timeout='30'):
    try:
        r = client.request(url, close=close, redirect=redirect, proxy=proxy, post=post, headers=headers, mobile=mobile, XHR=XHR, limit=limit, referer=referer, cookie=cookie, compression=compression, output=output, timeout=timeout)
        if r is not None and error is not False: return r
        if check in str(r) or str(r) == '': return r
        proxies = sorted(get(), key=lambda x: random.random())
        proxies = sorted(proxies, key=lambda x: random.random())
        proxies = proxies[:3]
        for p in proxies:
            p += urllib.quote_plus(url)
            if post is not None:
                if isinstance(post, dict):
                    post = utils.byteify(post)
                    post = urllib.urlencode(post)
                p += urllib.quote_plus('?%s' % post)
            r = client.request(p, close=close, redirect=redirect, proxy=proxy, headers=headers, mobile=mobile, XHR=XHR, limit=limit, referer=referer, cookie=cookie, compression=compression, output=output, timeout='20')
            if check in str(r) or str(r) == '': return r
    except:
        pass


def geturl(url):
    try:
        r = client.request(url, output='geturl')
        if r is None: return r
        host1 = re.findall('([\w]+)[.][\w]+$', urlparse.urlparse(url.strip().lower()).netloc)[0]
        host2 = re.findall('([\w]+)[.][\w]+$', urlparse.urlparse(r.strip().lower()).netloc)[0]
        if host1 == host2: return r
        proxies = sorted(get(), key=lambda x: random.random())
        proxies = sorted(proxies, key=lambda x: random.random())
        proxies = proxies[:3]
        for p in proxies:
            p += urllib.quote_plus(url)
            r = client.request(p, output='geturl')
            if r is not None: return parse(r)
    except:
        pass


def parse(url):
    try: url = client.replaceHTMLCodes(url)
    except: pass
    try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
    except: pass
    try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
    except: pass
    return url


def get():
    return [
    'https://www.3proxy.us/index.php?hl=2e5&q=',
    'https://www.4proxy.us/index.php?hl=2e5&q=',
    'http://buka.link/browse.php?b=20&u=',
    'http://buka.link/browse.php?u=%s&b=2',
    'http://dontfilter.us/browse.php?b=20&u=%s',
    'http://www.xxlproxy.com/index.php?hl=3e4&q=',
    'http://free-proxyserver.com/browse.php?b=20&u=',
    'http://proxite.net/browse.php?b=20&u=',
    'http://proxydash.com/browse.php?b=20&u=',
    'http://webproxy.stealthy.co/browse.php?b=20&u=',
    'http://sslpro.eu/browse.php?b=20&u=',
    'http://webtunnel.org/browse.php?b=20&u=',
    'http://proxycloud.net/browse.php?b=20&u=',
    'http://sno9.com/browse.php?b=20&u=',
    'http://www.onlineipchanger.com/browse.php?b=20&u=',
    'http://www.pingproxy.com/browse.php?b=20&u=',
    'https://www.ip123a.com/browse.php?b=20&u=',
    'http://buka.link/browse.php?b=20&u=',
    'https://zend2.com/open18.php?b=20&u=',
    'http://proxy.deals/browse.php?b=20&u=',
    'http://freehollandproxy.com/browse.php?b=20&u=',
    'http://proxy.rocks/browse.php?b=20&u=',
    'http://proxy.discount/browse.php?b=20&u=',
    'http://proxy.lgbt/browse.php?b=20&u=',
    'http://proxy.vet/browse.php?b=20&u=',
    'http://www.unblockmyweb.com/browse.php?b=20&u=',
    'http://onewebproxy.com/browse.php?b=20&u=',
    'http://pr0xii.com/browse.php?b=20&u=',
    'http://mlproxy.science/surf.php?b=20&u=',
    'https://www.prontoproxy.com/browse.php?b=20&u=',
    'http://fproxy.net/browse.php?b=20&u=',
    'http://www.mybriefonline.xyz/browse.php?b=20&u=',
    'http://www.navigate-online.xyz/browse.php?b=20&u='
    ]


