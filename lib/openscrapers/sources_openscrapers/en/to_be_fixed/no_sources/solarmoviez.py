# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# -Cleaned and Checked on 10-27-2018 by JewBMX

import re,urllib,urlparse,hashlib,random,string,json,base64,sys,time

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import cache
from openscrapers.modules import directstream
from openscrapers.modules import jsunfuck
from openscrapers.modules import source_utils
from openscrapers.modules import cfscrape

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
        self.domains = ['solarmoviez.ru','solarmovie.mrunlock.pw']
        self.base_link = 'https://solarmoviez.ru'
        self.search_link = '/movie/search/%s.html'
        self.info_link = '/ajax/movie_get_info/%s.html'
        self.server_link = '/ajax/v4_movie_episodes/%s'
        self.embed_link = '/ajax/movie_embed/%s'
        self.token_link = '/ajax/movie_token?eid=%s&mid=%s&_=%s'
        self.source_link = '/ajax/movie_sources/%s?x=%s&y=%s'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            search = '%s Season %01d' % (title, int(season))
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(search)))
            r = self.s.get(url, headers=headers).content
            r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
            r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
            url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
            return url
        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(title)))
            r = self.s.get(url, headers=headers).content
            r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            r = [(i[0], i[1], re.findall('(\d+)', i[0])[0]) for i in r]
            results = []
            for i in r:
                try:
                    info = client.request(urlparse.urljoin(self.base_link, self.info_link % i[2]), headers=headers, timeout='15')
                    y = re.findall('<div\s+class="jt-info">(\d{4})', info)[0]
                    if self.matchAlias(i[1], aliases) and (year == y):
                        url = i[0]
                        break
                    #results.append([i[0], i[1], re.findall('<div\s+class="jt-info">(\d{4})', info)[0]])
                except:
                    url = None
                    pass

            #try:
            #    r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
            #    url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
            #except:
            #    url = None
            #    pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
            headers = mozhdr
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
            self.s = cfscrape.create_scraper()
            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            headers['Referer'] = url
            ref_url = url
            mid = re.findall('-(\d*)\.',url)[0]
            data = {'id':mid}
            r = self.s.post(url, headers=headers)
            try:
                u = urlparse.urljoin(self.base_link, self.server_link % mid)
                r = self.s.get(u, headers=mozhdr).content
                r = json.loads(r)['html']
                rl = client.parseDOM(r, 'div', attrs = {'class': 'pas-list'})
                rh = client.parseDOM(r, 'div', attrs = {'class': 'pas-header'})
                ids = client.parseDOM(rl, 'li', ret='data-id')
                servers = client.parseDOM(rl, 'li', ret='data-server')
                labels = client.parseDOM(rl, 'a', ret='title')
                r = zip(ids, servers, labels)
                rrr = zip(client.parseDOM(rh, 'li', ret='data-id'), client.parseDOM(rh, 'li', ret='class'))
                types = {}
                for rr in rrr:
                    types[rr[0]] = rr[1] 
                               
                for eid in r:
                    try:
                        try:
                            ep = re.findall('episode.*?(\d+).*?',eid[2].lower())[0]
                        except:
                            ep = 0
                        if (episode == 0) or (int(ep) == episode):
                            t = str(int(time.time()*1000))
                            quali = source_utils.get_release_quality(eid[2])[0]
                            if 'embed' in types[eid[1]]:
                                url = urlparse.urljoin(self.base_link, self.embed_link % (eid[0]))
                                xml = self.s.get(url, headers=headers).content
                                url = json.loads(xml)['src']
                                valid, hoster = source_utils.is_host_valid(url, hostDict)
                                if not valid: continue
                                q = source_utils.check_sd_url(url)
                                q = q if q != 'SD' else quali
                                sources.append({'source': hoster, 'quality': q, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False })
                                continue
                            else:
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
                                r = self.s.get(u, headers=headers).text
                                length = len(r)
                                if length == 0: count += 1
                            uri = None
                            uri = json.loads(r)['playlist'][0]['sources']
                            try:
                                uri = [i['file'] for i in uri if 'file' in i]
                            except:
                                try:
                                    uri = [uri['file']]
                                except:
                                    continue
                            
                            for url in uri:
                                if 'googleapis' in url:
                                    q = source_utils.check_sd_url(url)
                                    sources.append({'source': 'gvideo', 'quality': q, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                                    continue

                                valid, hoster = source_utils.is_host_valid(url, hostDict)
                                #urls, host, direct = source_utils.check_directstreams(url, hoster)
                                q = quali                        
                                if valid:
                                    #for z in urls:
                                    if hoster == 'gvideo':
                                        direct = True
                                        try:
                                            q = directstream.googletag(url)[0]['quality']
                                        except:
                                            pass
                                        url = directstream.google(url, ref=ref_url)
                                    else: direct = False
                                    sources.append({'source': hoster, 'quality': q, 'language': 'en', 'url': url, 'direct': direct, 'debridonly': False})                             
                                else:
                                    sources.append({'source': 'CDN', 'quality': q, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                    except:
                        pass
            except:
                pass

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if not url.startswith('http'):
                url = 'http:' + url
            for i in range(3):
                if 'google' in url and not 'googleapis' in url:
                    url = directstream.googlepass(url)
                if url:
                    break
            return url
        except Exception:
            return

    def uncensored(a, b):
        x = '' ; i = 0
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
        except:
            pass

    def uncensored2(self, script):
        try:
            js = jsunfuck.JSUnfuck(script).decode()
            x = re.search('''_x=['"]([^"']+)''', js).group(1)
            y = re.search('''_y=['"]([^"']+)''', js).group(1)
            return {'x': x, 'y': y}
        except:
            pass
