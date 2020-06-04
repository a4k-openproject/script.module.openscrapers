# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 07-23-2019 by JewBMX in Scrubs.
# Has shows but is shitty and limited.

import re
import requests

from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 31
		self.language = ['en']
		self.domains = ['zmovies.me']
		self.base_link = 'https://zmovies.me'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0', 'Referer': self.base_link}
		self.session = requests.Session()


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			mtitle = cleantitle.geturl(title)
			url = self.base_link + '/watch-%s-%s-online-free-putlocker/' % (mtitle, year)
			return url
		except:
			source_utils.scraper_error('ZMOVIES')
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			if url is None:
				return sources
			hostDict = hostDict + hostprDict
			r = self.session.get(url, headers=self.headers).content
			match = re.compile('<IFRAME.+?SRC="(.+?)"', flags=re.DOTALL | re.IGNORECASE).findall(r)
			for url in match:
				url =  "https:" + url if not url.startswith('http') else url
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:
					quality, info = source_utils.get_release_quality(url, url)

					sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
			return sources
		except:
			source_utils.scraper_error('ZMOVIES')
			return sources


	def resolve(self, url):
		return url