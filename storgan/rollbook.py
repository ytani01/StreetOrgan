#
# (c) 2021 Yoichi Tanibayashi
#
"""
Street Organ Roll Book Maker
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import json
from midilib import Parser
from .my_logger import get_logger


DEF_LINE_WIDTH = 0.1


def note2scale(midi_note, base_note, note_offset=[]) -> int:
    """
    Parameters
    ----------
    midi_note: int
    base_note: int
    note_offset: list of int

    Returns
    -------
    scale: int
    """
    scale = -1

    for s, offset in enumerate(note_offset):
        if base_note + offset == midi_note:
            scale = s
            break

    return scale

def svg_square(x, y, w, h, color, line_width=DEF_LINE_WIDTH,
               stroke_dasharray='none') -> str:
    """
    Parameters
    ----------
    x, y, w, h: float
    color: str
    line_width: float
    stroke_dasharray: str

    Returns
    -------
    svg: str

    """
    svg = '<path style="'
    svg += 'fill:none;'
    svg += 'stroke:%s;' % (color)
    svg += 'stroke-width:%s;' % (line_width)
    svg += 'stroke-dasharray:%s"' % (stroke_dasharray)
    svg += ' d="M %.2f %.2f h %.2f v %.2f h %.2f Z" />\n' % (
        -x, -y, -w, -h, w)

    return svg


class HoleInfo:
    """
    Roll Book Hole data entity

    Attributes
    ----------
    note_info: midilib.NoteInfo
        MIDI note information
    sec: float
        length in sec
    scale: int
        scale number
    x, y, w, h: float
        coordinate in mm
    """
    def __init__(self, note_info=None, conf=None, debug=False):
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        self.note_info = note_info
        self.conf = conf

        self.start_sec = self.note_info.abs_time
        self.sec = self.note_info.length()
        self.scale = note2scale(self.note_info.note,
                                self.conf['base note'],
                                self.conf['note offset'])

        self.x = self.start_sec * self.conf['1sec']
        self.y = self.scale * self.conf['pitch'] + self.conf['margin']
        self.w = self.sec * self.conf['1sec']
        self.h = self.conf['hole height']

    def __str__(self):
        """ __str__ """
        str_data = 'note:%03d start_sec:%07.2f sec:%05.2f' % (
            self.note_info.note, self.start_sec, self.sec)
        str_data += ' scale:%02d' % (self.scale)
        str_data += ' (%.2f, %.2f)-(%.2f, %.2f)' % (
            self.x, self.y, self.w, self.h)
        return str_data

    def svg(self, color='#FF0000', line_width=DEF_LINE_WIDTH,
            stroke_dasharray='none'):
        """ generate SVG

        Parameters
        ----------
        color: str
        line_width: float
        stroke_dasharray: str

        Returns
        -------
        svg: str
            SVG data
        """
        svg = svg_square(self.x, self.y, self.w, self.h,
                         color, line_width,
                         stroke_dasharray=stroke_dasharray)

        return svg


class RollBook:
    """ RollBook class
    """
    DEF_CONF_FILE = os.path.expanduser('~/bin/storgan.conf')

    def __init__(self, model: str, conf_file=DEF_CONF_FILE, debug=False):
        """ Constructor

        Parameters
        ----------
        model: str
            Model Name
        conf_file: str
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('model=%s', model)

        self._model = model
        self._conf_file = conf_file
        self._log.debug('conf_file=%s', self._conf_file)

        self._conf = self.get_conf(self._model, self._conf_file)
        self._log.debug('conf=%s', json.dumps(self._conf))

        self._width = 0
        self._height = self._conf['book height']
        self._holes = []
        self._svg = ''

        self._midi_parser = Parser(debug=self._dbg)

    def get_conf(self, model='ModelName', conf_file=DEF_CONF_FILE):
        """
        Parameters
        ----------
        model: str
            Model Name
        conf_file: str
            configuration file name
        """
        self._log.debug('model=%s, conf_file=%s',
                        model, conf_file)

        with open(conf_file) as f:
            all_conf = json.load(f)

        for conf in all_conf:
            if conf['model'] == model:
                return conf

        return {}

    def svg(self, color='#0000FF', hole_color='#FF0000',
            line_width=DEF_LINE_WIDTH, stroke_dasharray='none'):
        """ generate SVG

        Parameters
        ----------
        color: str
        hole_color: str
        line_width: float
        stroke_dasharray: str

        Returns
        -------
        svg: str
            SVG data
        """
        svg = '<svg xmlns="http://www.w3.org/2000/svg"'
        svg += ' width="%.2fmm" height="%.2fmm"' % (
            self._width, self._height)
        svg += ' viewBox="%s %s %s %s">\n' % (
            -self._width, -self._height, self._width, self._height)
        # svg += '<g id="all">\n'

        svg += svg_square(0, 0, self._width, self._height,
                          color, line_width,
                          stroke_dasharray=stroke_dasharray)

        for hi in self._holes:
            if hi.scale < 0:
                s1 = hi.svg(color='#000000', stroke_dasharray='3 1')
            else:
                s1 = hi.svg(color=hole_color)

            svg += s1

        # svg += '</g>\n'
        svg += '</svg>\n'
        return svg

    def parse(self, midi_file, channel=[]):
        """
        Parameters
        ----------
        midi_file: str
            MIDI file name
        channel: list of int
            selected MIDI channel ([]: all)

        Returns
        -------
        hole_list: list of HoleInfo

        """
        self._log.debug('midi_file=%s', midi_file)

        midi = self._midi_parser.parse(midi_file, channel)
        self._log.debug('midi[channel_set]=%s', midi['channel_set'])

        for ni in midi['note_info']:
            hi = HoleInfo(ni, self._conf, debug=self._dbg)
            self._log.debug('hi=%s', hi)

            if hi:
                self._width = max(hi.x + hi.w, self._width)

            self._holes.append(hi)

        self._log.debug('width=%s, len(hole)=%s',
                        self._width, len(self._holes))

        svg = self.svg()
        return svg
