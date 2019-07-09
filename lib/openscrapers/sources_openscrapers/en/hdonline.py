# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
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
'''

import base64
import json
import re
import time
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import dom_parser
from openscrapers.modules import jsunfuck
from openscrapers.modules import source_utils

CODE = '''def retA():
    class Infix:
        def __init__(self, function):
            self.function = function
        def __ror__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __or__(self, other):
            return self.function(other)
        def __rlshift__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __rshift__(self, other):
            return self.function(other)
        def __call__(self, value1, value2):
            return self.function(value1, value2)
    def my_add(x, y):
        try: return x + y
        except Exception: return str(x) + str(y)
    x = Infix(my_add)
    return %s
param = retA()'''


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hdonline.is']
        self.base_link = 'https://hdonline.is/'
        self.search_link = '/search/%s'
        self.info_link = '/ajax/movie_info/%s.html?is_login=false'
        self.server_link = '/ajax/movie/episodes/%s'
        self.embed_link = '/ajax/movie/get_embed/%s'  # https://hdonline.is/ajax/movie/get_embed/1202711
        self.token_link = '/ajax/movie/token?eid=%s&mid=%s&_=%s'
        self.source_link = '/ajax/movie/get_sources/%s?x=%s&y=%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except BaseException:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            search = '%s Season %01d' % (title, int(season))
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))

            s = cfscrape.create_scraper()
            r = s.get(url).content
            r = client.parseDOM(r, 'li', attrs={'class': 'movie-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
            r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
            url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
            return url
        except BaseException:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))

            s = cfscrape.create_scraper()
            r = s.get(url).content
            r = client.parseDOM(r, 'li', attrs={'class': 'movie-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            results = [(i[0], i[1]) for i in r]
            try:
                r = [(i[0], i[1]) for i in results]
                url = [i[0] for i in r if self.matchAlias(i[1], aliases)][0]
            except BaseException:
                url = None
                pass

            if (url is None):
                url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}
            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)
            url += '/'
            ref_url = url
            mozhdr = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
            headers = mozhdr
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Referer'] = url
            self.s = cfscrape.create_scraper()
            mid = re.findall('-(\d*)/', url)[0]
            try:
                u = urlparse.urljoin(self.base_link, self.server_link % mid)
                r = self.s.get(u, headers=mozhdr).content
                r = json.loads(r)['html']

                r = dom_parser.parse_dom(r, 'li', req=['data-id', 'data-server'])
                r = [(i.attrs['data-id'], i.attrs['data-server'], dom_parser.parse_dom(i.content, 'a', req='title')[0])
                     for i in r]
                r = [(i[0], i[1], i[2].content) for i in r]  # r = zip(ids, servers, labels)

                urls = []
                for eid in r:
                    try:
                        ep = re.findall('episode.*?(\d+).*?', eid[2].lower())[0]
                        ep = '%01d' % int(ep)
                    except BaseException:
                        ep = 0
                    if (episode == 0) or (int(ep) == int(episode)):
                        t = int(time.time() * 1000)
                        url = urlparse.urljoin(self.base_link, self.token_link % (eid[0], mid, t))
                        script = self.s.get(url, headers=headers).content
                        if '$_$' in script:
                            params = self.uncensored1(script)
                        elif script.startswith('[]') and script.endswith('()'):
                            params = self.uncensored2(script)
                        elif '_x=' in script:
                            x = re.search('''_x=['"]([^"']+)''', script).group(1)
                            y = re.search('''_y=['"]([^"']+)''', script).group(1)
                            params = {'x': x, 'y': y}
                        else:
                            raise Exception()
                        u = urlparse.urljoin(self.base_link, self.source_link % (eid[0], params['x'], params['y']))
                        length = 0
                        count = 0
                        while length == 0 and count < 11:
                            r = self.s.get(u, headers=headers).content
                            length = len(r)
                            if length == 0:
                                if count == 9:
                                    u = u.replace('_sources', '_embed')
                                count += 1

                        try:
                            frames = re.findall('''file['"]:['"]([^'"]+)''', r)
                            for i in frames:
                                if '.srt' in i: continue
                                urls.append((i, eid[2]))
                        except BaseException:
                            pass

                        r1 = json.loads(r)

                        try:
                            frame = r1['src']
                            urls.append((frame, eid[2]))
                        except BaseException:
                            pass
                        try:
                            frame = r1['playlist'][0]
                            frame = frame['sources'][0]
                            frame = frame['file']
                            urls.append((frame, eid[2]))
                        except BaseException:
                            pass

                for i in urls:

                    s, eid = i[0], i[1]
                    try:
                        if 'googleapis' in s:
                            urls = directstream.googletag(s)
                            if not urls:
                                quality, info = source_utils.get_release_quality(url, eid)
                                sources.append({'source': 'gvideo', 'quality': quality,
                                                'language': 'en', 'url': s, 'direct': True,
                                                'debridonly': False})
                            else:
                                for i in urls:
                                    sources.append({'source': 'gvideo', 'quality': i['quality'],
                                                    'language': 'en', 'url': i['url'], 'direct': True,
                                                    'debridonly': False})
                        elif 'lh3.' in s:
                            urls = directstream.googletag(s)
                            for i in urls:
                                try:
                                    url2 = directstream.google(i['url'], ref=ref_url) if 'lh3.' in i['url'] else i[
                                        'url']
                                    if not url2: url2 = i['url']
                                    sources.append({'source': 'gvideo', 'quality': i['quality'], 'language': 'en',
                                                    'url': url2, 'direct': True, 'debridonly': False})
                                except BaseException:
                                    sources.append({'source': 'gvideo', 'quality': i['quality'], 'language': 'en',
                                                    'url': i['url'], 'direct': True, 'debridonly': False})
                        elif 'lemonstream' in s:
                            quality, info = source_utils.get_release_quality(s, eid)
                            sources.append({'source': 'CDN', 'quality': quality, 'language': 'en',
                                            'url': s, 'direct': True, 'debridonly': False})
                        elif 'notcool' in s:
                            s = s.replace('\\', '')
                            quality, info = source_utils.get_release_quality(s, eid)
                            sources.append({'source': 'CDN', 'quality': quality, 'language': 'en',
                                            'url': s, 'direct': True, 'debridonly': False})
                        else:
                            quality, info = source_utils.get_release_quality(s, eid)
                            valid, host = source_utils.is_host_valid(s, hostDict)
                            if valid:
                                sources.append({'source': host, 'quality': quality, 'language': 'en',
                                                'url': s, 'direct': False, 'debridonly': False})
                    except BaseException:
                        pass

            except BaseException:
                pass

            return sources
        except BaseException:
            return sources

    def resolve(self, url):
        try:
            if self.embed_link in url:
                result = self.s.get(url)
                url = json.loads(result)['embed_url']
                return url
            elif 'google' in url and not 'googleapis' in url:
                return directstream.googlepass(url)
            else:
                return url
        except BaseException:
            return

    def uncensored(a, b):
        x = '';
        i = 0
        for i, y in enumerate(a):
            z = b[i % len(b) - 1]
            y = int(ord(str(y)[0])) + int(ord(str(z)[0]))
            x += chr(y)
        x = base64.b64encode(x)
        return x

    def uncensored1(self, script):
        try:
            script = '(' + script.split("(_$$)) ('_');")[0].split("/* `$$` */")[-1].strip()
            script = script.replace('(__$)[$$$]', '\'"\'')
            script = script.replace('(__$)[_$]', '"\\\\"')
            script = script.replace('(o^_^o)', '3')
            script = script.replace('(c^_^o)', '0')
            script = script.replace('(_$$)', '1')
            script = script.replace('($$_)', '4')

            vGlobals = {"__builtins__": None, '__name__': __name__, 'str': str, 'Exception': Exception}
            vLocals = {'param': None}
            exec (CODE % script.replace('+', '|x|'), vGlobals, vLocals)
            data = vLocals['param'].decode('string_escape')
            x = re.search('''_x=['"]([^"']+)''', data).group(1)
            y = re.search('''_y=['"]([^"']+)''', data).group(1)
            return {'x': x, 'y': y}
        except BaseException:
            pass

    def uncensored2(self, script):
        try:
            js = jsunfuck.JSUnfuck(script).decode()
            x = re.search('''_x=['"]([^"']+)''', js).group(1)
            y = re.search('''_y=['"]([^"']+)''', js).group(1)
            return {'x': x, 'y': y}
        except BaseException:
            pass
