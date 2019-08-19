# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 04-15-2019 by JewBMX in Scrubs.
# Created by Tempest

import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['yifyddl.movie']
        self.base_link = 'https://yifyddl.movie/'
        self.search_link = '/movie/%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None: return sources
            if debrid.status() is False: raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            query = '%s %s' % (data['title'], data['year'])
            url = self.search_link % urllib.quote(query)
            url = urlparse.urljoin(self.base_link, url).replace('%20', '-')
            html = self.scraper(url).content
            try:
                results = client.parseDOM(html, 'div', attrs={'class': 'ava1'})
            except:
                return sources
            for torrent in results:
                link = re.findall('a data-torrent-id=".+?" href="(magnet:.+?)" class=".+?" title="(.+?)"', torrent,
                                  re.DOTALL)
                for link, name in link:
                    link = str(client.replaceHTMLCodes(link).split('&tr')[0])
                    quality, info = source_utils.get_release_quality(name, name)
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', torrent)[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except Exception:
                        pass
                    info = ' | '.join(info)
                    sources.append(
                        {'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': link, 'info': info,
                         'direct': False, 'debridonly': True})
            return sources
        except:
            return

    def resolve(self, url):
        return url
