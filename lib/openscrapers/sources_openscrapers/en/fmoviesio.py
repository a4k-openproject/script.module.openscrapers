# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 05-06-2019 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import traceback
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import log_utils
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['fmoviesto.to']
        self.base_link = 'https://fmoviesto.to'
        self.search_link = '/search.html?keyword=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = cleantitle.getsearch(title)
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % (search_id.replace(':', ' ').replace(' ', '+'))
            search_results = client.request(url)
            match = re.compile('<a href="/watch/(.+?)" title="(.+?)">', re.DOTALL).findall(search_results)
            for row_url, row_title in match:
                row_url = 'https://fmoviesto.to/watch/%s' % row_url
                if cleantitle.get(title) in cleantitle.get(row_title):
                    return row_url
            return
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('FmoviesIO - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            html = client.request(url)
            quality = re.compile('<div>Quanlity: <span class="quanlity">(.+?)</span></div>', re.DOTALL).findall(html)
            for qual in quality:
                quality = source_utils.check_url(qual)
                info = qual
            links = re.compile('var link_.+? = "(.+?)"', re.DOTALL).findall(html)
            for url in links:
                if not url.startswith('http'):
                    url = "https:" + url
                valid, host = source_utils.is_host_valid(url, hostDict)
                if valid:
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url,
                                    'direct': False, 'debridonly': False})
            return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('FmoviesIO - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
