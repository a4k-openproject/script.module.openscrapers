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

import base64
import json
import re
import urllib
import urlparse

from openscrapers.modules import anilist
from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import dom_parser
from openscrapers.modules import jsunpack
from openscrapers.modules import source_utils
from openscrapers.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['foxx.to']
        self.base_link = 'http://foxx.to'
        self.search_link = '/wp-json/dooplay/search/?keyword=%s&nonce=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            if not url and source_utils.is_anime('movie', 'imdb', imdb): url = self.__search([anilist.getAlternativTitle(title)] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and source_utils.is_anime('show', 'tvdb', tvdb): url = self.__search([tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)
            url = client.request(url, output='geturl')

            if season == 1 and episode == 1:
                season = episode = ''

            r = client.request(url)
            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'episodios'})
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*%s' % ('-%sx%s' % (season, episode)))})[0].attrs['href']

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url, output='extended')

            headers = r[3]
            headers.update({'Cookie': r[2].get('Set-Cookie'), 'Referer': self.base_link})
            r = r[0]

            rels = dom_parser.parse_dom(r, 'nav', attrs={'class': 'player'})
            rels = dom_parser.parse_dom(rels, 'ul', attrs={'class': 'idTabs'})
            rels = dom_parser.parse_dom(rels, 'li')
            rels = [(dom_parser.parse_dom(i, 'a', attrs={'class': 'options'}, req='href'), dom_parser.parse_dom(i, 'img', req='src')) for i in rels]
            rels = [(i[0][0].attrs['href'][1:], re.findall('/flags/(\w+)\.png$', i[1][0].attrs['src'])) for i in rels if i[0] and i[1]]
            rels = [i[0] for i in rels if len(i[1]) > 0 and i[1][0].lower() == 'de']

            r = [dom_parser.parse_dom(r, 'div', attrs={'id': i}) for i in rels]

            links = re.findall('''(?:link|file)["']?\s*:\s*["'](.+?)["']''', ''.join([i[0].content for i in r]))
            links += [l.attrs['src'] for i in r for l in dom_parser.parse_dom(i, 'iframe', attrs={'class': 'metaframe'}, req='src')]
            links += [l.attrs['src'] for i in r for l in dom_parser.parse_dom(i, 'source', req='src')]

            for i in links:
                try:
                    i = re.sub('\[.+?\]|\[/.+?\]', '', i)
                    i = client.replaceHTMLCodes(i)

                    if '/play/' in i: i = urlparse.urljoin(self.base_link, i)

                    if self.domains[0] in i:
                        i = client.request(i, headers=headers, referer=url)

                        for x in re.findall('''\(["']?(.*)["']?\)''', i):
                            try: i += jsunpack.unpack(base64.decodestring(re.sub('"\s*\+\s*"', '', x))).replace('\\', '')
                            except: pass

                        for x in re.findall('(eval\s*\(function.*?)</script>', i, re.DOTALL):
                            try: i += jsunpack.unpack(x).replace('\\', '')
                            except: pass

                        links = [(match[0], match[1]) for match in re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', i, re.DOTALL)]
                        links = [(x[0].replace('\/', '/'), source_utils.label_to_quality(x[1])) for x in links if '/no-video.mp4' not in x[0]]

                        doc_links = [directstream.google('https://drive.google.com/file/d/%s/view' % match) for match in re.findall('''file:\s*["'](?:[^"']+youtu.be/([^"']+))''', i, re.DOTALL)]
                        doc_links = [(u['url'], u['quality']) for x in doc_links if x for u in x]
                        links += doc_links

                        for url, quality in links:
                            if self.base_link in url:
                                url = url + '|Referer=' + self.base_link

                            sources.append({'source': 'gvideo', 'quality': quality, 'language': 'de', 'url': url, 'direct': True, 'debridonly': False})
                    else:
                        try:
                            # as long as resolveurl get no Update for this URL (So just a Temp-Solution)
                            did = re.findall('youtube.googleapis.com.*?docid=(\w+)', i)
                            if did: i = 'https://drive.google.com/file/d/%s/view' % did[0]

                            valid, host = source_utils.is_host_valid(i, hostDict)
                            if not valid: continue

                            urls, host, direct = source_utils.check_directstreams(i, host)

                            for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'de', 'url': x['url'], 'direct': direct, 'debridonly': False})
                        except:
                            pass
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            n = cache.get(self.__get_nonce, 24)

            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])), n)
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)
            r = json.loads(r)
            r = [(r[i].get('url'), r[i].get('title'), r[i].get('extra').get('date')) for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __get_nonce(self):
        n = client.request(self.base_link)
        try: n = re.findall('nonce"?\s*:\s*"?([0-9a-zA-Z]+)', n)[0]
        except: n = '5d12d0fa54'
        return n
