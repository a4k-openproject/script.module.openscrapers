# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 02-24-2019 by JewBMX in Scrubs.

import re,traceback,urllib,urlparse
from openscrapers.modules import cleantitle,client,proxy,source_utils,log_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['coolmoviezone.club']
		self.base_link = 'https://coolmoviezone.club'
# old coolmoviezone.info  coolmoviezone.online  coolmoviezone.biz


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			title = cleantitle.geturl(title)
			url = self.base_link + '/%s-%s' % (title,year)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []
			hostDict = hostprDict + hostDict
			r = client.request(url)
			match = re.compile('<td align="center"><strong><a href="(.+?)"').findall(r)
			for url in match: 
				host = url.split('//')[1].replace('www.','')
				host = host.split('/')[0].split('.')[0].title()
				quality = source_utils.check_sd_url(url)
				valid, host = source_utils.is_host_valid(url, hostDict)
				if valid:
				    sources.append({'source': host, 'quality': quality, 'language': 'en','url': url,'direct': False,'debridonly': False})
		except Exception:
			return
		return sources


	def resolve(self, url):
		return url

