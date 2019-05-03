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
import re, traceback, urllib, urlparse

from openscrapers.modules import cleantitle, client, directstream, log_utils, source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['series9.io', 'series9.co', 'seriesonline.io', 'series9.io', 'gomovies.pet']
        self.base_link = 'https://api.ocloud.stream/series'
        self.search_link = '/movie/search/%s'
        self.link_web = '?link_web=https%3A%2F%2Fwww2.series9.io%2F'

    def matchAlias(self, title, aliases):
        for alias in aliases:
            if cleantitle.get(title) == cleantitle.get(alias['title']):
                return True

    def movie(self, imdb, title, localtitle, aliases, year):
        aliases.append({'country': 'us', 'title': title})
        url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
        url = urllib.urlencode(url)
        return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        aliases.append({'country': 'us', 'title': tvshowtitle})
        url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
        url = urllib.urlencode(url)
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url is None:
            return
        url = urlparse.parse_qs(url)
        url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
        url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
        url = urllib.urlencode(url)
        return url

    def searchShow(self, title, season, aliases, headers):
        title = cleantitle.normalize(title)
        search = '%s Season %01d' % (title, int(season))
        url = urlparse.urljoin(self.base_link, self.search_link % cleantitle.geturl(search)) + self.link_web
        r = client.request(url, headers=headers, timeout='15')
        r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
        r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
        r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d)', i[1])) for i in r]
        r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
        url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == season][0]
        url = urlparse.urljoin(self.base_link, '%s/watching.html' % url)
        return url

    def searchMovie(self, title, year, aliases, headers):
        title = cleantitle.normalize(title)
        url = urlparse.urljoin(self.base_link, (self.search_link % cleantitle.geturl(title))) + self.link_web
        r = client.request(url, headers=headers, timeout='15')
        r = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
        r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
        results = [(i[0], i[1], re.findall('\((\d{4})', i[1])) for i in r]
        try:
            r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
            url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
        except:
            url = None
            log_utils.log('series9 - Exception: \n' + str(traceback.format_exc()))
            pass

        if (url == None):
            url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]

        url = urlparse.urljoin(self.base_link, '%s/watching.html' % url)
        return url


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                ep = data['episode']
                url = '%s/film/%s-season-%01d/watching.html?ep=%s' % (self.base_link, cleantitle.geturl(data['tvshowtitle']), int(data['season']), ep)
                r = client.request(url, headers=headers, timeout='10', output='geturl')

                if url == None:
                    url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)

            else:
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            if url == None: return sources

            r = client.request(url, headers=headers, timeout='10')
            r = client.parseDOM(r, 'div', attrs={'class': 'les-content'})
            if 'tvshowtitle' in data:
                ep = data['episode']
                links = client.parseDOM(r, 'a', attrs={'episode-data': ep}, ret='player-data')
            else:
                links = client.parseDOM(r, 'a', ret='player-data')

            for link in links:
                if '123movieshd' in link or 'seriesonline' in link:
                    r = client.request(link, headers=headers, timeout='10')
                    r = re.findall('(https:.*?redirector.*?)[\'\"]', r)

                    for i in r:
                        try:
                            sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'],
                                            'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                        except:
                            pass
                else:
                    try:
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(link.strip().lower()).netloc)[0]
                        if host not in hostDict:
                            pass
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        quality, info = source_utils.get_release_quality(url)

                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info,
                                        'direct': False, 'debridonly': False})
                    except:
                        pass

            return sources
        except:
            return sources

    def resolve(self, url):
        if "google" in url:
            return directstream.googlepass(url)
        else:
            return url
