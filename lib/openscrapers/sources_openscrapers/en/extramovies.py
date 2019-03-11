# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

"""
    OpenScrapers Project

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import base64
import random
import resolveurl

import re
import requests
import time


def clean_search(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|\(|\)|\[|\]|\{|\}|-|:|;|\*|\?|"|\'|<|>|\_|\.|\?', ' ', title).lower()
    title = ' '.join(title.split())
    return title


def random_agent():
    BR_VERS = [
        ['%s.0' % i for i in xrange(18, 43)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111',
         '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
         '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124',
         '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
         '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80'],
        ['11.0']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1',
                'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES),
                                  br_ver=random.choice(BR_VERS[index]))


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['extramovies.co.in','extramovies.host']
        self.base_link = 'http://extramovies.host' # Old  extramovies.cc
        self.sources2 = []


    def movie(self, imdb, title, localtitle, aliases, year):
        return title+'$$$$'+year+'$$$$'+imdb+'$$$$movie'


    def sources(self, url, hostDict, hostprDict):
        data=url.split('$$$$')
        title=data[0]
        year=data[1]
        imdb=data[2]
        if data[3]!='movie':
            return 0
        if 1:#try:
            start_time = time.time()
            search_id = clean_search(title.lower()) 
            start_url = self.base_link + '/?s=' +search_id.replace(' ','+')
            headers={'User-Agent':random_agent()}
            html = requests.get(start_url,headers=headers,timeout=5).content 
            match = re.compile('class="thumbnail">.+?href="(.+?)" title="(.+?)".+?class="rdate">(.+?)</span>.+?</article>',re.DOTALL).findall(html) # Regex info on results page
            for item_url, name ,release in match:
                release = release.strip()
                if year == release:
                    if year in release:
                        self.get_source(item_url,title,year,'','',start_time)
            return self.sources2


    def get_source(self,item_url,title,year,season,episode,start_time):
        if 1:#try:
            rez = item_url
            if '1080' in rez:
                res = '1080p'
            elif '720' in rez:
                res = '720p'
            else: 
                res = 'SD'
            headers={'User-Agent':random_agent()}
            OPEN = requests.get(item_url,headers=headers,timeout=10).content
            Regexs = re.compile('<h4 style="(.+?)</h4>',re.DOTALL).findall(OPEN)
            Regex = re.compile('link=(.+?)"',re.DOTALL).findall(str(Regexs))
            stream = re.compile('href="(.+?)"',re.DOTALL).findall(str(Regexs))
            count = 0
            for links in stream:
                if 'video.php' in links:
                    link = 'https://lh3.googleusercontent.com/'+links.split('=')[1].replace('&#038;s','')+'=m18|User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:61.0) Gecko/20100101 Firefox/61.0'
                    count +=1
                    self.sources2.append({'source': 'Google', 'quality': res,'language': 'en', 'url': link,'direct': True,'debridonly':False})
                elif '/openload.php?url=' in links:
                    link = 'https://openload.co/embed/'+links.split('=')[1]
                    host = link.split('//')[1].replace('www.','')
                    host = host.split('/')[0].split('.')[0].title()
                    if 'Www' not in host:
                        count +=1
                        self.sources2.append({'source': host, 'quality': res,'language': 'en', 'url': link,'direct': False,'debridonly':False})
            for link in Regex:
                try:
                    link = base64.b64decode(link)
                except:pass
                if not resolveurl.HostedMediaFile(link).valid_url():
                    continue
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                if 'Www' not in host:
                    count +=1
                    self.sources2.append({'source': host, 'quality': res,'language': 'en', 'url': link,'direct': False,'debridonly':False})


    def resolve(self, url):
        return url

