# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 12-07-2018 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import requests

from openscrapers.modules import cleantitle, source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['animetoon.org','animetoon.tv']
        self.base_link = 'http://www.animetoon.org'
        


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = '%s %s' % (title,year)
            return url
        except:
            return
			
			
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return
 
 
    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            if season == '1': 
                url = self.base_link + '/' + url + '-episode-' + episode
            else:
                url = self.base_link + '/' + url + '-season-' + season + '-episode-' + episode
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            User_Agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
            headers = {'User-Agent':User_Agent}
            r = requests.get(url,headers=headers,allow_redirects=False).content
            try:
                match = re.compile('<div><iframe src="(.+?)"').findall(r)
                for url in match:
                    host = url.split('//')[1].replace('www.','')
                    host = host.split('/')[0].split('.')[0].title()
                    quality = source_utils.check_sd_url(url)
                    r = requests.get(url,headers=headers,allow_redirects=False).content
                    if 'http' in url:
                        match = re.compile("url: '(.+?)',").findall(r)
                    else:
                        match = re.compile('file: "(.+?)",').findall(r)
                    for url in match:
                        sources.append({'source': host, 'quality': quality, 'language': 'en','url': url,'direct': False,'debridonly': False}) 
            except:
                return
        except Exception:
            return
        return sources


    def resolve(self, url):
        return url
        
        