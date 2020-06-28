# -*- coding: utf-8 -*-
"""
	OpenScrapers Module
"""

import base64
import gzip
import random
import re
import sys
import time

try:
	from HTMLParser import HTMLParser
except ImportError:
	from html.parser import HTMLParser
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO
try:
	import cookielib
except ImportError:
	import http.cookiejar as cookielib
try:
	from urllib2 import HTTPErrorProcessor, ProxyHandler, Request, build_opener, install_opener, HTTPSHandler, \
						HTTPCookieProcessor, HTTPHandler, urlopen
except ImportError:
	from urllib.request import HTTPErrorProcessor, ProxyHandler, Request, build_opener, install_opener, HTTPSHandler, \
						HTTPCookieProcessor, HTTPHandler, urlopen
try:
	from urllib2 import HTTPError
except ImportError:
	from urllib.error import HTTPError

try:
	from urlparse import parse_qs, urlparse, urljoin
except ImportError:
	from urllib.parse import parse_qs, urlparse, urljoin

try:
	from urllib import urlencode, quote_plus
except ImportError:
	from urllib.parse import urlencode, quote_plus

try:
    # Python 2 forward compatibility
    range = xrange
except NameError:
    pass

from openscrapers.modules import cache
from openscrapers.modules import dom_parser
from openscrapers.modules import log_utils
from openscrapers.modules import workers

def request(url, close=True, redirect=True, error=False, proxy=None, post=None, headers=None, mobile=False, XHR=False,
			limit=None, referer=None, cookie=None, compression=True, output='', timeout='30', ignoreSsl=False,
			flare=True, ignoreErrors=None):
	try:
		if url is None:
			return None

		handlers = []

		if proxy is not None:
			handlers += [ProxyHandler({'http': '%s' % (proxy)}), HTTPHandler]
			opener = build_opener(*handlers)
			opener = install_opener(opener)

		if output == 'cookie' or output == 'extended' or not close is True:
			cookies = cookielib.LWPCookieJar()
			handlers += [HTTPHandler(), HTTPSHandler(), HTTPCookieProcessor(cookies)]
			opener = build_opener(*handlers)
			opener = install_opener(opener)

		if ignoreSsl or ((2, 7, 8) < sys.version_info < (2, 7, 12)):
			try:
				import ssl
				ssl_context = ssl.create_default_context()
				ssl_context.check_hostname = False
				ssl_context.verify_mode = ssl.CERT_NONE
				handlers += [HTTPSHandler(context=ssl_context)]
				opener = build_opener(*handlers)
				opener = install_opener(opener)
			except:
				pass

		if url.startswith('//'):
			url = 'http:' + url

		try:
			headers.update(headers)
		except:
			headers = {}

		if 'User-Agent' in headers:
			pass
		elif mobile is not True:
			# headers['User-Agent'] = agent()
			headers['User-Agent'] = cache.get(randomagent, 1)
		else:
			headers['User-Agent'] = 'Apple-iPhone/701.341'

		if 'Referer' in headers:
			pass
		elif referer is not None:
			headers['Referer'] = referer

		if 'Accept-Language' not in headers:
			headers['Accept-Language'] = 'en-US'

		if 'X-Requested-With' in headers:
			pass
		elif XHR is True:
			headers['X-Requested-With'] = 'XMLHttpRequest'

		if 'Cookie' in headers:
			pass
		elif cookie is not None:
			headers['Cookie'] = cookie

		if 'Accept-Encoding' in headers:
			pass
		elif compression and limit is None:
			headers['Accept-Encoding'] = 'gzip'

		if redirect is False:
			class NoRedirection(HTTPErrorProcessor):
				def http_response(self, request, response):
					return response

			opener = build_opener(NoRedirection)
			opener = install_opener(opener)

			try:
				del headers['Referer']
			except:
				pass

		if isinstance(post, dict):
			# Gets rid of the error: 'ascii' codec can't decode byte 0xd0 in position 0: ordinal not in range(128)
			try: iter_items = post.iteritems()
			except: iter_items = post.items()
			for key, value in iter_items:
				try:
					post[key] = value.encode('utf-8')
				except:
					pass

			post = urlencode(post)

		request = Request(url, data=post)
		_add_request_header(request, headers)

		try:
			response = urlopen(request, timeout=int(timeout))
		except HTTPError as response:
			try:
				ignore = ignoreErrors and (int(response.code) == ignoreErrors or int(response.code) in ignoreErrors)
			except:
				ignore = False

			if not ignore:
				if response.code in [301, 307, 308, 503]:
					cf_result = response.read(5242880)
					try:
						encoding = response.info().getheader('Content-Encoding')
					except:
						encoding = None

					if encoding == 'gzip':
						cf_result = gzip.GzipFile(fileobj=StringIO(cf_result)).read()

					if flare and 'cloudflare' in str(response.info()).lower():
						log_utils.log('client module calling cfscrape: url=%s' % url, log_utils.LOGDEBUG)
						try:
							from openscrapers.modules import cfscrape
							if isinstance(post, dict):
								data = post
							else:
								try:
									data = parse_qs(post)
								except:
									data = None

							scraper = cfscrape.CloudScraper()
							response = scraper.request(method='GET' if post is None else 'POST', url=url,
													   headers=headers, data=data, timeout=int(timeout))
							result = response.content
							flare = 'cloudflare'  # Used below
							try:
								cookies = response.request._cookies
							except:
								log_utils.error()

						except:
							log_utils.error()

					elif 'cf-browser-verification' in cf_result:
						netloc = '%s://%s' % (urlparse(url).scheme, urlparse(url).netloc)
						ua = headers['User-Agent']
						cf = cache.get(cfcookie().get, 168, netloc, ua, timeout)
						headers['Cookie'] = cf
						request = Request(url, data=post)
						_add_request_header(request, headers)
						response = urlopen(request, timeout=int(timeout))
					else:
						log_utils.log('Request-Error (%s): %s' % (str(response.code), url), log_utils.LOGDEBUG)
						if error is False:
							return
				else:
					log_utils.log('Request-Error (%s): %s' % (str(response.code), url), log_utils.LOGDEBUG)
					if error is False:
						return

		if output == 'cookie':
			try:
				result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except:
				pass
			try:
				result = cf
			except:
				pass
			if close is True:
				response.close()
			return result

		elif output == 'geturl':
			result = response.geturl()
			if close is True:
				response.close()
			return result

		elif output == 'headers':
			result = response.headers
			if close is True:
				response.close()
			return result

		elif output == 'chunk':
			try:
				content = int(response.headers['Content-Length'])
			except:
				content = (2049 * 1024)
			if content < (2048 * 1024):
				return
			result = response.read(16 * 1024)
			if close is True:
				response.close()
			return result

		elif output == 'file_size':
			try:
				content = int(response.headers['Content-Length'])
			except:
				content = '0'
			response.close()
			return content

		if flare != 'cloudflare':
			if limit == '0':
				result = response.read(224 * 1024)
			elif limit is not None:
				result = response.read(int(limit) * 1024)
			else:
				result = response.read(5242880)

		try:
			encoding = response.info().getheader('Content-Encoding')
		except:
			encoding = None

		if encoding == 'gzip':
			result = gzip.GzipFile(fileobj=StringIO(result)).read()

		if 'sucuri_cloudproxy_js' in result:
			su = sucuri().get(result)

			headers['Cookie'] = su

			request = Request(url, data=post)
			_add_request_header(request, headers)

			response = urlopen(request, timeout=int(timeout))

			if limit == '0':
				result = response.read(224 * 1024)
			elif limit is not None:
				result = response.read(int(limit) * 1024)
			else:
				result = response.read(5242880)

			try:
				encoding = response.info().getheader('Content-Encoding')
			except:
				encoding = None
			if encoding == 'gzip':
				result = gzip.GzipFile(fileobj=StringIO(result)).read()

		if 'Blazingfast.io' in result and 'xhr.open' in result:
			netloc = '%s://%s' % (urlparse(url).scheme, urlparse(url).netloc)
			ua = headers['User-Agent']
			headers['Cookie'] = cache.get(bfcookie().get, 168, netloc, ua, timeout)
			result = _basic_request(url, headers=headers, post=post, timeout=timeout, limit=limit)

		if output == 'extended':
			try:
				response_headers = dict([(item[0].title(), item[1]) for item in response.info().items()])
			except:
				response_headers = response.headers

			try:
				response_code = str(response.code)
			except:
				response_code = str(response.status_code)  # object from CFScrape Requests object.

			try:
				cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
			except:
				pass

			try:
				cookie = cf
			except:
				pass

			if close is True:
				response.close()
			return (result, response_code, response_headers, headers, cookie)
		else:
			if close is True:
				response.close()
			return result

	except Exception as e:
		log_utils.log('Request-Error: (%s) => %s' % (str(e), url), log_utils.LOGDEBUG)
		return


def _basic_request(url, headers=None, post=None, timeout='30', limit=None):
	try:
		try:
			headers.update(headers)
		except:
			headers = {}
		request = Request(url, data=post)
		_add_request_header(request, headers)
		response = urlopen(request, timeout=int(timeout))
		return _get_result(response, limit)
	except:
		log_utils.error()
		return


def _add_request_header(_request, headers):
	try:
		if not headers:
			headers = {}
		try:
			scheme = _request.get_type()
		except:
			scheme = 'http'

		# Gaia removed trailing forward slash...why?  seems to break scrapers like cartoonhd
		# referer = headers.get('Referer') if 'Referer' in headers else '%s://%s' % (scheme, _request.get_host())
		referer = headers.get('Referer') if 'Referer' in headers else '%s://%s/' % (scheme, _request.get_host())

		_request.add_unredirected_header('Host', _request.get_host())
		_request.add_unredirected_header('Referer', referer)

		for key in headers:
			_request.add_header(key, headers[key])
	except:
		log_utils.error()
		return


def _get_result(response, limit=None):
	if limit == '0':
		result = response.read(224 * 1024)
	elif limit:
		result = response.read(int(limit) * 1024)
	else:
		result = response.read(5242880)

	try:
		encoding = response.info().getheader('Content-Encoding')
	except:
		encoding = None
	if encoding == 'gzip':
		result = gzip.GzipFile(fileobj=StringIO(result)).read()

	return result


def parseDOM(html, name='', attrs=None, ret=False):
	if attrs:
		try:
			attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.iteritems())
		except:
			attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.items())
	results = dom_parser.parse_dom(html, name, attrs, ret)

	if ret:
		results = [result.attrs[ret.lower()] for result in results]
	else:
		results = [result.content for result in results]
	return results


def replaceHTMLCodes(txt):
	# Some HTML entities are encoded twice. Decode double.
	return _replaceHTMLCodes(_replaceHTMLCodes(txt))


def _replaceHTMLCodes(txt):
	txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
	txt = HTMLParser().unescape(txt)
	txt = txt.replace("&quot;", "\"")
	txt = txt.replace("&amp;", "&")
	txt = txt.strip()
	return txt


def randomagent():
	BR_VERS = [
		['%s.0' % i for i in range(18, 50)],
		['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111',
		 '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111', '40.0.2214.115',
		 '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155',
		 '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71', '46.0.2490.80', '46.0.2490.86',
		 '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86', '51.0.2704.103',
		 '52.0.2743.116', '53.0.2785.143', '54.0.2840.71', '61.0.3163.100', '63.0.3239.132', '78.0.3904.108'],
		['11.0'],
		['8.0', '9.0', '10.0', '10.6']]
	WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1',
				'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
	FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
	RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
				'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
				'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
				'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
	index = random.randrange(len(RAND_UAS))
	return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES),
								  br_ver=random.choice(BR_VERS[index]))


def agent():
	return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'


class cfcookie:
	def __init__(self):
		self.cookie = None

	def get(self, netloc, ua, timeout):
		threads = []

		for i in list(range(0, 15)):
			threads.append(workers.Thread(self.get_cookie, netloc, ua, timeout))
		[i.start() for i in threads]

		for i in list(range(0, 30)):
			if self.cookie is not None:
				return self.cookie
			time.sleep(1)

	def get_cookie(self, netloc, ua, timeout):
		try:
			headers = {'User-Agent': ua}
			request = Request(netloc)
			_add_request_header(request, headers)

			try:
				response = urlopen(request, timeout=int(timeout))
			except HTTPError as response:
				result = response.read(5242880)
				try:
					encoding = response.info().getheader('Content-Encoding')
				except:
					encoding = None
				if encoding == 'gzip':
					result = gzip.GzipFile(fileobj=StringIO(result)).read()

			jschl = re.findall('name="jschl_vc" value="(.+?)"/>', result)[0]
			init = re.findall('setTimeout\(function\(\){\s*.*?.*:(.*?)};', result)[-1]
			builder = re.findall(r"challenge-form\'\);\s*(.*)a.v", result)[0]
			decryptVal = self.parseJSString(init)
			lines = builder.split(';')

			for line in lines:
				if len(line) > 0 and '=' in line:
					sections = line.split('=')
					line_val = self.parseJSString(sections[1])
					decryptVal = int(eval(str(decryptVal) + sections[0][-1] + str(line_val)))

			answer = decryptVal + len(urlparse(netloc).netloc)

			query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

			if 'type="hidden" name="pass"' in result:
				passval = re.findall('name="pass" value="(.*?)"', result)[0]
				query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (
					netloc, quote_plus(passval), jschl, answer)
				time.sleep(6)

			cookies = cookielib.LWPCookieJar()
			handlers = [HTTPHandler(), HTTPSHandler(), HTTPCookieProcessor(cookies)]
			opener = build_opener(*handlers)
			opener = install_opener(opener)

			try:
				request = Request(query)
				_add_request_header(request, headers)
				response = urlopen(request, timeout=int(timeout))
			except:
				pass

			cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])

			if 'cf_clearance' in cookie:
				self.cookie = cookie
		except:
			pass

	def parseJSString(self, s):
		try:
			offset = 1 if s[0] == '+' else 0
			val = int(
				eval(s.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
			return val
		except:
			pass


class bfcookie:
	def __init__(self):
		self.COOKIE_NAME = 'BLAZINGFAST-WEB-PROTECT'

	def get(self, netloc, ua, timeout):
		try:
			headers = {'User-Agent': ua, 'Referer': netloc}
			result = _basic_request(netloc, headers=headers, timeout=timeout)

			match = re.findall('xhr\.open\("GET","([^,]+),', result)
			if not match:
				return False

			url_Parts = match[0].split('"')
			url_Parts[1] = '1680'
			url = urljoin(netloc, ''.join(url_Parts))

			match = re.findall('rid=([0-9a-zA-Z]+)', url_Parts[0])
			if not match:
				return False

			headers['Cookie'] = 'rcksid=%s' % match[0]
			result = _basic_request(url, headers=headers, timeout=timeout)
			return self.getCookieString(result, headers['Cookie'])
		except:
			return

	# not very robust but lazieness...
	def getCookieString(self, content, rcksid):
		vars = re.findall('toNumbers\("([^"]+)"', content)
		value = self._decrypt(vars[2], vars[0], vars[1])
		cookie = "%s=%s;%s" % (self.COOKIE_NAME, value, rcksid)
		return cookie

	def _decrypt(self, msg, key, iv):
		from binascii import unhexlify, hexlify
		import pyaes

		msg = unhexlify(msg)
		key = unhexlify(key)
		iv = unhexlify(iv)

		if len(iv) != 16:
			return False

		decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
		plain_text = decrypter.feed(msg)
		plain_text += decrypter.feed()
		f = hexlify(plain_text)
		return f


class sucuri:
	def __init__(self):
		self.cookie = None

	def get(self, result):
		try:
			s = re.compile("S\s*=\s*'([^']+)").findall(result)[0]
			s = base64.b64decode(s)
			s = s.replace(' ', '')
			s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
			s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
			s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
			s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
			s = re.sub(';location.reload\(\);', '', s)
			s = re.sub(r'\n', '', s)
			s = re.sub(r'document\.cookie', 'cookie', s)

			cookie = '';
			exec (s)
			self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
			self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])

			return self.cookie
		except:
			pass