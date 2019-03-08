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

import base64
import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['streamit.ws']
        self.base_link = 'https://streamit.ws'
        self.search_link = '/livesearch.php'
        self.episode_link = '/lade_episode.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
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
            url = urlparse.urljoin(self.base_link, data.get('url', ''))
            imdb = data.get('imdb')
            season = data.get('season')
            episode = data.get('episode')

            if season and episode and imdb:
                r = urllib.urlencode({'val': 's%se%s' % (season, episode), 'IMDB': imdb})
                r = client.request(urlparse.urljoin(self.base_link, self.episode_link), XHR=True, post=r)
            else:
                r = client.request(url)

            l = dom_parser.parse_dom(r, 'select', attrs={'id': 'sel_sprache'})
            l = dom_parser.parse_dom(l, 'option', req='id')

            r = [(dom_parser.parse_dom(r, 'div', attrs={'id': i.attrs['id']})) for i in l if i.attrs['id'] == 'deutsch']
            r = [(i[0], dom_parser.parse_dom(i[0], 'option', req='id')) for i in r]
            r = [(id.attrs['id'], dom_parser.parse_dom(content, 'div', attrs={'id': id.attrs['id']})) for content, ids in r for id in ids]
            r = [(re.findall('hd(\d{3,4})', i[0]), dom_parser.parse_dom(i[1], 'a', req='href')) for i in r if i[1]]
            r = [(i[0][0] if i[0] else '0', [x.attrs['href'] for x in i[1]]) for i in r if i[1]]
            r = [(source_utils.label_to_quality(i[0]), i[1]) for i in r]

            for quality, urls in r:
                for link in urls:
                    try:
                        data = urlparse.parse_qs(urlparse.urlparse(link).query, keep_blank_values=True)

                        if 'm' in data:
                            data = data.get('m')[0]
                            link = base64.b64decode(data)

                        link = link.strip()

                        valid, host = source_utils.is_host_valid(link, hostDict)
                        if not valid: continue

                        sources.append({'source': host, 'quality': quality, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False, 'checkquality': True})
                    except:
                        pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(urlparse.urljoin(self.base_link, self.search_link), post=urllib.urlencode({'val': cleantitle.query(titles[0])}), XHR=True)
            r = dom_parser.parse_dom(r, 'li')
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content, re.findall('\((\d{4})', i.content)) for i in r]
            r = [(i[0], i[1], i[2][0] if i[2] else '0') for i in r]
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return
