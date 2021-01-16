#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
Handler1
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'
__version__ = '0.1'

import os
import tornado.web
from .rollbook import RollBook
from .my_logger import get_logger


class Handler1(tornado.web.RequestHandler):
    """
    Web handler1
    """
    TITLE = 'Street Organ Roll Book Maker'

    HTML_FILE = 'storgan.html'

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._workdir = app.settings.get('workdir')
        self._mylog.debug('workdir=%s', self._workdir)

        self._size_limit = app.settings.get('size_limit')
        self._mylog.debug('size_limit=%s', self._size_limit)

        # [!! 重要 !!] 末尾の「/」
        self._url_path = app.settings.get('url_prefix_handler1') + '/'

        self._model_name = RollBook.DEF_MODEL_NAME
        self._conf_file = RollBook.DEF_CONF_FILE

        self._rollbook = RollBook(self._model_name, self._conf_file,
                                  debug=self._dbg)

        super().__init__(app, req)

    def get_size_unit(self, f_size):
        """
        Parameters
        ----------
        f_size: int
            file size (bytes)
        """
        size_unit = ['B', 'KB', 'MB', 'GB', 'TB']

        while f_size >= 1024:
            size_unit.pop(0)
            f_size /= 1024

        return f_size, size_unit[0]

    def get_filesize(self, file_path):
        """
        Parameters
        ----------
        file_path: str

        """
        if not os.path.exists(file_path):
            return None

        f_size = os.path.getsize(file_path)

        return self.get_size_unit(f_size)

    def get(self, svg_data='', msg='Please select a file'):
        """
        GET method and rendering
        """
        # self._mylog.debug('svg_data=%s', svg_data)
        self._mylog.debug('request=%s', self.request)

        if self.request.uri != self._url_path:
            self.redirect(self._url_path, permanent=True)
            return

        size_limit, size_unit = self.get_size_unit(self._size_limit)

        self.render(self.HTML_FILE,
                    title=self.TITLE,
                    author=__author__,
                    version=__version__,
                    copyright_year='2021',
                    size_limit=size_limit,
                    size_unit=size_unit,
                    svg_data=svg_data,
                    msg=msg)

    async def post(self):
        """
        POST method
        """
        file1 = self.request.files['file1'][0]
        file1_path = '%s/%s' % (self._workdir, file1['filename'])
        svg1_path = '%s.svg' % (file1_path)

        if not os.path.exists(file1_path):
            with open(file1_path, mode='wb') as f:
                f.write(file1['body'])

        f_size, unit = self.get_filesize(file1_path)
        msg = '%s (%.1f %s)' % (file1_path, f_size, unit)

        svg_data = self._rollbook.parse(file1_path)
        self._mylog.debug('svg_data=%a', svg_data)

        with open(svg1_path, mode='w') as f:
            f.write(svg_data)

        self.get(svg_data=svg_data, msg=msg)
