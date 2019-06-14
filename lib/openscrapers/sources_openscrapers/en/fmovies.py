# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import json
import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['fmovies.sc']
        self.base_link = 'http://www4.fmovies.sc'
        self.search_link = '/search/%s+%s.html'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, (self.search_link % (clean_title, year)))
            search_results = self.scraper.get(search_url, headers={'referer': self.base_link}).content

            not_found = dom_parser.parse_dom(search_results, 'div', {'class': 'not-found'})
            if len(not_found) > 0:
                return

            links = client.parseDOM(search_results, "a", ret="href", attrs={"class": "ml-mask jt"})
            results = []
            for link in links:
                if '%s%s' % (cleantitle.get(title), year) in cleantitle.get(link):
                    results.append(link)
            return results
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            clean_title = cleantitle.geturl(url['tvshowtitle']) + '+s%02d' % int(season)
            search_url = urlparse.urljoin(self.base_link, (self.search_link % (clean_title.replace('-', '+'),
                                                                               url['year'])))
            search_results = self.scraper.get(search_url, headers={'referer': self.base_link}).content

            not_found = dom_parser.parse_dom(search_results, 'div', {'class': 'not-found'})
            if len(not_found) > 0:
                return

            links = client.parseDOM(search_results, "a", ret="href", attrs={"class": "ml-mask jt"})
            results = []
            for link in links:
                if '%ss%02d' % (cleantitle.get(url['tvshowtitle']), int(season)) in cleantitle.get(link):
                    link_results = self.scraper.get(link, headers={'referer': search_url}).content
                    r2 = dom_parser.parse_dom(link_results, 'div', {'id': 'ip_episode'})
                    r3 = [dom_parser.parse_dom(i, 'a', req=['href']) for i in r2 if i]
                    for i in r3[0]:
                        if i.content == 'Episode %s' % episode:
                            results.append(i.attrs['href'])
            return results
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            if url is None:
                return sources

            for href in url:
                r = self.scraper.get(href).content

                quality = re.findall(">(\w+)<\/p", r)
                if quality[0] == "HDHC":
                    quality = "1080p"
                elif quality[0] == "HD":
                    quality = "720p"
                else:
                    quality = quality[0]
                r = dom_parser.parse_dom(r, 'div', {'id': 'servers-list'})
                r = [dom_parser.parse_dom(i, 'a', req=['href']) for i in r if i]

                for i in r[0]:
                    href = {'url': i.attrs['href'], 'data-film': i.attrs['data-film'],
                            'data-server': i.attrs['data-server'], 'data-name': i.attrs['data-name']}

                    href = urllib.urlencode(href)

                    valid, host = source_utils.is_host_valid(i.content, hostDict)

                    if valid:
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': href,
                                        'direct': False, 'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            post = {'ipplugins': 1, 'ip_film': urldata['data-film'], 'ip_server': urldata['data-server'],
                    'ip_name': urldata['data-name'], 'fix': "0"}
            p1 = self.scraper.request(url.join(self.base_link, '/ip.file/swf/plugins/ipplugins.php'), post=post,
                                      referer=urldata['url'], XHR=True).content
            p1 = json.loads(p1)
            p2 = self.scraper.request(url.join(self.base_link, '/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=0') % (
                p1['s'], urldata['data-server'])).content
            p2 = json.loads(p2)
            p3 = self.scraper.request(
                url.join(self.base_link, '/ip.file/swf/ipplayer/api.php?hash=%s') % (p2['hash'])).content
            p3 = json.loads(p3)
            n = p3['status']
            if not n:
                p2 = self.scraper.request(url.join(self.base_link, '/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=1')
                                          % (p1['s'], urldata['data-server'])).content
                p2 = json.loads(p2)
            url = "https:%s" % p2["data"].replace("\/", "/")
            return url
        except:
            return
