# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re, urllib, urlparse, json

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.reddit.com']
        self.base_link = ['https://www.reddit.com/r/fullmoviesonyoutube/',
                          'https://www.reddit.com/r/fullmoviesonvimeo/',
                          'https://www.reddit.com/r/fullmoviesongoogle/']
        self.search_link = 'search.json?q=%s+%s&restrict_sr=1'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return
           
    def search(self, title, year):
        try:
            content = []
            for link in self.base_link:
                try:
                    query = urlparse.urljoin(link, self.search_link % (urllib.quote(title), year))
                    r = client.request(query)
                    r = json.loads(r)
                    r = r['data']['children'][0]['data']

                    if not cleantitle.get_simple(r['title'].split(year)[0]) == cleantitle.get(title): raise Exception()
                    if not year in r['title']: raise Exception()
                    content = [(r['title'], r['url'])]

                except BaseException: pass
            return content
        except BaseException: return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            urls = self.search(data['title'], data['year'])

            for url in urls:
                try:
                    link = client.replaceHTMLCodes(url[1])
                    link = link.encode('utf-8')
                    if link in sources: continue
                    if 'snahp' in link:
                        data = client.request(link)
                        data = client.parseDOM(data, 'center')
                        data = [i for i in data if 'Hidden Link' in i][0]
                        link = client.parseDOM(data, 'a', ret='href')[0]
                    if 'google' in link:
                        quality, info2 = source_utils.get_release_quality(url[0], link)
                        sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})

                    else:
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(link.strip().lower()).netloc)[0]
                        if host in hostDict:
                            host = host.encode('utf-8')
                            quality, info2 = source_utils.get_release_quality(url[0], link)
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})        
                except BaseException: pass    
            return sources
        except BaseException:
            return sources
            
    def resolve(self, url):
        return url