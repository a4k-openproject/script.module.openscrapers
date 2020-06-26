# -*- coding: utf-8 -*-
"""
	OpenScrapers Module
"""

import ast
import hashlib
import re
import time
try:
	from sqlite3 import dbapi2 as db, OperationalError
except ImportError:
	from pysqlite2 import dbapi2 as db, OperationalError

from openscrapers.modules import control
from openscrapers.modules import log_utils

cache_table = 'cache'


def get(function, duration, *args):
	# type: (function, int, object) -> object or None
	"""
	Gets cached value for provided function with optional arguments, or executes and stores the result
	:param function: Function to be executed
	:param duration: Duration of validity of cache in hours
	:param args: Optional arguments for the provided function
	"""

	try:
		key = _hash_function(function, args)
		cache_result = cache_get(key)
		if cache_result:
			if _is_cache_valid(cache_result['date'], duration):
				try:
					result = ast.literal_eval(cache_result['value'].encode('utf-8'))
				except:
					result = ast.literal_eval(cache_result['value'])
				return result

		fresh_result = repr(function(*args))
		if not fresh_result:
			# If the cache is old, but we didn't get fresh result, return the old cache
			if cache_result:
				return cache_result
			return None

		cache_insert(key, fresh_result)
		try:
			result = ast.literal_eval(fresh_result.encode('utf-8'))
		except:
			result = ast.literal_eval(fresh_result)
		return result
	except:
		log_utils.error()
		return None


def cache_get(key):
	try:
		cursor = _get_connection_cursor()
		cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='%s';" % cache_table)
		ck_table = cursor.fetchone()
		if not ck_table:
			cursor.close()
			return None
		cursor.execute("SELECT * FROM %s WHERE key = ?" % cache_table, [key])
		results = cursor.fetchone()
		cursor.close()
		return results
	except:
		log_utils.error()
		try:
			cursor.close()
		except:
			pass
		return None


def cache_insert(key, value):
	try:
		cursor = _get_connection_cursor()
		now = int(time.time())
		cursor.execute("CREATE TABLE IF NOT EXISTS %s (key TEXT, value TEXT, date INTEGER, UNIQUE(key))" % cache_table)
		update_result = cursor.execute("UPDATE %s SET value=?,date=? WHERE key=?" % cache_table, (value, now, key))
		if update_result.rowcount is 0:
			cursor.execute("INSERT INTO %s Values (?, ?, ?)" % cache_table, (key, value, now))
		cursor.connection.commit()
		cursor.close()
	except:
		log_utils.error()
		try:
			cursor.close()
		except:
			pass


def _get_connection_cursor():
	conn = _get_connection()
	return conn.cursor()


def _get_connection():
	control.makeFile(control.dataPath)
	conn = db.connect(control.cacheFile)
	conn.row_factory = _dict_factory
	return conn


def _dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


def _hash_function(function_instance, *args):
	return _get_function_name(function_instance) + _generate_md5(args)


def _get_function_name(function_instance):
	return re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))


def _generate_md5(*args):
	md5_hash = hashlib.md5()
	try:
		[md5_hash.update(str(arg)) for arg in args]
	except:
		[md5_hash.update(str(arg).encode('utf-8')) for arg in args]
	return str(md5_hash.hexdigest())


def _is_cache_valid(cached_time, cache_timeout):
	now = int(time.time())
	diff = now - cached_time
	return (cache_timeout * 3600) > diff