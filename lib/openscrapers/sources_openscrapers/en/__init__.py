# -*- coding: UTF-8 -*-

import os.path

sourcePath = os.path.dirname(__file__)

files = os.listdir(os.path.dirname(__file__))

__all__ = [filename[:-3] for filename in files if not filename.startswith('__') and filename.endswith('.py')]   