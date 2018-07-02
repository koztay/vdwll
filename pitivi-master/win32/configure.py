# -*- coding: utf-8 -*-
# Pitivi video editor
# Copyright (c) 2005, Edward Hervey <bilboed@bilboed.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, see <http://www.gnu.org/licenses/>.
"""
Utilities for getting the location of various directories.
Enables identical use for installed and uninstalled versions.
"""
import os.path

LIBDIR = os.path.realpath('../lib/pitivi')
WIN32_LIBDIR = '..\\..\\..\\..\\lib\\pitivi\\'
PKGDATADIR = os.path.realpath('../share/pitivi')
PIXMAPDIR = os.path.realpath('../share/pitivi/pixmaps')
pitivi_version = '0.13.4'
APPNAME = 'pitivi'
PYGTK_REQ = '2.12'
PYGST_REQ = '0.10'
GST_REQ = '0.10.22'
GNONLIN_REQ = '0.10.12'
PYCAIRO_REQ = '1.8'


def _get_root_dir():
    return '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])


def _in_devel():
    rd = _get_root_dir()
    return (os.path.exists(os.path.join(rd, '.svn')) or
            os.path.exists(os.path.join(rd, 'CVS')) or
            os.path.exists(os.path.join(rd, '.git')))


def get_pixmap_dir():
    """ Returns the directory for program-only pixmaps """
    _dir = os.path.dirname(os.path.abspath(__file__))
    if _in_devel():
        root = _dir
    else:
        root = PKGDATADIR
    print(os.path.join(root, 'pixmaps'))
    return os.path.join(root, 'pixmaps')


def get_global_pixmap_dir():
    """ Returns the directory for global pixmaps (ex : application icon) """
    if _in_devel():
        root = _get_root_dir()
    else:
        root = PIXMAPDIR
    return root
