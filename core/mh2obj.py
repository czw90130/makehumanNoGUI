#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------
Exports proxy mesh to obj

"""

import wavefront
import os
import numpy as np
import log

class Config:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{name}'")

def goodName(name):
        string = name.replace(" ", "_").replace("-","_").lower()
        return string

def setupTexFolder(filepath):
        import os

        def _getSubFolder(path, name):
            folder = os.path.join(path, name)
            if not os.path.exists(folder):
                log.message("Creating folder %s", folder)
                try:
                    os.mkdir(folder)
                except:
                    log.error("Unable to create separate folder:", exc_info=True)
                    return None
            return folder

        (fname, ext) = os.path.splitext(filepath)
        fname = goodName(os.path.basename(fname))
        outFolder = os.path.realpath(os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        texFolder = _getSubFolder(outFolder, "textures")
        _copiedFiles = {}

def exportObj(filepath, human, hiddenGeom=False):

    setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = goodName(os.path.splitext(filename)[0])

    objects = human.getObjects(excludeZeroFaceObjs=not hiddenGeom)
    meshes = [o.mesh for o in objects]

    if hiddenGeom:
        # Disable the face masking on copies of the input meshes
        meshes = [m.clone(filterMaskedVerts=False) for m in meshes]
        for m in meshes:
            # Would be faster if we could tell clone() to do this, but it would 
            # make the interface more complex.
            # We could also let the wavefront module do this, but this would 
            # introduce unwanted "magic" behaviour into the export function.
            face_mask = np.ones(m.face_mask.shape, dtype=bool)
            m.changeFaceMask(face_mask)
            m.calcNormals()
            m.updateIndexBuffer()

    config_dict = {
        'scale': 1.0,
        'feetOnGround': False,
        'offset': [0, 0, 0],
        'useNormals': True,
    }

    config = Config(config_dict)
    log.message("Writing OBJ file %s", filepath)
    wavefront.writeObjFile(filepath, meshes, True, config, filterMaskedFaces=not hiddenGeom)

    log.message("OBJ Export finished. Output file: %s" % filepath)
