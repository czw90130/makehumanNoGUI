import sys
sys.path = ["./core", "./lib", "./shared", "./apps"] + sys.path
import os
import fnmatch
import log
from getpath import isSubPath, getSysDataPath
from human import Human
import humanmodifier
import files3d
from mh2obj import exportObj
from core import G


if __name__ == '__main__':
    human = Human(files3d.loadMesh(getSysDataPath("3dobjs/base.obj")))
    humanmodifier.loadModifiers(getSysDataPath('modifiers/modeling_modifiers.json'), human)
    G.setHuman(human)
    human.setGender(0)
    human.setAge(1)
    log.debug("Loaded human from base.obj")
    exportObj("test.obj", human)
