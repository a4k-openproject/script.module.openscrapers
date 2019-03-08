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


import re,urllib,urlparse,json
from openscrapers.modules import client
from openscrapers.modules import control
from openscrapers.modules import source_utils

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['de']
        self.domains = ['pron.ee']
        self.base_link = 'https://www.pron.ee'
        self.search_link = '/api/search/%s/?apikey=%s&getmeta=0&query=%s&count=%d&from=%d'
        self.types = ['stream']
        self.streamLimit = control.setting('pron.limit')
        if self.streamLimit == '': self.streamLimit = 100
        self.streamLimit = int(self.streamLimit)
        self.streamIncrease = 100
        self.api = control.setting('pron.api')
        self.debrid = control.setting('pron.download')
        if self.debrid == 'true': self.types = ['stream', 'download']
        self.extensions = ['mp4', 'mpg', 'mpeg', 'mp2', 'm4v', 'm2v', 'mkv', 'avi', 'flv', 'asf', '3gp', '3g2', 'wmv', 'mov', 'qt', 'webm', 'vob', '']

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
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

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None:
                raise Exception()

            if not (self.api and not self.api == ''):
                raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = int(data['year']) if 'year' in data and not data['year'] == None else None
            season = int(data['season']) if 'season' in data and not data['season'] == None else None
            episode = int(data['episode']) if 'episode' in data and not data['episode'] == None else None
            query = '%s S%02dE%02d' % (title, season, episode) if 'tvshowtitle' in data else '%s %d' % (title, year)

            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            query += ' lang:%s' % self.language[0]
            query = urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, self.search_link)

            hostDict = hostprDict + hostDict

            iterations = self.streamLimit/self.streamIncrease
            last = self.streamLimit - (iterations * self.streamIncrease)
            if not last:
                iterations = iterations - 1
                last = self.streamIncrease
            iterations = iterations + 1

            seen_urls = set()
            for type in self.types:
                searchFrom = 0
                searchCount = self.streamIncrease
                for offset in range(iterations):
                    if iterations == offset + 1: searchCount = last
                    urlNew = url % (type, self.api, query, searchCount, searchFrom)
                    searchFrom = searchFrom + self.streamIncrease

                    results = client.request(urlNew)
                    results = json.loads(results)

                    apistatus  = results['status']
                    if apistatus != 'success': break

                    results = results['result']

                    added = False
                    for result in results:
                        jsonName = result['title']
                        jsonSize = result['sizeinternal']
                        jsonExtension = result['extension']
                        jsonLanguage = result['lang']
                        jsonHoster = result['hostername'].lower()
                        jsonLink = result['hosterurls'][0]['url']

                        if jsonLink in seen_urls: continue
                        seen_urls.add(jsonLink)

                        if not jsonHoster in hostDict: continue

                        if not self.extensionValid(jsonExtension): continue

                        quality, info = source_utils.get_release_quality(jsonName)
                        info.append(self.formatSize(jsonSize))
                        info.append(jsonName)
                        info = '|'.join(info)

                        sources.append({'source' : jsonHoster, 'quality':  quality, 'language' : jsonLanguage, 'url' : jsonLink, 'info': info, 'direct' : False, 'debridonly' : False})
                        added = True

                    if not added:
                        break

            return sources
        except:
            return sources

    def resolve(self, url):
      return url

    def extensionValid(self, extension):
        extension = extension.replace('.', '').replace(' ', '').lower()
        return extension in self.extensions

    def formatSize(self, size):
        if size == 0 or size is None: return ''
        size = int(size) / (1024 * 1024)
        if size > 2000:
            size = size / 1024
            unit = 'GB'
        else:
            unit = 'MB'
        size = '[B][%s %s][/B]' % (size, unit)
        return size
