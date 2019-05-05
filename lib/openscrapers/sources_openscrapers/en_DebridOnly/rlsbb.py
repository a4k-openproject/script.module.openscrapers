# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
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
'''

import ast
import json
import operator as op
import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


def parseJSString(s):
    result = ''
    for x in s:
        if '(' in x:
            if '((' in x:
                result += parseJSString(re.findall(r'.(\(.*?\))', x))
                continue
            offset = 1 if s[0] == '+' else 0
            val = x.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0')[offset:]
            val = val.strip('(').strip(')')
            val = val.replace('(+0', '(0').replace('(+1', '(1')
            result += str(eval_expr(val.strip(' ')))
        else:
            result += x.strip('\'')
    return result


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rlsbb.ru']
        self.base_link = 'http://rlsbb.ru'
        self.searchbase_link = 'http://search.rlsbb.ru'
        self.search_cookie = 'serach_mode=rlsbb'
        self.search_link = '/lib/search%s?phrase=%s&pindex=1&code=%s&rand=0.7736787998237127'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': cleantitle.getsearch(title), 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': cleantitle.getsearch(tvshowtitle), 'year': year}
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
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            if debrid.status() is False:
                raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = (data['tvshowtitle'] if 'tvshowtitle' in data else data['title'])
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'], int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s' % (
                data['title'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            query = query.replace("&", "and")
            query = query.replace("  ", " ")
            query = query.replace(" ", "-")

            query = urllib.quote_plus(query)
            url = '%s/?s=%s&submit=Find' % (self.base_link, query)

            resp = self.scraper.get(url)

            capture = re.findall(r'<script id="rlsbb_script" data-code-rlsbb="(\d*)" .*? src="(.*?)"><', resp.text)[0]
            rlsbb_code = capture[0]
            script_url = capture[1]

            resp = self.scraper.get(script_url)
            location_code = re.findall(r'\'/lib/search\' (.*?);', resp.text)[0]

            location_maths = re.findall(r'( \(.*?\) )| (\'.*?\') |\+ (\d*) \+|(\'\d*.php\')', location_code)

            location_maths = [x for i in location_maths for x in i if str(x) != '']

            location_builder = parseJSString(location_maths)

            url = '%s%s' % (self.searchbase_link, self.search_link % (location_builder, query, rlsbb_code))

            r = self.scraper.get(url).content

            try:
                results = json.loads(r)['results']
            except:
                return None

            if 'tvshowtitle' in data:
                regex = r'.*?(%s) .*?(s%se%s)' % (data['tvshowtitle'].lower(),
                                                  str(data['season']).zfill(2),
                                                  str(data['episode']).zfill(2))
            else:
                regex = r'.*?(%s) .*?(%s)' % (data['title'], data['year'])

            post_urls = []

            for post in results:

                if 'old' in post['domain']:
                    continue
                capture = re.findall(regex, post['post_title'].lower())
                capture = [i for i in capture if len(i) > 1]
                if len(capture) >= 1:
                    post_urls.append('http://%s/%s' % (post['domain'], post['post_name']))

            if len(post_urls) == 0:
                return None

            items = []
            for url in post_urls:
                r = self.scraper.get(url).content
                posts = client.parseDOM(r, "div", attrs={"class": "content"})
                hostDict = hostprDict + hostDict
                for post in posts:
                    try:
                        u = client.parseDOM(post, 'a', ret='href')
                        for i in u:
                            try:
                                if hdlr in i.upper() and cleantitle.get(title) in cleantitle.get(i):
                                    items.append(i)
                            except:
                                pass
                    except:
                        pass

            seen_urls = set()

            for item in items:
                try:
                    url = str(item)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    host = url.replace("\\", "")
                    host2 = host.strip('"')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host2.strip().lower()).netloc)[0]

                    if host not in hostDict:
                        continue

                    if any(x in host2 for x in ['.rar', '.zip', '.iso']):
                        continue

                    quality, info = source_utils.get_release_quality(url)

                    info = ' | '.join(info)
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': host2, 'info': info,
                                    'direct': False, 'debridonly': False})

                except:
                    pass
            check = [i for i in sources if not i['quality'] == 'CAM']
            if check:
                sources = check
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
