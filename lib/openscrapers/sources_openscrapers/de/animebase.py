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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import tvmaze
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['anime-base.net']
        self.base_link = 'http://anime-base.net'
        self.search_link = '/suche_ajax.php'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = None
            for title in [tvshowtitle, localtvshowtitle, tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(aliases):
                if url: break
                url = self.__search(title)
            return urllib.urlencode({'url': url}) if url else None
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            episode = tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            data.update({'episode': episode})
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
            url = data.get('url')
            episode = int(data.get('episode', 1))

            r = client.request(urlparse.urljoin(self.base_link, url))
            r = {'': dom_parser.parse_dom(r, 'div', attrs={'id': 'gerdub'}), 'subbed': dom_parser.parse_dom(r, 'div', attrs={'id': 'gersub'})}

            for info, data in r.iteritems():
                data = dom_parser.parse_dom(data, 'tr')
                data = [dom_parser.parse_dom(i, 'a', req='href') for i in data if dom_parser.parse_dom(i, 'a', attrs={'id': str(episode)})]
                data = [(link.attrs['href'], dom_parser.parse_dom(link.content, 'img', req='src')) for i in data for link in i]
                data = [(i[0], i[1][0].attrs['src']) for i in data if i[1]]
                data = [(i[0], re.findall('/(\w+)\.\w+', i[1])) for i in data]
                data = [(i[0], i[1][0]) for i in data if i[1]]

                for link, hoster in data:
                    valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                    if not valid: continue

                    sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'info': info, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if not url.startswith('http'): url = urlparse.urljoin(self.base_link, url)

            if self.base_link in url:
                r = client.request(url)
                r = dom_parser.parse_dom(r, 'meta', req='content')[0]
                r = r.attrs['content']
                r = re.findall('''url\s*=\s*([^'"]+)''', r, re.I)
                if r:
                    url = r[0]

            return url
        except:
            return

    def __search(self, title):
        try:
            t = cleantitle.get(title)

            r = client.request(urlparse.urljoin(self.base_link, self.search_link), post={'suchbegriff': title})
            r = dom_parser.parse_dom(r, 'a', attrs={'class': 'ausgabe_1'}, req='href')
            r = [(i.attrs['href'], i.content) for i in r]
            r = [i[0] for i in r if cleantitle.get(i[1]) == t][0]

            return source_utils.strip_domain(r)
        except:
            return
