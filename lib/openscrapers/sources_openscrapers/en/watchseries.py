# -*- coding: utf-8 -*-


import re,urllib,urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watch-series.co','watch-series.ru']
        self.base_link = 'https://ww3.watch-series.co'
        self.search_link = '/series/%s-season-%s-episode-%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle.replace(" ", "-").lower()
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link % (url, season, episode))
            print url
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None:
                return

            hostDict =  hostDict + hostprDict
            result = client.request(url)
            print result

            dom = dom_parser.parse_dom(result, 'a', req='data-video')
            urls = [i.attrs['data-video'] if i.attrs['data-video'].startswith('https') else 'https:' + i.attrs['data-video'] for i in dom]
            print urls

            for url in urls:
                valid, hoster = source_utils.is_host_valid(url, hostDict)
                if not valid: continue
                try:
                    url.decode('utf-8')
                    sources.append({'source': hoster, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
