# -*- coding: utf-8 -*-
# modified by Venom for Openscrapers (updated 6-27-2020)

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, quote_plus
except ImportError: from urllib.parse import urlencode, quote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 22
		self.language = ['en']
		self.domains = ['mvl.688.org', 'dls.myvideolinks.net', 'get.myvideolinks.net', 'go.myvideolinks.net', 'myvideolinks.69.mu',
								'sag.myvideolinks.net', 'looka.myvideolinks.net', 'kita.myvideolinks.net']
		self.base_link = 'http://mvl.688.org'
		self.search_link = '/?s=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urlencode(url)
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url is None:
				return
			url = parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
			url = urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		sources = []
		try:
			# test = client.request(self.base_link)
			# search form seems down for now with new url
			# new_search = client.parseDOM(test, 'form', ret='action')[0] # to try to combat their constant search link changes

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

			hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = urljoin(self.base_link, self.search_link)
			# url = urljoin(new_search, self.search_link)
			url = url % quote_plus(query)
			# log_utils.log('url = %s' % url, __name__, log_utils.LOGDEBUG)
			r = client.request(url, timeout='5')
			if not r:
				return sources
			if 'Nothing Found' in r:
				return sources

			r = client.parseDOM(r, 'article')
			r1 = client.parseDOM(r, 'h2')
			# r2 = client.parseDOM(r, 'div', attrs={'class': 'entry-excerpt'})

			if 'tvshowtitle' in data: # fuckers removed file size for episodes
				posts = zip(client.parseDOM(r1, 'a', ret='href'), client.parseDOM(r1, 'a')) # keep for now case they bring size back
			else:
				posts = zip(client.parseDOM(r1, 'a', ret='href'), client.parseDOM(r1, 'a'))

			hostDict = hostprDict + hostDict
			items = []
			for post in posts:
				try:
					base_u = client.request(post[0], timeout='5')
					if 'tvshowtitle' in data:
						regex = '<h4>(' + title + '.+?)</h4>'
						lists = zip(re.findall(regex, base_u), re.findall('<ul>(.+?)</ul>', base_u, re.DOTALL))
						for links in lists:
							u = re.findall('\'(http.+?)\'', links[1]) + re.findall('\"(http.+?)\"', links[1])
							t = links[0].replace('HDTV', '')
							s = 0
							items += [(t, i, s) for i in u]
					else:
						byline = client.parseDOM(base_u, 'div', attrs={'class': 'entry-byline cf'})
						if 'TV SHOWS' in str(byline):
							continue
						list = client.parseDOM(base_u, 'div', attrs={'class': 'entry-content cf'})
						u = client.parseDOM(list, 'ul')[0]
						u = re.findall('\'(http.+?)\'', u) + re.findall('\"(http.+?)\"', u)
						u = [i for i in u if '/embed/' not in i]
						u = [i for i in u if 'youtube' not in i]
						try:
							t = post[1].encode('utf-8')
						except:
							t = post[1]
						s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', list[0])[0]
						items += [(t, i, s) for i in u]
				except:
					source_utils.scraper_error('MYVIDEOLINK')
					pass

			for item in items:
				try:
					url = item[1]
					url = client.replaceHTMLCodes(url)
					try:
						url = url.encode('utf-8')
					except:
						pass
					if url.endswith(('.rar', '.zip', '.iso', '.part', '.png', '.jpg', '.bmp', '.gif')):
						continue

					valid, host = source_utils.is_host_valid(url, hostDict)
					if not valid:
						continue

					host = client.replaceHTMLCodes(host)
					try:
						host = host.encode('utf-8')
					except:
						pass

					name = item[0]
					name = client.replaceHTMLCodes(name).replace(' ', '.')
					if not source_utils.check_title(title.replace('!', ''), name, hdlr, data['year']):
						continue

					quality, info = source_utils.get_release_quality(name, url)

					try:
						size = item[2]
						dsize, isize = source_utils._size(size)
						if isize:
							info.insert(0, isize)
					except:
						dsize = 0
						pass

					fileType = source_utils.getFileType(name)
					info.append(fileType)
					info = ' | '.join(info) if fileType else info[0]

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
				except:
					source_utils.scraper_error('MYVIDEOLINK')
					pass
			return sources
		except:
			source_utils.scraper_error('MYVIDEOLINK')
			return sources


	def resolve(self, url):
		return url