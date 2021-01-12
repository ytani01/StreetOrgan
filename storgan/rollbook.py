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


class HoleInfo:
    """
    Roll Book Hole data entity

    Attributes
    ----------
    note: int
        MIDI note number
    sec: float
        length in sec
    scale: int
        scale number
    x0, y0, x1, y1: float
        coordinate in mm
    """
    def __init__(self,
                 note=None, start_sec=None, sec=None,
                 scale=None,
                 x0=None, y0=None, x1=None, y1=None,
                 debug=False):
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        self.note = note
        self.start_sec = start_sec
        self.sec = sec

        self.scale = scale
        (self.x0, self.y0) = (x0, y0)
        (self.x1, self.y1) = (x1, y1)

    def __str__(self):
        """ __str__ """
        str_data = 'note:%03d start_sec:%07.2f sec:%05.2f' % (
            self.note, self.start_sec, self.sec)
        str_data += ' scale:%02d' % (self.scale)
        str_data += ' (%.2f, %.2f)-(%.2f, %.2f)' % (
            self.x0, self.y0, self.x1, self.y1)
        return str_data

    def svg(self):
        """
        Returns
        -------
        svg: str
            SVG data
        """
        svg = '<path style="'
        svg += 'fill:none;'
        svg += 'stroke:#0000FF;'
        svg += 'stroke-width:0.1;'
        svg += 'stroke-dasharray:none"'
        svg += ' d="M %.2f %.2f' % (self.x0, self.y0)
        svg += ' L %.2f %.2f' % (self.x1, self.y0)
        svg += ' L %.2f %.2f' % (self.x1, self.y1)
        svg += ' L %.2f %.2f' % (self.x0, self.y1)
        svg += ' L %.2f %.2f' % (self.x0, self.y0)
        svg += ' Z />"'

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

    def note2scale(self, note) -> int:
        """
        Parameters
        ----------
        note: int
            MIDI note number
        """
        scale = -1

        for s, offset in enumerate(self._conf['note offset']):
            if self._conf['base note'] + offset == note:
                scale = s
                break

        return scale

    def sec2mm(self, sec: float) -> float:
        """
        Parameters
        ----------
        sec: float
            length in sec

        Returns
        -------
        mm: float
            length in mm
        """
        mm = self._conf['1sec'] * sec
        return mm

    def noteinfo2holeinfo(self, note_info):
        """
        Parameters
        ----------
        note_info: midilib.NoteInfo

        Returns
        -------
        hole_info: HoleInfo

        """
        note = note_info.note
        start_sec = note_info.abs_time
        sec = note_info.length()
        mm = self.sec2mm(sec)
        scale = self.note2scale(note)

        if scale < 0:
            return None

        x0 = self.sec2mm(start_sec)
        y0 = scale * self._conf['pitch'] + self._conf['margin']
        x1 = x0 + mm
        y1 = y0 + self._conf['hole height']

        hole_info = HoleInfo(note=note, start_sec=start_sec, sec=sec,
                             scale=scale,
                             x0=x0, y0=y0, x1=x1, y1=y1,
                             debug=self._dbg)
        return hole_info

    def notes2holes(self, notes):
        """
        Parameters
        ----------
        notes: list of midilib.NoteInfo

        Returns
        -------
        hole_info: list of HoleInfo

        """
        hole_info = []

        self._width = 0

        for ni in notes:
            self._log.debug('ni=%s', ni)

            hi = self.noteinfo2holeinfo(ni)
            if hi:
                self._width = max(hi.x1, self._width)

            hole_info.append(hi)

        return hole_info

    def holes2svg(self, holes):
        """
        Parameters
        ----------
        holes: list of HoleInfo

        """
        svg = '<svg xmlns="%s" version="%s"' % (
            "http://www.w3.org/2000/svg", "1.1")
        svg += ' width="%.2fmm" height="%.2fmm"' % (
            self._width, self._height)
        svg += ' viewBox="0 0 %.2f %.2f">\n' % (
            self._width, self._height)

        for hi in holes:
            if hi is None:
                s1 = ''
            else:
                s1 = hi.svg()

            svg += s1 + '\n'

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

        holes = self.notes2holes(midi['note_info'])
        for hi in holes:
            self._log.debug('hi=%s', hi)

        svg = self.holes2svg(holes)
        print(svg)
