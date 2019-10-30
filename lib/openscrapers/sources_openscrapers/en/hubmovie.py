# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# Need to add a year check in sometime to make sure there isnt false hits.

import re

from openscrapers.modules import client
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hubmovie.cc', 'hubmoviehd.net']
        self.base_link = 'http://hubmovie.cc'
        self.search_link = '/pages/search2/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = cleantitle.getsearch(title)
            search_url = self.base_link + self.search_link  %(search_id.replace(':', ' ').replace(' ', '%20'))
            search_results = client.request(search_url)
            match = re.compile('<a href=".(.+?)">',re.DOTALL).findall(search_results)
            for link in match:
                if cleantitle.geturl(title).lower() in link:
                    url = self.base_link + link
                    return url
            return
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostDict + hostprDict
            if url == None:
                return sources
            html = client.request(url)
            links = re.compile('<div class="link_go">.+?<a href="(.+?)" target="_blank">',re.DOTALL).findall(html)
            for link in links:
                valid, host = source_utils.is_host_valid(link, hostDict)
                if valid:
                    quality,info = source_utils.get_release_quality(link, link)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


