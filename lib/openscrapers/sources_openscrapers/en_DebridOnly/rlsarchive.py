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
        self.domain = 'rls4u.net'
        self.base_link = 'http://rlsarchive.com'
        self.search_link = '/index.php?do=search&subaction=search&story=%s'
        self.search_options = '&search_start=0&full_search=1&result_from=1&titleonly=3&searchuser=&replyless=1' \
                              '&replylimit=0&searchdate=0&beforeafter=after&sortby=date&resorder=desc&showposts=0' \
                              '&catlist%5B%5D=11&catlist%5B%5D=12&catlist%5B%5D=13&catlist%5B%5D=14'
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
                    url = self.base_link + url + self.search_options
                    html = self.scraper.get(url)
                    if html.status_code == 200:
                        posts = client.parseDOM(html.content, "div", attrs={"class": "post-head"})
                        for post in posts:
                            url = client.parseDOM(post, "a", ret='href')
                            if len(url) > 0:
                                html = self.scraper.get(url[0])
                                if html.status_code == 200:
                                    quotes = client.parseDOM(html.content, "div", attrs={"class": "quote"})
                                    for quote in quotes:
                                        hrefs = client.parseDOM(quote, "a", ret='href')
                                        if not hrefs:
                                            continue
                                        for href in hrefs:
                                            quality = source_utils.check_sd_url(href)
                                            href = href.encode('utf-8')
                                            valid, host = source_utils.is_host_valid(href, hostDict)
                                            if any(x in href for x in ['.rar', '.zip', '.iso']):
                                                continue
                                            if not valid:
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
