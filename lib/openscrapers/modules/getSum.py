# -*- coding: utf-8 -*-
# --[getSum v1.4]--|--[From JewBMX]--
# Lazy Module to make life a little easier.

import re
try:
	from HTMLParser import HTMLParser
except ImportError:
	from html.parser import HTMLParser

from openscrapers.modules.utils import byteify
from openscrapers.modules import log_utils

headers = {
	'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3555.0 Safari/537.36"}


class GetSum(object):
	_frame_regex = r'(?:iframe|source).+?(?:src)=(?:\"|\')(.+?)(?:\"|\')'
	_datavideo_regex = r'(?:data-video|data-src|data-href)=(?:\"|\')(.+?)(?:\"|\')'
	_filesource_regex = r'(?:file|source)(?:\:)\s*(?:\"|\')(.+?)(?:\"|\')'
	_magnet_regex = r'''(magnet:\?[^"']+)'''
	_timeout = 10

	def findSum(self, text, type=None):
		try:
			self.links = set()
			if not text:
				return
			if re.search(self._frame_regex, text, re.IGNORECASE) or type == 'iframe':
				links = re.compile(self._frame_regex).findall(text)
				if links:
					for link in links:
						link = "https:" + link if not link.startswith('http') else link
						if link in self.links:
							continue
						self.links.add(link)
			if re.search(self._datavideo_regex, text, re.IGNORECASE) or type == 'datavideo':
				links = re.compile(self._datavideo_regex).findall(text)
				if links:
					for link in links:
						link = "https:" + link if not link.startswith('http') else link
						if link in self.links:
							continue
						self.links.add(link)
			if re.search(self._filesource_regex, text, re.IGNORECASE) or type == 'filesource':
				links = re.compile(self._filesource_regex).findall(text)
				if links:
					for link in links:
						link = "https:" + link if not link.startswith('http') else link
						if link in self.links:
							continue
						self.links.add(link)
			if re.search(self._magnet_regex, text, re.IGNORECASE) or type == 'magnet':
				links = re.compile(self._magnet_regex).findall(text)
				if links:
					for link in links:
						link = str(byteify(replaceHTMLCodes(link)).split('&tr')[0])
						link = "magnet:" + link if not link.startswith('magnet') else link
						if link in self.links:
							continue
						self.links.add(link)
			return self.links
		except Exception:
			return self.links


########################################################
########################################################


def logSum(matches):
	number = 0
	for match in matches:
		log_utils.log('getSum - logSum:  %d  -  %s' % (number, match))
		number = number + 1


# Normal = getSum.get(url)
# CFscrape = getSum.get(url, Type='cfscrape')
def get(url, Type=None):
	if not url:
		return
	if Type == 'client' or Type is None:
		from openscrapers.modules import client
		content = client.request(url, headers=headers)
	if Type == 'cfscrape':
		from openscrapers.modules import cfscrape
		cfscraper = cfscrape.create_scraper()
		content = cfscraper.get(url, headers=headers).content
	if Type == 'redirect':
		import requests
		content = requests.get(url, headers=headers).url
	if content is None:
		log_utils.log('getSum - Get ERROR:  No Content Got for:  ' + str(url))
		raise Exception()
	return content


# results = getSum.findSum(text)
# for result in results:
def findSum(text, type=None, timeout=10):
	if not text:
		return
	getSum = GetSum()
	results = getSum.findSum(text, type=type)
	if results:
		return results
	else:
		return []


# results = getSum.findEm(text, '(?:iframe|source).+?(?:src)=(?:\"|\')(.+?)(?:\"|\')')
# for result in results:
def findEm(text, regex):
	results = re.findall(regex, text, flags=re.DOTALL | re.IGNORECASE)
	if results:
		return results
	else:
		return []


# results = getSum.findThat(text, 'hhhhh')
# for result in results:
def findThat(text, regex):
	p_reg = re.compile(regex, flags=re.DOTALL | re.IGNORECASE)
	results = p_reg.findall(text)
	if results:
		return results
	else:
		return []


def find_match(regex, text, index=0):
	results = re.findall(text, regex, flags=re.DOTALL | re.IGNORECASE)
	return results[index]


def findall(text, regex):
	p_reg = re.compile(regex, re.DOTALL + re.MULTILINE + re.UNICODE)
	result = p_reg.findall(text)
	return result


def findallIgnoreCase(text, regex):
	p_reg = re.compile(regex, re.DOTALL + re.MULTILINE + re.UNICODE + re.IGNORECASE)
	result = p_reg.findall(text)
	return result


def regex_get_all(text, start_with, end_with):
	r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
	return r


def get_sources(text):
	sources = re.compile('sources\s*:\s*\[(.+?)\]').findall(text)
	return sources


def get_sources_content(text):
	sources = re.compile('\{(.+?)\}').findall(text)
	return sources


def get_files(text):
	files = re.compile('''['"]?file['"]?\s*:\s*['"]([^'"]*)''').findall(text)
	return files


def get_files2(text):
	match = re.findall('''['"]file['"]\s*:\s*['"]([^'"]+)''', text)
	return match


def get_video(text):
	pattern = 'file(?:\'|\")?\s*(?:\:)\s*(?:\"|\')(.+?)(?:\"|\')'
	match = re.compile(pattern).findall(text)
	links = []
	for url in match:
		links.append(byteify(url))
	return links


def replaceHTMLCodes(text):
	text = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", text)
	text = HTMLParser().unescape(text)
	text = text.replace("&quot;", "\"")
	text = text.replace("&amp;", "&")
	text = text.replace("%2B", "+")
	text = text.replace("\/", "/")
	text = text.replace("\\", "")
	text = text.strip()
	return text


def unpacked(url):
	try:
		from openscrapers.modules import client
		from openscrapers.modules import jsunpack
		from openscrapers.modules import log_utils
		unpacked = ''
		html = client.request(url)
		if jsunpack.detect(html):
			unpacked = jsunpack.unpack(html)
			# log_utils.log('WatchWrestling - unpacked: \n' + str(unpacked))
		else:
			log_utils.log('getSum - unpacked - Failed.')
		return unpacked
	except:
		return


def TEST_RUN():
	from openscrapers.modules import jsunpack
	from openscrapers.modules import log_utils
	log_utils.log('#####################################')
	url = 'https://site.com'
	data = get(url, Type='cfscrape')
	packed = find_match(data, "text/javascript'>(eval.*?)\s*</script>")
	unpacked = jsunpack.unpack(packed)
	log_utils.log('---getSum TEST_RUN - unpacked: \n' + str(unpacked))
	log_utils.log('#####################################')
	return unpacked
