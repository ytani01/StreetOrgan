#
# (c) 2021 Yoichi Tanibayashi
#
"""
Web Interface
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import tornado.ioloop
import tornado.httpserver
import tornado.web
from .handler1 import Handler1, Download
from .my_logger import get_logger


class WebServer:
    """
    Web application server
    """
    DEF_PORT = 10081

    DEF_WEBROOT = './webroot'
    URL_PREFIX = '/storgan'
    URL_PREFIX_HANDLER1 = URL_PREFIX + '/handler1'

    DEF_WORKDIR = '/tmp/storgan'

    DEF_SIZE_LIMIT = 100*1024*1024  # 100MB

    def __init__(self, port=DEF_PORT,
                 webroot=DEF_WEBROOT, workdir=DEF_WORKDIR,
                 size_limit=DEF_SIZE_LIMIT,
                 version='current',
                 debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
            port number
        webroot: str

        workdir: str

        size_limit: int
            max upload size
        version: str
            version string
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.info('port=%s, webroot=%s, workdir=%s, size_limit=%s',
                       port, webroot, workdir, size_limit)
        self._log.info('version=%s', version)

        self._port = port
        self._webroot = webroot
        self._workdir = workdir
        self._size_limit = size_limit
        self._version = version

        try:
            os.makedirs(self._workdir, exist_ok=True)
        except Exception as ex:
            raise ex

        self._app = tornado.web.Application(
            [
                (r'/', Handler1),
                (r'%s' % self.URL_PREFIX, Handler1),
                (r'%s/' % self.URL_PREFIX, Handler1),
                (r'%s.*' % self.URL_PREFIX_HANDLER1, Handler1),
                (r'%s/download/.*' % self.URL_PREFIX, Download),
            ],
            static_path=os.path.join(self._webroot, "static"),
            static_url_prefix=self.URL_PREFIX + '/static/',
            template_path=os.path.join(self._webroot, "templates"),
            autoreload=True,
            # xsrf_cookies=False,

            # url_prefix_handler1=self.URL_PREFIX_HANDLER1,
            url_prefix_handler1=self.URL_PREFIX,

            webroot=self._webroot,
            workdir=self._workdir,
            size_limit=self._size_limit,
            version=self._version,

            debug=self._dbg
        )
        self._log.debug('app=%s', self._app.__dict__)

        self._svr = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=self._size_limit)
        self._log.debug('svr=%s', self._svr.__dict__)

    def main(self):
        """ main """
        self._log.debug('')

        self._svr.listen(self._port)
        self._log.info('start server: run forever ..')

        tornado.ioloop.IOLoop.current().start()

        self._log.debug('done')
