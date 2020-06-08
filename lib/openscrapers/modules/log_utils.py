# -*- coding: utf-8 -*-


try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO
import cProfile
import inspect
import json
import os
import pstats
import time
from datetime import datetime

from openscrapers.modules import control

try:
	import xbmc
	from xbmc import LOGDEBUG, LOGERROR, LOGNOTICE, LOGWARNING  # @UnusedImport

	LOGPATH = xbmc.translatePath('special://logpath/')
	name = control.addonInfo('name')
except:
	xbmc = False
	LOGDEBUG = "LOGDEBUG"
	LOGERROR = "LOGERROR"
	LOGNOTICE = "LOGNOTICE"
	LOGWARNING = "LOGWARNING"
	name = "OPENSCRAPERS"

# Using color coding, for color formatted log viewers like Assassin's Tools
DEBUGPREFIX = '[COLOR red][ OPENSCRAPERS DEBUG ][/COLOR]'


def log(msg, caller=None, level=LOGNOTICE):
	debug_enabled = control.setting('debug.enabled')
	debug_log = control.setting('debug.location')

	print DEBUGPREFIX + ' Debug Enabled?: ' + str(debug_enabled)
	print DEBUGPREFIX + ' Debug Log?: ' + str(debug_log)

	if control.setting('debug.enabled') != 'true':
		return

	try:
		if caller is not None and level == LOGDEBUG:
			func = inspect.currentframe().f_back.f_code
			line_number = inspect.currentframe().f_back.f_lineno
			caller = "%s.%s()" % (caller, func.co_name)
			msg = 'From func name: %s Line # :%s\n                       msg : %s' % (caller, line_number, msg)

		if caller is not None and level == LOGERROR:
			msg = 'From func name: %s.%s() Line # :%s\n                       msg : %s'%(caller[0], caller[1], caller[2], msg)

		if isinstance(msg, unicode):
			msg = '%s (ENCODED)' % (msg.encode('utf-8'))

		if not control.setting('debug.location') == '0':
			log_file = os.path.join(LOGPATH, 'openscrapers.log')
			if not os.path.exists(log_file):
				f = open(log_file, 'w')
				f.close()
			with open(log_file, 'a') as f:
				line = '[%s %s] %s: %s' % (datetime.now().date(), str(datetime.now().time())[:8], DEBUGPREFIX, msg)
				f.write(line.rstrip('\r\n') + '\n')
		else:
			print('%s: %s' % (DEBUGPREFIX, msg))
	except Exception as e:
		try:
			xbmc.log('Logging Failure: %s' % (e), level)
		except:
			pass


def error(message=None, exception=True):
	try:
		import sys
		if exception:
			type, value, traceback = sys.exc_info()
			sysaddon = sys.argv[0].split('//')[1].replace('/', '.')
			filename = (traceback.tb_frame.f_code.co_filename).replace('\\', '.').replace('.py', '')
			filename = filename.split(sysaddon)[1].replace('\\', '.')
			name = traceback.tb_frame.f_code.co_name
			linenumber = traceback.tb_lineno
			errortype = type.__name__
			errormessage = value.message
			if errormessage == '':
				raise Exception()
			if message:
				message += ' -> '
			else:
				message = ''
			message += str(errortype) + ' -> ' + str(errormessage)
			caller = [filename, name, linenumber]
		else:
			caller = None
		log(msg=message, caller=caller, level = LOGERROR)
	except:
		pass


class Profiler(object):
	def __init__(self, file_path, sort_by='time', builtins=False):
		self._profiler = cProfile.Profile(builtins=builtins)
		self.file_path = file_path
		self.sort_by = sort_by

	def profile(self, f):
		def method_profile_on(*args, **kwargs):
			try:
				self._profiler.enable()
				result = self._profiler.runcall(f, *args, **kwargs)
				self._profiler.disable()
				return result
			except Exception as e:
				log('Profiler Error: %s' % e, LOGWARNING)
				return f(*args, **kwargs)

		def method_profile_off(*args, **kwargs):
			return f(*args, **kwargs)

		if _is_debugging():
			return method_profile_on
		else:
			return method_profile_off

	def __del__(self):
		self.dump_stats()

	def dump_stats(self):
		if self._profiler is not None:
			s = StringIO()
			params = (self.sort_by,) if isinstance(self.sort_by, basestring) else self.sort_by
			ps = pstats.Stats(self._profiler, stream=s).sort_stats(*params)
			ps.print_stats()
			if self.file_path is not None:
				with open(self.file_path, 'w') as f:
					f.write(s.getvalue())


def trace(method):
	def method_trace_on(*args, **kwargs):
		start = time.time()
		result = method(*args, **kwargs)
		end = time.time()
		log('{name!r} time: {time:2.4f}s args: |{args!r}| kwargs: |{kwargs!r}|'.format(name=method.__name__,
																					   time=end - start, args=args,
																					   kwargs=kwargs), LOGDEBUG)
		return result

	def method_trace_off(*args, **kwargs):
		return method(*args, **kwargs)

	if _is_debugging():
		return method_trace_on
	else:
		return method_trace_off


def _is_debugging():
	command = {'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.getSettings',
			   'params': {'filter': {'section': 'system', 'category': 'logging'}}}
	js_data = execute_jsonrpc(command)
	for item in js_data.get('result', {}).get('settings', {}):
		if item['id'] == 'debug.showloginfo':
			return item['value']
	return False


def execute_jsonrpc(command):
	if not isinstance(command, basestring):
		command = json.dumps(command)
	response = control.jsonrpc(command)
	return json.loads(response)
