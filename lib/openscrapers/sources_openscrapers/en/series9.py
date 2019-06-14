#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

# -Cleaned and Checked on 04-15-2019 by JewBMX in Scrubs.
''''
    Updated and refactored by someone.
    Originally created by others.
'''
import re
import traceback
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['series9.io', 'series9.co', 'seriesonline.io', 'series9.io', 'gomovies.pet']
        self.base_link = 'https://www2.series9.io/'
        self.search_link = 'https://api.ocloud.stream/series/movie/search/%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': cleantitle.getsearch(title), 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': cleantitle.getsearch(tvshowtitle), 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
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
        except:
            return

    def searchShow(self, title, season):
        title = cleantitle.normalize(title)
        search = '%s Season %01d' % (title, int(season))
        url = self.search_link % cleantitle.geturl(search)
        r = self.scraper.get(url, params={'link_web': self.base_link}).content
        r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
        r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
        r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
        r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
        url = [i[0] for i in r if cleantitle.get(i[2][0]) == cleantitle.get(title) and i[2][1] == season][0]
        url = urlparse.urljoin(self.base_link, '%s/watching.html' % url)
        return url

    def searchMovie(self, title, year):
        title = cleantitle.normalize(title)
        url = self.search_link % cleantitle.geturl(title)
        r = self.scraper.get(url, params={'link_web': self.base_link}).content
        r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
        r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
        results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
        try:
            r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
            url = [i[0] for i in r if cleantitle.get(i[1]).endswith(cleantitle.get(title)) and (year == i[2])][0]
        except:
            url = None
            pass

        try:
            if url is None:
                url = [i[0] for i in results if cleantitle.get(i[1]).endswith(cleantitle.get(title))][0]
        except:
            url = None
            pass

        return url

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            if 'tvshowtitle' in data:
                url = self.searchShow(data['tvshowtitle'], data['season'])
            else:
                url = self.searchMovie(data['title'], data['year'])

            if url is None:
                return sources

            r = self.scraper.get(url, params={'link_web': self.base_link}).content
            quality = client.parseDOM(r, 'span', attrs={'class': 'quality'})[0]
            quality = source_utils.check_sd_url(quality)
            r = client.parseDOM(r, 'div', attrs={'class': 'les-content'})

            if 'tvshowtitle' in data:
                ep = data['episode']
                links = client.parseDOM(r, 'a', attrs={'episode-data': ep}, ret='player-data')
            else:
                links = client.parseDOM(r, 'a', ret='player-data')

            for link in links:
                if '123movieshd' in link or 'seriesonline' in link:
                    r = self.scraper.get(url, data={'link_web': self.base_link}).content
                    r = re.findall('(https:.*?redirector.*?)[\'\"]', r)

                    for i in r:
                        try:
                            sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'],
                                            'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                        except:
                            traceback.print_exc()
                            pass
                else:
                    try:
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(link.strip().lower()).netloc)[0]
                        if host not in hostDict:
                            pass
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': [],
                                        'direct': False, 'debridonly': False})
                    except:
                        pass
            return sources
        except:
            traceback.print_exc()
            return sources

    def resolve(self, url):
        if "google" in url:
            return directstream.googlepass(url)
        else:
            return url
