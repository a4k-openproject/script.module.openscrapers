# -*- coding: utf-8 -*-
"""
    OpenScrapers Module

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Addon Name: OpenScrapers Module
# Addon id: script.module.openscrapers


import os
import sys
import urllib
import urlparse

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    import xbmcvfs
except:
    pass

integer = 1000

try:
    lang = xbmcaddon.Addon().getLocalizedString

    lang2 = xbmc.getLocalizedString

    setting = xbmcaddon.Addon().getSetting

    setSetting = xbmcaddon.Addon().setSetting

    addon = xbmcaddon.Addon

    addItem = xbmcplugin.addDirectoryItem

    item = xbmcgui.ListItem

    directory = xbmcplugin.endOfDirectory

    content = xbmcplugin.setContent

    property = xbmcplugin.setProperty

    addonInfo = xbmcaddon.Addon().getAddonInfo

    infoLabel = xbmc.getInfoLabel

    condVisibility = xbmc.getCondVisibility

    jsonrpc = xbmc.executeJSONRPC

    window = xbmcgui.Window(10000)

    dialog = xbmcgui.Dialog()

    progressDialog = xbmcgui.DialogProgress()

    progressDialogBG = xbmcgui.DialogProgressBG()

    windowDialog = xbmcgui.WindowDialog()

    button = xbmcgui.ControlButton

    image = xbmcgui.ControlImage

    getCurrentDialogId = xbmcgui.getCurrentWindowDialogId()

    keyboard = xbmc.Keyboard

    execute = xbmc.executebuiltin

    skin = xbmc.getSkinDir()

    player = xbmc.Player()

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

    resolve = xbmcplugin.setResolvedUrl

    openFile = xbmcvfs.File

    makeFile = xbmcvfs.mkdir

    deleteFile = xbmcvfs.delete

    deleteDir = xbmcvfs.rmdir

    listDir = xbmcvfs.listdir

    transPath = xbmc.translatePath

    skinPath = xbmc.translatePath('special://skin/')

    addonPath = xbmc.translatePath(addonInfo('path'))

    dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')

except:
    def setting(id):
        return ''

    dataPath = ''
    pass

# Modified `sleep` command that honors a user exit request
def sleep (time):
    while time > 0 and not xbmc.abortRequested:
        xbmc.sleep(min(100, time))
        time = time - 100

settingsFile = os.path.join(dataPath, 'settings.xml')

viewsFile = os.path.join(dataPath, 'views.db')

bookmarksFile = os.path.join(dataPath, 'bookmarks.db')

providercacheFile = os.path.join(dataPath, 'providers.13.db')

metacacheFile = os.path.join(dataPath, 'meta.5.db')

searchFile = os.path.join(dataPath, 'search.1.db')

libcacheFile = os.path.join(dataPath, 'library.db')

cacheFile = os.path.join(dataPath, 'cache.db')

key = "RgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6"

iv = "p2s5v8y/B?E(H+Mb"


def addonId():
    return addonInfo('id')


def addonName():
    return addonInfo('name')


def get_plugin_url(queries):
    try:
        query = urllib.urlencode(queries)
    except UnicodeEncodeError:
        for k in queries:
            if isinstance(queries[k], unicode):
                queries[k] = queries[k].encode('utf-8')
        query = urllib.urlencode(queries)
    addon_id = sys.argv[0]
    if not addon_id: addon_id = addonId()
    return addon_id + '?' + query

def apiLanguage(ret_name=None):
    langDict = {'Bulgarian': 'bg', 'Chinese': 'zh', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Finnish': 'fi', 'French': 'fr', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he', 'Hungarian': 'hu', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko', 'Norwegian': 'no', 'Polish': 'pl', 'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk', 'Slovenian': 'sl', 'Spanish': 'es', 'Swedish': 'sv', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk'}

    trakt = ['bg','cs','da','de','el','en','es','fi','fr','he','hr','hu','it','ja','ko','nl','no','pl','pt','ro','ru','sk','sl','sr','sv','th','tr','uk','zh']
    tvdb = ['en','sv','no','da','fi','nl','de','it','es','fr','pl','hu','el','tr','ru','he','ja','pt','zh','cs','sl','hr','ko']
    youtube = ['gv', 'gu', 'gd', 'ga', 'gn', 'gl', 'ty', 'tw', 'tt', 'tr', 'ts', 'tn', 'to', 'tl', 'tk', 'th', 'ti', 'tg', 'te', 'ta', 'de', 'da', 'dz', 'dv', 'qu', 'zh', 'za', 'zu', 'wa', 'wo', 'jv', 'ja', 'ch', 'co', 'ca', 'ce', 'cy', 'cs', 'cr', 'cv', 'cu', 'ps', 'pt', 'pa', 'pi', 'pl', 'mg', 'ml', 'mn', 'mi', 'mh', 'mk', 'mt', 'ms', 'mr', 'my', 've', 'vi', 'is', 'iu', 'it', 'vo', 'ii', 'ik', 'io', 'ia', 'ie', 'id', 'ig', 'fr', 'fy', 'fa', 'ff', 'fi', 'fj', 'fo', 'ss', 'sr', 'sq', 'sw', 'sv', 'su', 'st', 'sk', 'si', 'so', 'sn', 'sm', 'sl', 'sc', 'sa', 'sg', 'se', 'sd', 'lg', 'lb', 'la', 'ln', 'lo', 'li', 'lv', 'lt', 'lu', 'yi', 'yo', 'el', 'eo', 'en', 'ee', 'eu', 'et', 'es', 'ru', 'rw', 'rm', 'rn', 'ro', 'be', 'bg', 'ba', 'bm', 'bn', 'bo', 'bh', 'bi', 'br', 'bs', 'om', 'oj', 'oc', 'os', 'or', 'xh', 'hz', 'hy', 'hr', 'ht', 'hu', 'hi', 'ho', 'ha', 'he', 'uz', 'ur', 'uk', 'ug', 'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'as', 'ar', 'av', 'ay', 'az', 'nl', 'nn', 'no', 'na', 'nb', 'nd', 'ne', 'ng', 'ny', 'nr', 'nv', 'ka', 'kg', 'kk', 'kj', 'ki', 'ko', 'kn', 'km', 'kl', 'ks', 'kr', 'kw', 'kv', 'ku', 'ky']

    name = None
    name = setting('api.language')
    if not name: name = 'AUTO'
    
    if name[-1].isupper():
        try: name = xbmc.getLanguage(xbmc.ENGLISH_NAME).split(' ')[0]
        except: pass
    try: name = langDict[name]
    except: name = 'en'
    lang = {'trakt': name} if name in trakt else {'trakt': 'en'}
    lang['tvdb'] = name if name in tvdb else 'en'
    lang['youtube'] = name if name in youtube else 'en'

    if ret_name:
        lang['trakt'] = [i[0] for i in langDict.iteritems() if i[1] == lang['trakt']][0]
        lang['tvdb'] = [i[0] for i in langDict.iteritems() if i[1] == lang['tvdb']][0]
        lang['youtube'] = [i[0] for i in langDict.iteritems() if i[1] == lang['youtube']][0]

    return lang


def version():
    num = ''
    try: version = addon('xbmc.addon').getAddonInfo('version')
    except: version = '999'
    for i in version:
        if i.isdigit(): num += i
        else: break
    return int(num)


def cdnImport(uri, name):
    import imp
    from openscrapers.modules import client

    path = os.path.join(dataPath, 'py' + name)
    path = path.decode('utf-8')

    deleteDir(os.path.join(path, ''), force=True)
    makeFile(dataPath) ; makeFile(path)

    r = client.request(uri)
    p = os.path.join(path, name + '.py')
    f = openFile(p, 'w') ; f.write(r) ; f.close()
    m = imp.load_source(name, p)

    deleteDir(os.path.join(path, ''), force=True)
    return m


try:
    def openSettings(query=None, id=addonInfo('id')):
        try:
            idle()
            execute('Addon.OpenSettings(%s)' % id)
            if query == None: raise Exception()
            c, f = query.split('.')
            execute('SetFocus(%i)' % (int(c) + 100))
            execute('SetFocus(%i)' % (int(f) + 200))
        except:
            return
except:
    pass


def getCurrentViewId():
    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return str(win.getFocusId())


def refresh():
    return execute('Container.Refresh')

def busy():
    return execute('ActivateWindow(busydialog)')

def idle():
    return execute('Dialog.Close(busydialog)')


def queueItem():
    return execute('Action(Queue)')
