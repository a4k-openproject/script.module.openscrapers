import os
import sys
import threading
import time

sys.path.append(os.path.join(os.path.curdir, 'lib'))
from lib import openscrapers

hosts = [u'', u'4shared.com', u'openload.co', u'rapidgator.net', u'sky.fm', u'thevideo.me', u'filesmonster.com',
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

# Set test_mode to 1 for automatic testing of all providers
# Set test_mode to 0 to select which provider to test
test_mode = 0

# Set test_mode to 'movie' to test movie scraping
# Set test_mode to 'episode' to test episode scraping
test_type = 'movie'

# Test information
movie_info = {'title': 'Inception', 'imdb': 'tt1375666', 'aliases': [], 'localtitle': 'Inception', 'year': '2010'}

# TODO Fill out showinfo and episode info for tests
show_info = {''}


def worker_thread(provider_name, provider_source):
    start_time = time.time()
    try:
        # Confirm Provider contains the movie function
        if not getattr(provider_source, test_type, False):
            return

        if not getattr(provider_source, 'unit_test', False):

            # Run movie Call
            url = provider_source.movie(movie_info['imdb'], movie_info['title'], movie_info['localtitle'],
                                        movie_info['aliases'], movie_info['year'])
            if url is None:
                failed_providers.append((provider_name, 'Movie Call Returned None'))

            # Run source call
            url = provider_source.sources(url, hosts, [])
            if url is None:
                failed_providers.append((provider_name, 'Sources Call Returned None'))

            # Gather time analytics
            runtime = time.time() - start_time

            passed_providers.append((provider_name, url, runtime))
        else:
            # Provider has unit test entry point, run provider with it
            try:
                unit_test = provider_source.unit_test('movie', hosts)
            except Exception as e:
                failed_providers.append((provider_name, e))
                return

            if unit_test is None:
                failed_providers.append((provider_name, 'Unit Test Returned None'))
                return

            runtime = time.time() - start_time

            passed_providers.append((provider_name, unit_test, runtime))

    except Exception as e:
        # Appending issue provider to failed providers
        failed_providers.append((provider_name, e))

provider_list = openscrapers.sources()
failed_providers = []
passed_providers = []
workers = []

if __name__ == '__main__':

    total_runtime = time.time()

    print('Running Unit Tests. Please Wait...')

    # Build and run threads
    if test_mode == 1:
        for provider in provider_list:
            workers.append(threading.Thread(target=worker_thread, args=(provider[0], provider[1])))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

    else:
        print('Please Select a provider:')
        for idx, provider in enumerate(provider_list):
            print('%s) %s' % (idx, provider[0]))

        while True:
            try:
                choice = int(raw_input())
                provider = provider_list[choice]
                break
            except ValueError:
                print('Please enter a number')
            except IndexError:
                print("You've entered and incorrect selection")

        worker_thread(provider[0], provider[1])

    total_runtime = time.time() - total_runtime

    # Print any failures to the console
    print(' ')
    print('Provider Failures:')
    print('##################')
    if len(failed_providers) == 0:
        print('None')
        print(' ')
    else:
        for provider in failed_providers:
            print('Provider Name: %s' % provider[0].upper())
            print('Exception: %s' % provider[1])
            print(' ')

    if test_mode == 1:
        all_sources = [source for sources in passed_providers for source in sources[1] if source is not None]
    else:
        all_sources = passed_providers[0][1]
        if all_sources is None:
            all_sources = []

    # TODO Expand analytical information
    print('Analytical Data:')
    print('################')
    if test_mode == 1:
        print('Total Runtime: %s' % total_runtime)
        print('Total Passed Providers: %s' % len(passed_providers))
        print('Total Failed Providers: %s' % len(failed_providers))
        print('Skipped Providers: %s' % (len(provider_list) - (len(passed_providers) + len(failed_providers))))
    else:
        print('Total No. Sources: %s' % len(all_sources))
