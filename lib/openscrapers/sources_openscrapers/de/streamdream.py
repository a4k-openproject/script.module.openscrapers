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

import re
import urllib
import urlparse

from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['streamdream.ws']
        self.base_link = 'http://streamdream.ws'
        self.search_link = '/searchy.php?ser=%s'
        self.hoster_link = '/episodeholen2.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            imdb = re.sub('[^0-9]', '', imdb)
            url = self.__search(imdb)
            return urllib.urlencode({'url': url, 'imdb': imdb}) if url else None
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            imdb = re.sub('[^0-9]', '', imdb)
            url = self.__search(imdb)
            return urllib.urlencode({'url': url, 'imdb': imdb}) if url else None
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
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
            if not url:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, data.get('url'))
            season = data.get('season')
            episode = data.get('episode')

            if season and episode:
                r = urllib.urlencode({'imdbid': data['imdb'], 'language': 'de', 'season': season, 'episode': episode})
                r = client.request(urlparse.urljoin(self.base_link, self.hoster_link), XHR=True, post=r)
            else:
                r = client.request(url)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'linkbox'})[0].content
            r = re.compile('(<a.+?/a>)', re.DOTALL).findall(r)
            r = [(dom_parser.parse_dom(i, 'a', req='href'), dom_parser.parse_dom(i, 'img', attrs={'class': re.compile('.*linkbutton')}, req='class')) for i in r]
            r = [(i[0][0].attrs['href'], i[1][0].attrs['class'].lower()) for i in r if i[0] and i[1]]
            r = [(i[0].strip(), 'HD' if i[1].startswith('hd') else 'SD') for i in r]

            for url, quli in r:
                valid, host = source_utils.is_host_valid(url, hostDict)
                if not valid: continue

                sources.append({'source': host, 'quality': quli, 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, imdb):
        try:
            r = client.request(urlparse.urljoin(self.base_link, self.search_link % imdb))
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [i.attrs['href'] for i in r if i]

            if len(r) > 1:
                for i in r:
                    data = client.request(urlparse.urljoin(self.base_link, i))
                    data = re.compile('(imdbid\s*[=|:]\s*"%s"\s*,)' % imdb, re.DOTALL).findall(data)

                    if len(data) >= 1:
                        url = i
            else:
                url = r[0]

            if url:
                return source_utils.strip_domain(url)
        except:
            return
