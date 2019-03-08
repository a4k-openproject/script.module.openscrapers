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
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import json
import re
import urllib
import urlparse

from openscrapers.modules import cache
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['kinox.to', 'kinox.ag', 'kinox.tv', 'kinox.me', 'kinox.am', 'kinox.nu', 'kinox.pe', 'kinox.sg']
        self._base_link = None
        self.search_link = '/Search.html?q=%s'
        self.get_links_epi = '/aGET/MirrorByEpisode/?Addr=%s&SeriesID=%s&Season=%s&Episode=%s'
        self.mirror_link = '/aGET/Mirror/%s&Hoster=%s&Mirror=%s'

    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'http://%s' % self.domains[0])
        return self._base_link

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(imdb)
            if url:
                return urllib.urlencode({'url': url})
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(imdb)
            if url:
                return urllib.urlencode({'url': url})
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            data.update({'season': season, 'episode': episode})
            return urllib.urlencode(data)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if url == None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, data.get('url'))
            season = data.get('season')
            episode = data.get('episode')

            r = client.request(url)

            if season and episode:
                r = dom_parser.parse_dom(r, 'select', attrs={'id': 'SeasonSelection'}, req='rel')[0]
                r = client.replaceHTMLCodes(r.attrs['rel'])[1:]
                r = urlparse.parse_qs(r)
                r = dict([(i, r[i][0]) if r[i] else (i, '') for i in r])
                r = urlparse.urljoin(self.base_link, self.get_links_epi % (r['Addr'], r['SeriesID'], season, episode))
                r = client.request(r)

            r = dom_parser.parse_dom(r, 'ul', attrs={'id': 'HosterList'})[0]
            r = dom_parser.parse_dom(r, 'li', attrs={'id': re.compile('Hoster_\d+')}, req='rel')
            r = [(client.replaceHTMLCodes(i.attrs['rel']), i.content) for i in r if i[0] and i[1]]
            r = [(i[0], re.findall('class="Named"[^>]*>([^<]+).*?(\d+)/(\d+)', i[1])) for i in r]
            r = [(i[0], i[1][0][0].lower().rsplit('.', 1)[0], i[1][0][2]) for i in r if len(i[1]) > 0]

            for link, hoster, mirrors in r:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue
                u = urlparse.parse_qs('&id=%s' % link)
                u = dict([(x, u[x][0]) if u[x] else (x, '') for x in u])
                for x in range(0, int(mirrors)):
                    url = self.mirror_link % (u['id'], u['Hoster'], x + 1)
                    if season and episode: url += "&Season=%s&Episode=%s" % (season, episode)
                    try: sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})
                    except: pass

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url, referer=self.base_link)
            r = json.loads(r)['Stream']
            r = [(dom_parser.parse_dom(r, 'a', req='href'), dom_parser.parse_dom(r, 'iframe', req='src'))]
            r = [i[0][0].attrs['href'] if i[0] else i[1][0].attrs['src'] for i in r if i[0] or i[1]][0]

            if not r.startswith('http'):
                r = urlparse.parse_qs(r)
                r = [r[i][0] if r[i] and r[i][0].startswith('http') else (i, '') for i in r][0]

            return r
        except:
            return

    def __search(self, imdb):
        try:
            l = ['1', '15']

            r = client.request(urlparse.urljoin(self.base_link, self.search_link % imdb))
            r = dom_parser.parse_dom(r, 'table', attrs={'id': 'RsltTableStatic'})
            r = dom_parser.parse_dom(r, 'tr')
            r = [(dom_parser.parse_dom(i, 'a', req='href'), dom_parser.parse_dom(i, 'img', attrs={'alt': 'language'}, req='src')) for i in r]
            r = [(i[0][0].attrs['href'], i[0][0].content, i[1][0].attrs['src']) for i in r if i[0] and i[1]]
            r = [(i[0], i[1], re.findall('.+?(\d+)\.', i[2])) for i in r]
            r = [(i[0], i[1], i[2][0] if len(i[2]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[2]))  # german > german/subbed
            r = [i[0] for i in r if i[2] in l][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'http://%s' % domain
                    r = client.request(url, limit=1, timeout='10')
                    r = dom_parser.parse_dom(r, 'meta', attrs={'name': 'keywords'}, req='content')
                    if r and 'kino.to' in r[0].attrs.get('content').lower():
                        return url
                except:
                    pass
        except:
            pass

        return fallback
