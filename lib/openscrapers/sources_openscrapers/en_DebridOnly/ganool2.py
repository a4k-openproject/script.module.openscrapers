# -*- coding: utf-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# As long as you retain this notice you can do whatever you want with
# this stuff. If we meet some day, and you think this stuff is worth it,
# you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################


import re
import urllib
import urlparse

import requests
# from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['ganool.bz', 'ganool.ws', 'ganol.si', 'ganool123.com']
		self.base_link = 'https://123movie.nu'
		self.search_link = '/search/?q=%s'
		self.download_links = '/loadmoviedownloadsection.php'

	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception:
			return

	def sources(self, url, hostDict, hostprDict):
		sources = []

		hostDict = hostprDict + hostDict

		try:
			if url is None:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title']
			year = data['year']

			search = title.lower()

			url = urlparse.urljoin(self.base_link, self.search_link % (search.replace(' ', '+')))

			shell = requests.Session()

			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}
			Digital = shell.get(url, headers=headers).content

			BlackFlag = re.compile(
				'data-movie-id="" class="ml-item".+?href="(.+?)" class="ml-mask jt".+?<div class="moviename">(.+?)</div>',
				re.DOTALL).findall(Digital)

			for Digibox, Powder in BlackFlag:
				if title.lower() in Powder.lower():
					if year in str(Powder):
						r = shell.get(Digibox, headers=headers).content
						quals = re.compile('<strong>Quality:</strong>\s+<a href=.+?>(.+?)</a>', re.DOTALL).findall(r)

						for url in quals:
							quality = source_utils.check_url(url)

						key = re.compile("var randomKeyNo = '(.+?)'", re.DOTALL).findall(r)
						post_link = urlparse.urljoin(self.base_link, self.download_links)
						payload = {'key': key}
						post = shell.post(post_link, headers=headers, data=payload)
						response = post.content

						grab = re.compile('<a rel="\w+" href="(.+?)">\w{5}\s\w+\s\w+\s\w+\s\w{5}<\/a>',
						                  re.DOTALL).findall(response)

						for links in grab:
							r = shell.get(links, headers=headers).content
							links = re.compile('<a rel="\w+" href="(.+?)" target="\w+">', re.DOTALL).findall(r)

						for link in links:
							valid, host = source_utils.is_host_valid(link, hostDict)

							if 'rar' in link:
								continue

							sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link,
							                'direct': False, 'debridonly': False})

			return sources
		except Exception:
			return sources

	def resolve(self, url):
		return url
