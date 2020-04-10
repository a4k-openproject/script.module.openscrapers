# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.

import re
from openscrapers.modules import client
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['megashare9.yt']
        self.base_link = 'http://megashare9.yt'

        self.movie_link = '/%s-%s-online'
        self.movie2_link = '/%s-%s-watch-online'
        self.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3555.0 Safari/537.36"}


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            mtitle = cleantitle.geturl(title)
            link1 = self.base_link + self.movie_link % (mtitle, year)
            link2 = self.base_link + self.movie2_link % (mtitle, year)
            url = link1 + '+++' + link2
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            link1 = url.split('+++')[0]
            link2 = url.split('+++')[1]
            r = client.request(link1, headers=self.headers)
            if not r:
                r = client.request(link2, headers=self.headers)
            match = re.compile('<iframe.+?src="(.+?)"').findall(r)
            for link in match:
                hostDict = hostDict + hostprDict
                valid, host = source_utils.is_host_valid(link, hostDict)
                if valid:
                    quality, info = source_utils.get_release_quality(link, link)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': link, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


