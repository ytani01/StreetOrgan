#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
Handler1
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import tornado.web
from .rollbook import RollBook
from .my_logger import get_logger


class Download(tornado.web.RequestHandler):
    """
    Download SVG file
    """
    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._webroot = app.settings.get('webroot')
        self._mylog.debug('webroot=%s', self._webroot)

        self._workdir = app.settings.get('workdir')
        self._mylog.debug('workdir=%s', self._workdir)

        self._size_limit = app.settings.get('size_limit')
        self._mylog.debug('size_limit=%s', self._size_limit)

        # [!! 重要 !!] 末尾の「/」
        self._url_path = app.settings.get('url_prefix_handler1') + '/'

        self._version = app.settings.get('version')

        self._model_name = RollBook.DEF_MODEL_NAME
        self._conf_file = RollBook.DEF_CONF_FILE

        self._rollbook = RollBook(self._model_name, self._conf_file,
                                  debug=self._dbg)

        super().__init__(app, req)

    def get(self):
        """
        GET method and rendering
        """
        self._mylog.debug('request=%s', self.request)

        fname = self.request.uri.split('/')[-1]
        self._mylog.debug('fname=%s', fname)

        path_name = '%s/svg/%s' % (self._webroot, fname)
        self._mylog.debug('path_name=%s', path_name)

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition',
                        'attachment; filename=' + fname)

        buf_size = 4096
        with open(path_name, 'r') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)

        self.finish()


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

        self._webroot = app.settings.get('webroot')
        self._mylog.debug('webroot=%s', self._webroot)

        self._workdir = app.settings.get('workdir')
        self._mylog.debug('workdir=%s', self._workdir)

        self._size_limit = app.settings.get('size_limit')
        self._mylog.debug('size_limit=%s', self._size_limit)

        # [!! 重要 !!] 末尾の「/」
        self._url_path = app.settings.get('url_prefix_handler1') + '/'

        self._version = app.settings.get('version')

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

    def get(self, svg_data='', svg_filename='',
            msg='Please select a MIDI file'):
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
                    version=self._version,
                    copyright_year='2021',
                    size_limit=size_limit,
                    size_unit=size_unit,
                    svg_data=svg_data,
                    svg_filename=svg_filename,
                    msg=msg)

    async def post(self):
        """
        POST method
        """
        file1 = self.request.files['file1'][0]
        file1_fname = file1['filename']
        file1_path = '%s/midi/%s' % (self._webroot, file1_fname)
        svg1_fname = '%s.svg' % (file1_fname)
        svg1_path = '%s/svg/%s' % (self._webroot, svg1_fname)

        if not os.path.exists(file1_path):
            with open(file1_path, mode='wb') as f:
                f.write(file1['body'])

        f_size, unit = self.get_filesize(file1_path)
        msg = '%s (%.1f %s)' % (file1['filename'], f_size, unit)

        svg_data = self._rollbook.parse(file1_path)
        self._mylog.debug('svg_data=%a', svg_data)

        with open(svg1_path, mode='w') as f:
            f.write(svg_data)

        self.get(svg_data=svg_data, svg_filename=svg1_fname, msg=msg)
