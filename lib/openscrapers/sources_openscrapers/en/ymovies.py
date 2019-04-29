# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

"""
    OpenScrapers Project
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

import base64
import json
import re
import traceback
import urllib

import urlparse
from openscrapers.modules import cfscrape, cleantitle, client, directstream, \
    dom_parser, jsunfuck, log_utils, source_utils

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
        self.domains = ['yesmovies.to']
        self.base_link = 'https://yesmovies.to'
        self.search_link = '/search/%s.html'
        self.info_link = '/ajax/movie_info/%s.html?is_login=false'
        self.server_link = '/ajax/v4_movie_episodes/%s'
        self.embed_link = '/ajax/movie_embed/%s'
        self.token_link = '/ajax/movie_token?eid=%s&mid=%s'
        self.source_link = '/ajax/movie_sources/%s?x=%s&y=%s'
        self.scraper = cfscrape.create_scraper()

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('YMovies - Exception: \n' + str(failure))
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('YMovies - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('YMovies - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('YMovies - Exception: \n' + str(failure))
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            search = '%s Season %01d' % (title, int(season))
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))
            log_utils.log('shit Returned: %s' % str(url), log_utils.LOGNOTICE)
            r = self.scraper.get(url).content
            r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
            r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
            url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
            return url
        except Exception:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = self.scraper.get(url).content
            r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
            try:
                r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
                url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
            except Exception:
                url = None
                pass

            if (url is None):
                url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

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

            mid = re.findall('-(\d+)', url)[-1]

            try:
                headers = {'Referer': url}
                u = urlparse.urljoin(self.base_link, self.server_link % mid)
                r = self.scraper.get(u).content
                r = json.loads(r)['html']
                r = client.parseDOM(r, 'div', attrs={'class': 'pas-list'})
                ids = client.parseDOM(r, 'li', ret='data-id')
                servers = client.parseDOM(r, 'li', ret='data-server')
                labels = client.parseDOM(r, 'a', ret='title')
                r = zip(ids, servers, labels)
                u = urlparse.urljoin(self.base_link, self.info_link % mid)
                quality = self.scraper.get(u).content
                quality = dom_parser.parse_dom(quality, 'div', attrs={'class': 'jtip-quality'})[0].content
                if quality == "HD":
                    quality = "720p"
                for eid in r:
                    try:
                        try:
                            ep = re.findall('episode.*?(\d+).*?', eid[2].lower())[0]
                        except Exception:
                            ep = 0
                        if (episode == 0) or (int(ep) == episode):
                            if eid[1] != '6':
                                url = urlparse.urljoin(self.base_link, self.embed_link % eid[0])
                                link = self.scraper.get(url).content
                                link = json.loads(link)['src']
                                valid, host = source_utils.is_host_valid(link, hostDict)
                                sources.append({'source': host, 'quality': quality, 'language': 'en',
                                                'url': link, 'info': [], 'direct': False, 'debridonly': False})
                            else:
                                url = urlparse.urljoin(self.base_link, self.token_link % (eid[0], mid))
                                script = self.scraper.get(url).content
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

                                u = urlparse.urljoin(self.base_link, self.source_link %
                                                     (eid[0], params['x'], params['y']))
                                r = self.scraper.get(u).content
                                url = json.loads(r)['playlist'][0]['sources']
                                url = [i['file'] for i in url if 'file' in i]
                                url = [directstream.googletag(i) for i in url]
                                url = [i[0] for i in url if i]

                                for s in url:
                                    if 'lh3.googleusercontent.com' in s['url']:
                                        s['url'] = directstream.googleredirect(s['url'])

                                    sources.append({'source': 'gvideo', 'quality': s['quality'], 'language': 'en',
                                                    'url': s['url'], 'direct': True, 'debridonly': False})
                    except Exception:
                        pass
            except Exception:
                pass

            return sources
        except Exception:
            return sources

    def resolve(self, url):
        try:
            if self.embed_link in url:
                result = self.scraper.get(url).content
                url = json.loads(result)['embed_url']
                return url

            return url
        except Exception:
            return

    def uncensored(self, a, b):
        x = ''
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
        except Exception:
            pass

    def uncensored2(self, script):
        try:
            js = jsunfuck.JSUnfuck(script).decode()
            x = re.search('''_x=['"]([^"']+)''', js).group(1)
            y = re.search('''_y=['"]([^"']+)''', js).group(1)
            return {'x': x, 'y': y}
        except Exception:
            pass
