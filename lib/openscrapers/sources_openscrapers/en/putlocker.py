# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    putlocker scraper for Exodus forks.
    Nov 9 2018 - Checked
    Oct 11 2018 - Cleaned and Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re

from openscrapers.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlockerr.is', 'putlockers.movie']
        # self.base_link = 'https://putlockerr.is'
        self.base_link = 'https://vidsrc.me'


# https://putlockerr.is/embed/tt7286456/
# https://vidsrc.me/embed/tt7286456/


https://vidsrc.me/watch/RjNNRGtjcEU2bDdEMU04eHF5RG9DWmFLUkxQWExKT2pIVGliZUN1T2VrUlJMRGd3SXNkaG1EcHNwak11b3ZCSnpZWG13dUNHTjR1WHJ3dGJwcVI4Y0hteEpteXNUVUxCV2FTdXZNOFJoWTRsTUFSb2w2QjEyR3RVYjNVbGlZKzI4bFVrY0xLSStScVJnR2FXcVFDL3lFaVY1VG9nVmNqaVpLZW1uc2lIT2VLZXZGOExFbFQrOTRwZkRUSjdmS1IxT2xJMVkzSkd5SjQ9
https://vidsrc.xyz/watch/RjNNRGtjcEU2bDdEMU04eHF5RG9DWmFLUkxQWExKT2pIVGliZUN1T2VrUlJMRGd3SXNkaG1EcHNwak11b3ZCSnpZWG13dUNHTjR1WHJ3dGJwcVI4Y0hteEpteXNUVUxCV2FTdXZNOFJoWTRsTUFSb2w2QjEyR3RVYjNVbGlZKzI4bFVrY0xLSStScVJnR2FXcVFDL3lFaVY1VG9nVmNqaVpLZW1uc2lIT2VLZXZGOExFbFQrOTRwZkRUSjdmS1IxT2xJMVkzSkd5SjQ9

        self.search_link = '/embed/%s/'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.base_link + self.search_link % imdb
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
	log_utils.log('urls = %s' % urls, log_utils.LOGDEBUG)
        try:
            sources = []
            r = self.scraper.get(url).content
            try:
                # match = re.compile('<iframe src="(.+?)://(.+?)/(.+?)"').findall(r)
                match = re.compile('<iframe src="(.+?)://(.+?)/(.+?)"').findall(r)
                for http, host, url in match:
                    url = '%s://%s/%s' % (http, host, url)
                    sources.append({'source': host, 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False,
                                    'debridonly': False})
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url
