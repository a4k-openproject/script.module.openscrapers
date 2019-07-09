# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

# -Cleaned and Checked on 04-15-2019 by JewBMX in Scrubs.


import json
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchepisodeseries.com', 'watchepisodeseries.unblocked.cx']
        self.base_link = 'http://www.watchepisodeseries.com/'
        self.search_link = '/home/search?q=%s'
        self.scraper = cfscrape.create_scraper()

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            simple_title = cleantitle.get_simple(tvshowtitle)
            tvshowtitle = cleantitle.geturl(tvshowtitle).replace('-', '+')
            search_url = urlparse.urljoin(self.base_link, self.search_link % tvshowtitle)
            r = self.scraper.get(search_url).content
            r = json.loads(r)['series']
            r = [(urlparse.urljoin(self.base_link, i['seo_name'])) for i in r if
                 simple_title == cleantitle.get_simple(i['original_name'])]
            if r:
                return r[0]
            else:
                return
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            r = self.scraper.get(url).content
            r = dom_parser.parse_dom(r, 'div', {'class': 'el-item'})
            r = [(dom_parser.parse_dom(i, 'div', {'class': 'season'}), \
                  dom_parser.parse_dom(i, 'div', {'class': 'episode'}), \
                  dom_parser.parse_dom(i, 'a', req='href')) \
                 for i in r if i]
            r = [(i[2][0].attrs['href']) for i in r if i[0][0].content == 'Season %01d' % int(season) \
                 and i[1][0].content == 'Episode %01d' % int(episode)]
            if r:
                return r[0]
            else:
                return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None:
                return sources
            r = self.scraper.get(url).content
            r = dom_parser.parse_dom(r, 'div', {'class': 'll-item'})
            r = [(dom_parser.parse_dom(i, 'a', req='href'), \
                  dom_parser.parse_dom(i, 'div', {'class': 'notes'})) \
                 for i in r if i]
            r = [(i[0][0].attrs['href'], i[0][0].content, i[1][0].content if i[1] else 'None') for i in r]
            for i in r:
                try:
                    url = i[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    valid, host = source_utils.is_host_valid(i[1], hostDict)
                    if not valid:
                        continue
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    info = []
                    quality, info = source_utils.get_release_quality(i[1], i[2])
                    info = ' | '.join(info)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            r = client.request(url)
            r = dom_parser.parse_dom(r, 'a', req=['href', 'data-episodeid', 'data-linkid'])[0]
            url = r.attrs['href']
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
