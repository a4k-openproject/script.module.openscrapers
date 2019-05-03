# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'rmz.cr'
        self.base_link = 'http://rmz.cr/'
        self.search_link = self.base_link + 'search/%s/releases/exact/'
        self.search_options_movie = 'm/'
        self.search_options_series = 's/'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        url = {'imdb': imdb, 'title': title, 'year': year}
        url = urllib.urlencode(url)
        return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
        url = urllib.urlencode(url)
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        url = urlparse.parse_qs(url)
        url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
        url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
        url = urllib.urlencode(url)
        return url

    def sources(self, url, hostDict, hostprDict):
        try:
            hostDict = hostDict + hostprDict

            sources = []
            query_bases = []
            options = []

            if url is None:
                return sources

            if not debrid.status():
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = (data['tvshowtitle'] if 'tvshowtitle' in data else data['title'])
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            # tvshowtitle
            if 'tvshowtitle' in data:
                query_bases.append('%s ' % (data['tvshowtitle'].replace("-", "")))
                if 'year' in data:
                    query_bases.append('%s %s ' % (data['tvshowtitle'], data['year']))
                options.append('S%02dE%02d' % (int(data['season']), int(data['episode'])))
                options.append('S%02d' % (int(data['season'])))
            else:
                query_bases.append('%s %s ' % (data['title'], data['year']))
                query_bases.append('%s ' % (data['title']))
                query_bases.append('2160p')
                query_bases.append('')

            for option in options:
                for query_base in query_bases:
                    q = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query_base + option)
                    q = q.replace("  ", " ").replace(" ", "+")
                    url = self.search_link % q
                    html = self.scraper.get(url)
                    if html.status_code == 200:
                        links = client.parseDOM(html.content, "div", attrs={"class": "list_items"})
                        if len(links) == 0:
                            continue
                        items = client.parseDOM(links, "a", ret='href')
                        if len(items) == 0:
                            continue
                        for url in items:
                            if len(url) == 0:
                                continue
                            html = self.scraper.get(self.base_link + url)
                            if html.status_code == 200:
                                link_blocks = client.parseDOM(html.content, "pre", attrs={"class": "links"})
                                for linkBlock in link_blocks:
                                    for href in linkBlock.splitlines():
                                        quality = source_utils.check_sd_url(href)
                                        href = href.encode('utf-8')
                                        valid, host = source_utils.is_host_valid(href, hostDict)
                                        if not valid:
                                            continue
                                        if any(x in href for x in ['.rar', '.zip', '.iso']):
                                            continue
                                        if hdlr in href.upper() and cleantitle.get(title) in cleantitle.get(href):
                                            sources.append(
                                                {'source': host, 'quality': quality, 'language': 'en', 'url': href,
                                                 'direct': False, 'debridonly': False})
                if len(sources) > 0:
                    return sources
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
