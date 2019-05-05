import json
import os
import random
import sys
import threading
import time
import traceback

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append(os.path.join(os.path.curdir, 'lib'))

arguments = {}

for i in sys.argv:
    try:
        i = i.split('=')
        arguments.update({i[0]: i[1]})
    except:
        pass

print(arguments)

folders = arguments.get('folders', None)

if folders is not None:
    folders = folders.split(',')
else:
    folders = None

test_type = int(arguments.get('test_type', 1))

test_mode = arguments.get('test_mode', 'movie')

TIMEOUT_MODE = arguments.get('timeout_mode', False)

no_tests = int(arguments.get('number_of_tests', '10'))

if TIMEOUT_MODE in ['true', 'True', 'y']:
    no_tests = 1
    TIMEOUT_MODE = True
else:
    TIMEOUT_MODE = False

from lib import openscrapers

print('Testing Folders: %s' % (' | '.join(folders if folders is not None else ['All'])))
print('Running %s tests' % no_tests)

# Test information
movie_meta = []
episode_meta = []
trakt_api_key = 'c1d7d1519b5d70158fc568c42b8c7a39b4f73a73e17e25c0e85152a542cd1664'  # Soz Not Soz ExodusRedux

trakt_movies_url = 'https://api.trakt.tv/movies/popular?extended=full&limit=%s' % (no_tests - 1)
trakt_shows_url = 'https://api.trakt.tv/shows/popular?extended=full&limit=%s' % no_tests
trakt_episodes_url = 'https://api.trakt.tv/shows/%s/seasons?extended=episodes'

print('######################################')
print('GETTING META FROM TRAKT ....')
print('######################################')

trakt_headers = {'trakt-api-version': '2', 'trakt-api-key': trakt_api_key, 'Content-Type': 'application/json'}

if test_mode == 'movie':
    resp = requests.get(trakt_movies_url, headers=trakt_headers)
    resp = json.loads(resp.text)

    movie_meta.append({'imdb': u'tt1270797', 'title': u'Venom', 'localtitle': u'Venom',
                       'year': str(2018), 'aliases': []})

    for movie in resp:
        if movie['title'] == 'Venom':
            continue
        print('Adding Movie: %s' % movie['title'])
        movie_meta.append({'imdb': movie['ids']['imdb'], 'title': movie['title'], 'localtitle': movie['title'],
                           'year': str(movie['year']), 'aliases': []})

else:
    resp = requests.get(trakt_shows_url, headers=trakt_headers)
    resp = json.loads(resp.text)

    for show in resp:
        episodes = requests.get(trakt_episodes_url % show['ids']['trakt'], headers=trakt_headers)
        episodes = json.loads(episodes.text)
        episodes = [episode for season in episodes for episode in season['episodes'] if season['number'] != 0]
        random.shuffle(episodes)
        episode = episodes[0]
        print('Adding Episode: %s - S%sE%s' % (show['title'], episode['season'], episode['number']))
        episode_meta.append({'show_imdb': show['ids']['imdb'], 'show_tvdb': show['ids']['tvdb'],
                             'tvshowtitle': show['title'], 'localtvshowtitle': show['title'], 'aliases': [],
                             'year': show['year'], 'imdb': episode['ids']['imdb'], 'tvdb': episode['ids']['tvdb'],
                             'title': episode['title'], 'premiered': '', 'season': episode['season'],
                             'episode': episode['number']})

RUNNING_PROVIDERS = []
TOTAL_SOURCES = []
PROVIDER_LIST = openscrapers.sources(folders, True)
FAILED_PROVIDERS = []
PASSED_PROVIDERS = []
workers = []
TOTAL_RUNTIME = 0
TIMEOUT = 10

hosts = [u'4shared.com', u'openload.co', u'rapidgator.net', u'sky.fm', u'thevideo.me', u'filesmonster.com',
         u'youtube.com', u'icerbox.com', u'nitroflare.com', u'1fichier.com', u'docs.google.com', u'mediafire.com',
         u'hitfile.net', u'2shared.com', u'rapidvideo.com', u'filerio.com', u'extmatrix.com', u'datafile.com',
         u'solidfiles.com', u'dl.free.fr', u'inclouddrive.com', u'zippyshare.com', u'unibytes.com', u'flashx.tv',
         u'canalplus.fr', u'redbunker.net', u'nowvideo.club', u'dailymotion.com', u'load.to', u'uploaded.net',
         u'scribd.com', u'big4shared.com', u'rockfile.eu', u'uptobox.com', u'filesabc.com', u'streamcherry.com',
         u'isra.cloud', u'filefactory.com', u'youporn.com', u'oboom.com', u'vimeo.com', u'real-debrid.com',
         u'redtube.com', u'file.al', u'faststore.org', u'soundcloud.com', u'gigapeta.com', u'share-online.biz',
         u'datei.to', u'datafilehost.com', u'depositfiles.com', u'rutube.ru', u'upstore.net', u'salefiles.com',
         u'streamango.com', u'cbs.com', u'worldbytez.com', u'turbobit.net', u'mega.co.nz', u'tusfiles.net',
         u'uploadc.com', u'wipfiles.net', u'hulkshare.com', u'rarefile.net', u'sendspace.com', u'vidoza.net',
         u'alfafile.net', u'keep2share.cc', u'yunfile.com', u'vidlox.tv', u'catshare.net', u'vk.com',
         u'clicknupload.me', u'userscloud.com', u'ulozto.net', u'easybytez.com']


def domain_analysis(domain_name):
    result = {'domain_status': 'None', 'domain_protocol': '', 'domain_name': '', 'domain_http_enabled': '',
              'cloudflare_enabled': '', 'cloudflare_captcha_enabled': '', 'cloudflare_antibot_enabled': ''}
    try:
        resp = requests.get(domain_name)
        result['domain_status'] = resp.status_code
        parsed_url = urlparse(resp.url)
        cookie_domain = None

        result['domain_protocol'] = parsed_url.scheme
        result['domain_name'] = parsed_url.netloc

        for d in resp.cookies.list_domains():
            if d.startswith(".") and d in ("." + parsed_url.netloc):
                cookie_domain = d
                break

        cloudflare_cookie = resp.cookies.get("__cfduid", "", domain=cookie_domain)
        result['cloudflare_enabled'] = cloudflare_cookie is not None
        if resp.headers.get('Server', '').startswith('cloudflare'):
            if b'/cdn-cgi/l/chk_captcha' in resp.content:
                result['cloudflare_captcha_enabled'] = True
            elif resp.status_code == 503:
                result['cloudflare_antibot_enabled'] = True

        result['domain_status'] = resp.status_code
    except Exception:
        result['domain_status'] = 'Error'
    return result


def worker_thread(provider_name, provider_source):
    global RUNNING_PROVIDERS
    global TOTAL_SOURCES
    global PASSED_PROVIDERS
    global FAILED_PROVIDERS
    RUNNING_PROVIDERS.append(provider_name)
    try:
        # Confirm Provider contains the movie function
        if getattr(provider_source, test_mode, False):
            analysis = {}

            # Run analysis on the domains
            if not hasattr(provider_source, 'base_link'):
                print('Warning: provider %s is missing base_link property' % provider_name)
            else:
                analysis = domain_analysis(provider_source.base_link)

                if analysis['domain_status'] is not 'Offline' \
                        and not hasattr(provider_source, 'scraper') \
                        and ('cloudflare_enabled' in analysis and analysis['cloudflare_enabled']):
                    print('Warning: provider %s is missing a CF scraper but CF cookie is detected' % provider_name)

            if hasattr(provider_source, 'base_link') \
                    and (('domain_status' not in analysis) or (analysis['domain_status'] is 'Offline')):
                print('Warning: Error while fetching domains for provider %s' % provider_name)

            if test_mode == 'movie':
                test_objects = movie_meta
            elif test_mode == 'episode':
                test_objects = episode_meta
            else:
                RUNNING_PROVIDERS.remove(provider_name)
                return

            url = []
            start_time = time.time()

            for i in test_objects:
                if TIMEOUT_MODE and TOTAL_RUNTIME > TIMEOUT:
                    break

                # Prepare test by fetching url
                if test_mode == 'movie':
                    url = provider_source.movie(i['imdb'], i['title'], i['localtitle'], i['aliases'], i['year'])
                    if url is None:
                        print('Warning provider (%s) returned none from movie method' % provider_name)
                        continue

                elif test_mode == 'episode':
                    url = provider_source.tvshow(i['show_imdb'], i['show_tvdb'], i['tvshowtitle'],
                                                 i['localtvshowtitle'], i['aliases'], i['year'])
                    if url is None:
                        print('Warning provider (%s) returned none from tvshow method' % provider_name)
                        continue

                    url = provider_source.episode(url, i['imdb'], i['tvdb'], i['title'], i['premiered'],
                                                  i['season'],
                                                  i['episode'])
                    if url is None:
                        print('Warning provider (%s) returned none from episode method' % provider_name)
                        continue
                else:
                    RUNNING_PROVIDERS.remove(provider_name)
                    return

                # Execute source method to gather urls
                url = provider_source.sources(url, hosts, [])
                if url is None:
                    continue
                else:
                    if len(url) > 0:
                        TOTAL_SOURCES += url
                    else:
                        continue
            if url is None:
                url = []
            # Gather time analytics
            runtime = time.time() - start_time
            PASSED_PROVIDERS.append((provider_name, url, runtime, analysis))
    except Exception as e:
        traceback.print_exc()
        RUNNING_PROVIDERS.remove(provider_name)
        # Appending issue provider to failed providers
        FAILED_PROVIDERS.append((provider_name, e))

    try:
        RUNNING_PROVIDERS.remove(provider_name)
    except:
        pass


if __name__ == '__main__':

    TOTAL_RUNTIME = 0

    print('Running Unit Tests. Please Wait...')

    # Build and run threads
    if test_type == 1:
        for provider in PROVIDER_LIST:
            workers.append(threading.Thread(target=worker_thread, args=(provider[0], provider[1])))

        for worker in workers:
            worker.start()
        time.sleep(1)

        while len(RUNNING_PROVIDERS) > 0:
            if TOTAL_RUNTIME > TIMEOUT and TIMEOUT_MODE:
                break
            print('Running Providers [%s]: %s' % (len(RUNNING_PROVIDERS),
                                                  ' | '.join([i.upper() for i in RUNNING_PROVIDERS])))
            time.sleep(1)
            TOTAL_RUNTIME += 1
    else:
        print('Please Select a provider:')
        for idx, provider in enumerate(PROVIDER_LIST):
            print('%s) %s' % (idx, provider[0]))

        while True:
            try:
                choice = int(raw_input())
                provider = PROVIDER_LIST[choice]
                break
            except ValueError:
                print('Please enter a number')
            except IndexError:
                print("You've entered and incorrect selection")

        RUNNING_PROVIDERS.append('')
        worker_thread(provider[0], provider[1])

    # Print any failures to the console
    print(' ')
    print('Provider Failures:')
    print('##################')
    if len(FAILED_PROVIDERS) == 0:
        print('None')
        print(' ')
    else:
        for provider in FAILED_PROVIDERS:
            print('Provider Name: %s' % provider[0].upper())
            print('Exception: %s' % provider[1])
            print(' ')

    # TODO Expand analytical information
    print('Analytical Data:')
    print('################')
    if test_type == 1:
        print('Total Runtime: %s' % TOTAL_RUNTIME)
        print('Total Passed Providers: %s' % len(PASSED_PROVIDERS))
        print('Total Failed Providers: %s' % len(FAILED_PROVIDERS))
        print('Skipped Providers: %s' % (len(PROVIDER_LIST) - (len(PASSED_PROVIDERS) + len(FAILED_PROVIDERS))))

    elif test_type == 0:
        all_sources = PASSED_PROVIDERS[0][1]
        if all_sources is None:
            all_sources = []
    pre_dup = TOTAL_SOURCES
    post_dup = {}
    for i in TOTAL_SOURCES:
        post_dup.update({str(i['url']): i})
    total_duplicates = len(pre_dup) - len([i for i in post_dup])
    print('Total Sources: %s' % len(post_dup))
    print('Total Duplicates: %s' % total_duplicates)
    print('   ')
    print('Sources quality:')
    print('#################')
    quality = {}
    for i in TOTAL_SOURCES:
        quality.update({i['quality']: quality[i['quality']] + 1 if i['quality'] in quality else 1})
    for x in quality:
        print('%s: %s Sources' % (x, quality[x]))

    base_output_path = os.path.join(os.getcwd(), 'test-results', '-'.join(folders if folders is not None else ['All']))
    output_filename = 'results-%s' % time.time()

    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)

    with open(os.path.join(base_output_path, output_filename + '.csv'), 'w+') as output:
        output.write('Provider Name,Number Of Sources,Runtime,%s\n' %
                     ','.join(str(x) for x in PASSED_PROVIDERS[0][3].keys()))
        for i in PASSED_PROVIDERS:
            try:
                if i[1] is not None:
                    output.write('%s,%s,%s,%s\n' % (
                        i[0], len([] if i[1] is None else i[1]), i[2], ','.join(str(x) for x in i[3].values())))
            except:
                pass

    for i in PASSED_PROVIDERS:
        if len(i[1]) > 0:
            with open(os.path.join(base_output_path, output_filename + '-' + i[0] + '.csv'), 'w+') as output:
                output.write('%s\n' % ','.join(str(x) for x in i[1][0].keys()))
                try:
                    if i[1] is not None:
                        for s in i[1]:
                            output.write('%s\n' % ','.join(str(x) for x in s.values()))
                except:
                    pass