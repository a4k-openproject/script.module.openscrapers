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
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# -Cleaned and Checked on 11-13-2018 by JewBMX in Scrubs.

import re,urllib,urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser2

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['300mbfilms.co']
        self.base_link = 'https://300mbfilms.co' #https://www.300mbfilms.co
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
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

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            posts = client.parseDOM(r, 'item')

            hostDict = hostprDict + hostDict

            items = []

            for post in posts:
                try:
                    t = client.parseDOM(post, 'title')[0]
                    u = client.parseDOM(post, 'link')[0]
                    s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', t)
                    s = s[0] if s else '0'

                    items += [(t, u, s) ]

                except:
                    pass

            urls = []
            for item in items:

                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if not y == hdlr: raise Exception()

                    quality, info = source_utils.get_release_quality(name, item[1])
                    if any(x in quality for x in ['CAM', 'SD']): continue

                    try:
                        size = re.sub('i', '', item[2])
                        div = 1 if size.endswith('GB') else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass

                    info = ' | '.join(info)

                    url = item[1]
                    links = self.links(url)
                    urls += [(i, quality, info) for i in links]

                except:
                    pass

            for item in urls:

                if 'earn-money' in item[0]: continue
                if any(x in item[0] for x in ['.rar', '.zip', '.iso']): continue
                url = client.replaceHTMLCodes(item[0])
                url = url.encode('utf-8')

                valid, host = source_utils.is_host_valid(url, hostDict)
                if not valid: continue
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')

                sources.append({'source': host, 'quality': item[1], 'language': 'en', 'url': url, 'info': item[2], 'direct': False, 'debridonly': True})

            return sources
        except:
            return sources

    def links(self, url):
        urls = []
        try:
            if url is None: return
            r = client.request(url)
            r = client.parseDOM(r, 'div', attrs={'class': 'entry'})
            r = client.parseDOM(r, 'a', ret='href')
            r1 = [(i) for i in r if 'money' in i][0]
            r = client.request(r1)
            r = client.parseDOM(r, 'div', attrs={'id': 'post-\d+'})[0]

            if 'enter the password' in r:
                plink= client.parseDOM(r, 'form', ret='action')[0]

                post = {'post_password': '300mbfilms', 'Submit': 'Submit'}
                send_post = client.request(plink, post=post, output='cookie')
                link = client.request(r1, cookie=send_post)
            else:
                link = client.request(r1)

            link = re.findall('<strong>Single(.+?)</tr', link, re.DOTALL)[0]
            link = client.parseDOM(link, 'a', ret='href')
            link = [(i.split('=')[-1]) for i in link]
            for i in link:
                urls.append(i)

            return urls
        except:
            pass

    def resolve(self, url):
        return url


