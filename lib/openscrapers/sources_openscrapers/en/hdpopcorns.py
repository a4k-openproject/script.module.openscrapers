# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    hdpopcorns scraper for Exodus forks.
    Nov 9 2018 - Checked
    Oct 10 2018 - Cleaned and Checked

    Updated and refactored by someone.
    Originally created by others.
'''

import re,requests,traceback,base64,urllib,urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import log_utils
from openscrapers.modules import debrid
from openscrapers.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hdpopcorns.co','hdpopcorns.eu']
        self.base_link = 'http://hdpopcorns.co'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = title.replace(':', ' ').replace(' ', '+').lower()
            start_url = urlparse.urljoin(self.base_link, self.search_link % (search_id))

            search_results = self.scraper.get(start_url).content
            match = re.compile('<header>.+?href="(.+?)" title="(.+?)"',re.DOTALL).findall(search_results)
            for item_url,item_title in match:
                movie_name, movie_year = re.findall("(.*?)(\d+)", item_title)[0]
                if not cleantitle.get(title) == cleantitle.get(movie_name):
                    continue
                if not year in movie_year:
                    continue
                return item_url
        except:
            failure = traceback.format_exc()
            log_utils.log('HDPopcorn - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if url == None: return
        try:
            OPEN = self.scraper.get(url).content
            headers = {'Origin':'http://hdpopcorns.co', 'Referer':url,
                       'X-Requested-With':'XMLHttpRequest', 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            try:
                params = re.compile('FileName1080p.+?value="(.+?)".+?FileSize1080p.+?value="(.+?)".+?value="(.+?)"',re.DOTALL).findall(OPEN)
                for param1, param2,param3 in params:
                    request_url = '%s/select-movie-quality.php' %(self.base_link)
                    form_data = {'FileName1080p':param1,'FileSize1080p':param2,'FSID1080p':param3}
                link = self.scraper.post(request_url, data=form_data, headers=headers,timeout=3).content
                final_url = re.compile('<strong>1080p</strong>.+?href="(.+?)"',re.DOTALL).findall(link)[0]
                sources.append({'source': 'DirectLink', 'quality': '1080p', 'language': 'en', 'url': final_url, 'direct': True, 'debridonly': False})
            except:pass
            try:
                params = re.compile('FileName720p.+?value="(.+?)".+?FileSize720p".+?value="(.+?)".+?value="(.+?)"',re.DOTALL).findall(OPEN)
                for param1, param2,param3 in params:
                    request_url = '%s/select-movie-quality.php' %(self.base_link)
                    form_data = {'FileName720p':param1,'FileSize720p':param2,'FSID720p':param3}
                link = self.scraper.post(request_url, data=form_data, headers=headers,timeout=3).content
                final_url = re.compile('<strong>720p</strong>.+?href="(.+?)"',re.DOTALL).findall(link)[0]
                sources.append({'source': 'DirectLink', 'quality': '720p', 'language': 'en', 'url': final_url, 'direct': True, 'debridonly': False})
            except:pass
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('HDPopcorn - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
        