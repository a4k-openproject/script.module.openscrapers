# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    watchseries scraper for Exodus forks.
    Nov 9 2018 - Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re,urllib,urlparse,json,base64, random

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser
from openscrapers.modules import debrid
from openscrapers.modules import log_utils

# Working: https://seriesfree.to/episode/dawsons_creek_s6_e23.html

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['watchseriesfree.to','seriesfree.to']
		self.base_link = 'https://seriesfree.to/'
		self.search_link = 'https://seriesfree.to/search/%s'
		self.max_conns = 10 #set to 10 bc that = how many the prev scraper might hit
		self.min_srcs = 3

	def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
		try:
			query = self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle))

			# req page 3 times to workaround their BS random 404's
			# responses (legit & BS 404s) are actually very fast: timeout prob not important
			for i in range(4):
				result = client.request(query, timeout=3)
				if not result == None: break
			

			t = [tvshowtitle] + source_utils.aliases_to_array(aliases)
			t = [cleantitle.get(i) for i in set(t) if i]
			result = re.compile('itemprop="url"\s+href="([^"]+).*?itemprop="name"\s+class="serie-title">([^<]+)', re.DOTALL).findall(result)
			for i in result:
				if cleantitle.get(cleantitle.normalize(i[1])) in t and year in i[1]: url = i[0]

			url = url.encode('utf-8')
			
			#log_utils.log('\n\n~~~ outgoing tvshow() url')
			#log_utils.log(url)
			
			# returned 'url' format like: /serie/x_files 
			return url
		except:
			return


	def episode(self, url, imdb, tvdb, title, premiered, season, episode):
		try:
			if url == None: return
			#log_utils.log('\n\n~~~ incomingish episode() url')
			#log_utils.log(url)

			url = urlparse.urljoin(self.base_link, url)
			#log_utils.log('\n\n~~~ baselink-joined url')
			#log_utils.log(url)
			
			
			# req page 3 times to workaround their BS random 404's
			# responses (legit & BS both) are actually very fast: timeout not that important
			for i in range(4):
				result = client.request(url, timeout=3)
				if not result == None: break
			
				

			# grab all 'a' that are staged with ep-links formating
			items = dom_parser.parse_dom(result, 'a', attrs={'itemprop':'url'})
			#
			## <a itemprop="url" href="/episode/the_middle_s9_e16.html" title="Watch The Middle Season 9 Episode 16 Online For Free">
			##  <span class="sinfo fl-l">
			##   <span><span>9</span>
			##   </span>×<span itemprop="episodeNumber">16</span>
			##  </span>
			##  <em class="date fl-r" itemprop="datePublished">2018-03-13</em>
			##  <span class="txt-ell" title="Watch The Middle Season 9 Episode 16 Online For Free">
			##   <span class="W title txt-ell ">
			##    <span><span>The Middle</span></span>
			##    <em> - <span itemprop="name">The Crying Game</span></em>
			##   </span>
			##  </span></a>
			#
			
			
			# firstly, try to match YYYY-MM-DD listed in ep listing
			#  (this should (?) be more reliable than season/ep)
			try:	
				#log_utils.log('\n\n~~~ Attempting: find ep by air-date')
				
				# iterate through all 'a', from 'items' above...
				# grab all links that contain matching season/ep...
				# assign the first one's href to url
				url = [i.attrs['href'] for i in items if bool(re.compile('"datePublished">%s' % premiered).search(i.content))][0]
			except:
				url = None
				pass  
			
			
			# if no url match by date, continue to try by season/ep#
			if url == None:
				#log_utils.log('\n\n~~~ Attempting: (url==None) match by season/ep')
			
				# iterate through all 'a', from 'items' above...
				# grab all links that contain matching season/ep...
				# assign the first one's href to url
				url = [i.attrs['href'] for i in items if bool(re.compile('<span\s*>%s<.*?itemprop="episodeNumber">%s<\/span>' % (season,episode)).search(i.content))][0]
			
			
			url = url.encode('utf-8')
			#log_utils.log('\n\n~~~ outgoing episode() url')
			#log_utils.log(url)
			
			# returned 'url' format like: /episode/x_files_s4_e1.html
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
	
		#log_utils.log('\n\n~~~ incoming sources() url')
		#log_utils.log(url)
	
		try:
			sources = []
			if url == None: return sources

			req = urlparse.urljoin(self.base_link, url)
			
			# three attempts to pull up the episode-page, then bail
			for i in range(4):
				result = client.request(req, timeout=3)
				if not result == None: break
				
				
			# get the key div's contents
			# then get all the links along with preceding text hinting at host
			# ep pages sort links by hoster which is bad if the top hosters
			#	are unavailable for debrid OR if they're ONLY avail for debrid
			#	(for non-debrid peeps) so shuffle the list
			dom = dom_parser.parse_dom(result, 'div', attrs={'class':'links', 'id': 'noSubs'})
			result = dom[0].content		
			links = re.compile('<i class="fa fa-youtube link-logo"></i>([^<]+).*?href="([^"]+)"\s+class="watch',re.DOTALL).findall(result)
			random.shuffle(links)
			
			
			# Here we stack the deck for debrid users by copying
			#  all debrid hosts to the top of the list
			# This is ugly but it works. Someone else please make it cleaner?
			if debrid.status() == True:
				debrid_links = []
				for pair in links:
					for r in debrid.debrid_resolvers:
						if r.valid_url('', pair[0].strip()): debrid_links.append(pair)
				links = debrid_links + links


			# master list of hosts ResolveURL and placenta itself can resolve
			# we'll check against this list to not waste connections on unsupported hosts
			hostDict = hostDict + hostprDict
			
			conns = 0 
			for pair in links:
			
				# try to be a little polite, and limit connections 
				#  (unless we're not getting sources)
				if conns > self.max_conns and len(sources) > self.min_srcs: break	 

				
				# the 2 groups from the link search = hoster name, episode page url
				host = pair[0].strip()	  
				link = pair[1]
				
				
				# check for valid hosts and jump to next loop if not valid
				valid, host = source_utils.is_host_valid(host, hostDict)
				#log_utils.log("\n\n** conn #%s: %s (valid:%s) %s" % (conns,host,valid,link)) #######
				if not valid: continue
				
				
				# two attempts per source link, then bail
				# NB: n sources could potentially cost n*range connections!!! 
				link = urlparse.urljoin(self.base_link, link)
				for i in range(2):
					result = client.request(link, timeout=3)
					conns += 1
					if not result == None: break	 
				
				
				# if both attempts failed, using the result will too, so bail to next loop
				try:
					link = re.compile('href="([^"]+)"\s+class="action-btn').findall(result)[0]
				except: 
					continue
					
					
				# I don't think this scraper EVER has direct links, but...
				#  (if nothing else, it sets the quality)
				try:
					u_q, host, direct = source_utils.check_directstreams(link, host)
				except:
					continue
					
				# check_directstreams strangely returns a list instead of a single 2-tuple
				link, quality = u_q[0]['url'], u_q[0]['quality']
				#log_utils.log('	checked host: %s' % host)
				#log_utils.log('	checked direct: %s' % direct)
				#log_utils.log('	quality, link: %s, %s' % (quality,link))
				#log_utils.log('	# of urls: %s' % len(u_q))

				
				sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': direct, 'debridonly': False})
					
			return sources
		except:
			failure = traceback.format_exc()
			log_utils.log('WATCHSERIES - Exception: \n' + str(failure))
			return sources


	def resolve(self, url):
		return url
