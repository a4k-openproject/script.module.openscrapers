# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

# -Cleaned and Checked on 04-15-2019 by JewBMX in Scrubs.


import json
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser2
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchepisodeseries.com', 'watchepisodeseries.unblocked.cx']
        self.base_link = 'http://www.watchepisodeseries.com/'
        self.search_link = '/home/search?q=%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            simple_title = cleantitle.get_simple(tvshowtitle)
            tvshowtitle = cleantitle.geturl(tvshowtitle).replace('-', '+')
            search_url = urlparse.urljoin(self.base_link, self.search_link % tvshowtitle)
            r = client.request(search_url)
            r = json.loads(r)['series']
            r = [(urlparse.urljoin(self.base_link, i['seo_name'])) for i in r if
                 simple_title == cleantitle.get_simple(i['original_name'])]
            if r:
                return r[0]
            else:
                return
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'div', {'class': 'el-item'})
            r = [(dom_parser2.parse_dom(i, 'div', {'class': 'season'}), \
                  dom_parser2.parse_dom(i, 'div', {'class': 'episode'}), \
                  dom_parser2.parse_dom(i, 'a', req='href')) \
                 for i in r if i]
            r = [(i[2][0].attrs['href']) for i in r if i[0][0].content == 'Season %01d' % int(season) \
                 and i[1][0].content == 'Episode %01d' % int(episode)]
            if r:
                return r[0]
            else:
                return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            results_limit = 30
            vshare_limit = 1
            openload_limit = 1
            speedvid_limit = 1
            vidoza_limit = 1
            vidlox_limit = 1
            mango_limit = 1
            streamplay_limit = 1
            vidtodo_limit = 1
            clipwatch_limit = 1
            vidcloud_limit = 1
            vev_limit = 1
            flix555_limit = 1
            if url == None: return sources
            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'div', {'class': 'll-item'})
            r = [(dom_parser2.parse_dom(i, 'a', req='href'), \
                  dom_parser2.parse_dom(i, 'div', {'class': 'notes'})) \
                 for i in r if i]
            r = [(i[0][0].attrs['href'], i[0][0].content, i[1][0].content if i[1] else 'None') for i in r]
            for i in r:
                try:
                    url = i[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    valid, host = source_utils.is_host_valid(i[1], hostDict)
                    if not valid: continue
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if 'vshare' in host:
                        if vshare_limit < 1:
                            continue
                        else:
                            vshare_limit -= 1
                    if 'openload' in host:
                        if openload_limit < 1:
                            continue
                        else:
                            openload_limit -= 1
                    if 'speedvid' in host:
                        if speedvid_limit < 1:
                            continue
                        else:
                            speedvid_limit -= 1
                    if 'vidoza' in host:
                        if vidoza_limit < 1:
                            continue
                        else:
                            vidoza_limit -= 1
                    if 'vidlox' in host:
                        if vidlox_limit < 1:
                            continue
                        else:
                            vidlox_limit -= 1
                    if 'vidtodo' in host:
                        if vidtodo_limit < 1:
                            continue
                        else:
                            vidtodo_limit -= 1
                    if 'mango' in host:
                        if mango_limit < 1:
                            continue
                        else:
                            mango_limit -= 1
                    if 'streamplay' in host:
                        if streamplay_limit < 1:
                            continue
                        else:
                            streamplay_limit -= 1
                    if 'clipwatch' in host:
                        if clipwatch_limit < 1:
                            continue
                        else:
                            clipwatch_limit -= 1
                    if 'vidcloud' in host:
                        if vidcloud_limit < 1:
                            continue
                        else:
                            vidcloud_limit -= 1
                    if 'vev' in host:
                        if vev_limit < 1:
                            continue
                        else:
                            vev_limit -= 1
                    if 'flix555' in host:
                        if flix555_limit < 1:
                            continue
                        else:
                            flix555_limit -= 1
                    info = []
                    quality, info = source_utils.get_release_quality(i[2], i[2])
                    info = ' | '.join(info)
                    if results_limit < 1:
                        continue
                    else:
                        results_limit -= 1
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'a', req=['href', 'data-episodeid', 'data-linkid'])[0]
            url = r.attrs['href']
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
