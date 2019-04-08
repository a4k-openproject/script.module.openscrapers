
#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.


import re,urllib,urlparse

from openscrapers.modules  import cleantitle, client, log_utils, source_utils, cfscrape

from bs4 import BeautifulSoup


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['filepursuit.com']                                                                   # List of base urls, such as 'filmfrantic.com'
        self.base_link = 'https://filepursuit.com'                                                                      # Base URL, such as 'http://filmfrantic.com'
        self.search_link = '/pursuit?q='                                                           # part of link on search results page, with %s on any portion where you need to insert title, year, etc.
                                                                                                                # Example: '/s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            pass

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            # if no link returned in movie and tvshow searches, nothing to do here, return out.
            if url == None or len(url) == 0:
                return sources

            #Time to get scraping
            title = url['title']
            year = url['title']
            #Build up the search url
            searchLink = self.search_link + title + ' ' + year
            url = urlparse.urljoin(self.base_link, searchLink)

            #Site uses cf, so we need cfscrape
            scraper = cfscrape.create_scraper()
            html = scraper.get(url).content
            result_soup = BeautifulSoup(html, "html.parser")

            #Parse the table of results
            table = result_soup.find("table")
            table_body = table.find("tbody")
            rows = table_body.findAll("tr")
            fileLinks = []
            for row in rows:
                cols = row.findAll("td")
                for col in cols:
                    links = col.findAll("a", href=True)
                    for link in links:
                        if "/file/" in link['href']:
                            #Use this onse
                            fileLinks.append(link['href'])
                            break
            #Retrieve actual links from result pages
            actualLinks = []
            for fileLink in fileLinks:
                actual_url = urlparse.urljoin(self.base_link, fileLink)
                html = scraper.get(actual_url.encode('ascii')).content
                linkSoup = BeautifulSoup(html, "html.parser")
                link = str(linkSoup.find("button", {"title": "Copy Link"})['data-clipboard-text'])               
                #Exclude zip and rar files
                if link.lower().endswith('rar') or link.lower().endswith('zip'):
                    continue
                else:
                    actualLinks.append(link)

            for link in actualLinks:
                quality,info = source_utils.get_release_quality(link, url)
                sources.append({'source': 'DIRECT', 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': True, 'debridonly': False})
            return sources
        except Exception as e:
            #log_utils.log('EXCEPTION MSG: '+str(e))
            return sources

    def resolve(self, url):
        return url