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
import urlparse

import requests
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['iwannawatch.is']
        self.base_link = 'https://www.iwannawatch.is'
        self.search_link = '/wp-admin/admin-ajax.php?action=bunyad_live_search&query=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = cleantitle.getsearch(title)
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % (search_id.replace(' ', '+').replace('-', '+').replace('++', '+'))
            headers = {'User-Agent': User_Agent}
            search_results = requests.get(url, headers=headers, timeout=10).content
            match = re.compile('<li>.+?<a href="(.+?)".+?title="(.+?)".+?<a href=.+?>(.+?)<', re.DOTALL).findall(
                search_results)
            for row_url, row_title, release in match:
                if cleantitle.get(title) in cleantitle.get(row_title):
                    if year in str(release):
                        return row_url
            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            headers = {'User-Agent': User_Agent}
            html = requests.get(url, headers=headers, timeout=10).content
            try:
                qual = re.compile('<div class="cf">.+?class="quality">(.+?)</td>', re.DOTALL).findall(html)
                for i in qual:
                    quality = source_utils.check_url(i)
                links = re.compile('li class=.+?data-href="(.+?)"', re.DOTALL).findall(html)
                for link in links:
                    if 'http' not in link:
                        link = 'http:' + link
                    host = link.split('//')[1].replace('www.', '')
                    host = host.split('/')[0].split('.')[0].title()
                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if link in str(sources):
                        continue
                    if valid:
                        sources.append(
                            {'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False,
                             'debridonly': False})
                return sources
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
