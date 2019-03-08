# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import json
import re
import urllib
import urlparse
import base64

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['tata.to']
        self.base_link = 'http://tata.to'
        self.search_link = '/filme?suche=%s&type=alle'
        self.ajax_link = '/ajax/stream/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search_movie(imdb, year)
            return url if url else None
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'aliases': aliases, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            tvshowtitle = data['tvshowtitle']
            localtvshowtitle = data['localtvshowtitle']
            aliases = source_utils.aliases_to_array(eval(data['aliases']))

            year = re.findall('(\d{4})', premiered)
            year = year[0] if year else data['year']

            url = self.__search([localtvshowtitle] + aliases, year, season, episode)
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search([tvshowtitle] + aliases, year, season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            ref = urlparse.urljoin(self.base_link, url)
            url = urlparse.urljoin(self.base_link, self.ajax_link % re.findall('-(\w+)$', ref)[0])

            headers = {'Referer': ref, 'User-Agent': client.randomagent()}

            result = client.request(url, headers=headers, post='')
            result = base64.decodestring(result)
            result = json.loads(result).get('playinfo', [])

            if isinstance(result, basestring):
                result = result.replace('embed.html', 'index.m3u8')

                base_url = re.sub('index\.m3u8\?token=[\w\-]+[^/$]*', '', result)

                r = client.request(result, headers=headers)
                r = [(i[0], i[1]) for i in re.findall('#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(\d+)[^\n]+\n([^\n]+)', r, re.DOTALL) if i]
                r = [(source_utils.label_to_quality(i[0]), i[1] + source_utils.append_headers(headers)) for i in r]
                r = [{'quality': i[0], 'url': base_url+i[1]} for i in r]
                for i in r: sources.append({'source': 'CDN', 'quality': i['quality'], 'language': 'de', 'url': i['url'], 'direct': True, 'debridonly': False})
            elif result:
                result = [i.get('link_mp4') for i in result]
                result = [i for i in result if i]
                for i in result:
                    try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'de', 'url': i, 'direct': True, 'debridonly': False})
                    except: pass

            return sources
        except:
            return

    def resolve(self, url):
        return url

    def __search_movie(self, imdb, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % imdb)

            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'container'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'ml-item-content'})
            r = [(dom_parser.parse_dom(i, 'a', attrs={'class': 'ml-image'}, req='href'), dom_parser.parse_dom(i, 'ul', attrs={'class': 'item-params'})) for i in r]
            r = [(i[0][0].attrs['href'], re.findall('calendar.+?>.+?(\d{4})', ''.join([x.content for x in i[1]]))) for i in r if i[0] and i[1]]
            r = [(i[0], i[1][0] if len(i[1]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[1]), reverse=True)  # with year > no year
            r = [i[0] for i in r if i[1] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __search(self, titles, year, season=0, episode=False):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'container'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'ml-item-content'})

            f = []
            for i in r:
                _url = dom_parser.parse_dom(i, 'a', attrs={'class': 'ml-image'}, req='href')[0].attrs['href']

                _title = re.sub('<.+?>|</.+?>', '', dom_parser.parse_dom(i, 'h6')[0].content).strip()
                try: _title = re.search('(.*?)\s(?:staf+el|s)\s*(\d+)', _title, re.I).group(1)
                except: pass

                _season = '0'

                _year = re.findall('calendar.+?>.+?(\d{4})', ''.join([x.content for x in dom_parser.parse_dom(i, 'ul', attrs={'class': 'item-params'})]))
                _year = _year[0] if len(_year) > 0 else '0'

                if season > 0:
                    s = dom_parser.parse_dom(i, 'span', attrs={'class': 'season-label'})
                    s = dom_parser.parse_dom(s, 'span', attrs={'class': 'el-num'})
                    if s: _season = s[0].content.strip()

                if cleantitle.get(_title) in t and _year in y and int(_season) == int(season):
                    f.append((_url, _year))
            r = f
            r = sorted(r, key=lambda i: int(i[1]), reverse=True)  # with year > no year
            r = [i[0] for i in r if r[0]][0]

            url = source_utils.strip_domain(r)
            if episode:
                r = client.request(urlparse.urljoin(self.base_link, url))
                r = dom_parser.parse_dom(r, 'div', attrs={'class': 'season-list'})
                r = dom_parser.parse_dom(r, 'li')
                r = dom_parser.parse_dom(r, 'a', req='href')
                r = [(i.attrs['href'], i.content) for i in r]
                r = [i[0] for i in r if i[1] and int(i[1]) == int(episode)][0]
                url = source_utils.strip_domain(r)
            return url
        except:
            return
