# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import traceback
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import control
from openscrapers.modules import jsunpack
from openscrapers.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['streamlord.com']
        self.base_link = 'http://www.streamlord.com'
        self.search_link = '/searchtest.php'
        self.user = control.setting('streamlord.user')
        self.password = control.setting('streamlord.pass')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('StreamLord - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('StreamLord - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('StreamLord - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if (self.user != '' and self.password != ''):  # raise Exception()

                login = urlparse.urljoin(self.base_link, '/login.html')

                post = urllib.urlencode({'username': self.user, 'password': self.password, 'submit': 'Login'})

                cookie = client.request(login, post=post, output='cookie', close=False)

                r = client.request(login, post=post, cookie=cookie, output='extended')

                headers = {'User-Agent': r[3]['User-Agent'], 'Cookie': r[4]}
            else:
                headers = {}

            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

                year = data['year']

                query = urlparse.urljoin(self.base_link, self.search_link)

                post = urllib.urlencode({'searchapi2': title})

                r = client.request(query, post=post, headers=headers)

                if 'tvshowtitle' in data:
                    r = re.findall('(watch-tvshow-.+?-\d+\.html)', r)
                    r = [(i, re.findall('watch-tvshow-(.+?)-\d+\.html', i)) for i in r]
                else:
                    r = re.findall('(watch-movie-.+?-\d+\.html)', r)
                    r = [(i, re.findall('watch-movie-(.+?)-\d+\.html', i)) for i in r]

                r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
                r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1])]
                r = [i[0] for i in r][0]

                u = urlparse.urljoin(self.base_link, r)
                for i in range(3):
                    r = client.request(u, headers=headers)
                    if not 'failed' in r: break

                if 'season' in data and 'episode' in data:
                    r = re.findall('(episode-.+?-.+?\d+.+?\d+-\d+.html)', r)
                    r = [i for i in r if '-s%02de%02d-' % (int(data['season']), int(data['episode'])) in i.lower()][0]

                    r = urlparse.urljoin(self.base_link, r)

                    r = client.request(r, headers=headers)

            else:
                r = urlparse.urljoin(self.base_link, url)

                r = client.request(r, post=post, headers=headers)

            quality = 'HD' if '-movie-' in r else 'SD'

            try:
                f = re.findall('''["']sources['"]\s*:\s*\[(.*?)\]''', r)[0]
                f = re.findall('''['"]*file['"]*\s*:\s*([^\(]+)''', f)[0]

                u = re.findall('function\s+%s[^{]+{\s*([^}]+)' % f, r)[0]
                u = re.findall('\[([^\]]+)[^+]+\+\s*([^.]+).*?getElementById\("([^"]+)', u)[0]

                a = re.findall('var\s+%s\s*=\s*\[([^\]]+)' % u[1], r)[0]
                b = client.parseDOM(r, 'span', {'id': u[2]})[0]

                url = u[0] + a + b
                url = url.replace('"', '').replace(',', '').replace('\/', '/')
                url += '|' + urllib.urlencode(headers)
            except:
                try:
                    url = r = jsunpack.unpack(r)
                    url = url.replace('"', '')
                except:
                    url = re.findall(
                        r'sources[\'"]\s*:\s*\[.*?file[\'"]\s*:\s*(\w+)\(\).*function\s+\1\(\)\s*\{\s*return\([\'"]([^\'"]+)',
                        r, re.DOTALL)[0][1]

            sources.append(
                {'source': 'cdn', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False,
                 'autoplay': True})

            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('StreamLord - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url
