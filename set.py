#!/usr/bin/env python3

import string
from math import *
import numpy as np
import weakref

alphanumeric = [str(i) for i in list(range(10)) + [j for j in string.ascii_uppercase]]
def alpha(dec):
    s=""
    for i in range(0, 5):
        s = alphanumeric[dec % 36] + s
        dec //= 36
    return s

class Set(object):
    counter = 1
    unnamedSets = []

    def __init__(self, name=None, otherSet=None, cmd=None):
        if name is None:
            self._name = "SE%s" % alpha(Set.counter)
            Set.counter += 1
            Set.unnamedSets.append(self)
        else:
            self._name = name
        if cmd is None:
            self.cmd = []
        else:
            self.cmd = cmd
        self.f = {}
        self.b = None
        if otherSet is not None:
            self.add(otherSet)

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        pass
        self.cmd.append("SETA %s se %s" % (name, self._name))
        self.cmd.append("SETR %s " % (self._name))
        if self in Set.unnamedSets:
            Set.unnamedSets.remove(self)
        self._name = name

    def intersect(self, sets, entity='se'):
        self.cmd.append("SETI %s %s %s" % (self._name, entity, ' '.join([str(i) for i in sets])))
        return self

    def open(self):
        self.cmd.append("SETO %s" % self._name)
        return self

    def close(self):
        self.cmd.append("SETC %s" % self._name)
        return self

    def delete(self):
        if self in Set.unnamedSets:
            Set.unnamedSets.remove(self)
        self.cmd.append("DEL se %s" % self._name)

    def zap(self):
        self.cmd.append("ZAP %s" % self._name)
        return self

    def rm(self, object, entity='se'):
        self.cmd.append("SETR %s %s %s" % (self._name, entity, object))
        return self

    def rmn(self, objects, entity='se'):
        for object in objects:
            self.rm(object, entity)
        return self

    def add(self, object, entity='se'):
        self.cmd.append("SETA %s %s %s" % (self._name, entity, object))
        return self

    def addn(self, objects, entity='se'):
        for object in objects:
            self.add(object, entity)
        return self

    def down(self):
        self.cmd.append("COMP %s do" % self._name)
        return self

    def up(self):
        self.cmd.append("COMP %s up" % self._name)
        return self

    def translate(self, vector, set='', div='', append=True):
        if append:
            app = 'a'
        else:
            app = ''

        if not set:
            op = 'MOVE'
            app = ''
        elif not div:
            op = 'COPY'
        else:
            op = 'SWEP'
#            if div > 99:
#                div = 98
            div = str(div)

        self.cmd.append("%s %s %s tra %.11f %.11f %.11f %s %s" % (
            op, self._name, set, vector[0], vector[1], vector[2], div, app))
        return self

    def rotate(self, p1, p2, angle, set='', div='', append=True):
        if append:
            app = 'a'
        else:
            app = ''

        if not set:
            op = 'MOVE'
            app = ''
        elif not div:
            op = 'COPY'
        else:
            op = 'SWEP'
            if div > 99:
                div = 98
            div = str(div)

        self.cmd.append("%s %s %s rot %s %s %.9f %s %s" % (
            op, self._name, set, p1, p2, angle, div, app))
        return self

    def mirror(self, p1, p2, set='', div='', append=True):
        if append:
            app = 'a'
        else:
            app = ''

        if not set:
            op = 'MOVE'
            app = ''
        elif not div:
            op = 'COPY'
        else:
            op = 'SWEP'
            if div > 99:
                div = 98
            div = str(div)

        self.cmd.append("%s %s %s mir %s %s %s %s" % (
            op, self._name, set, p1, p2, div, app))
        return self

    def scale(self, factor, point, set='', div='', append=True):
        if append:
            app = 'a'
        else:
            app = ''

        if not set:
            op = 'MOVE'
            app = ''
        elif not div:
            op = 'COPY'
        else:
            op = 'SWEP'
            if div > 99:
                div = 98
            div = str(div)

        self.cmd.append("%s %s %s scal %f %s %s %s" % (
            op, self._name, set, factor, point, div, app))
        return self

    def mergePoints(self, tol=1e-6):
        self.cmd.append("GTOL %f" % tol)
        self.cmd.append("MERG p %s" % self._name)
        return self

    def mergeLines(self, tol=1e-6):
        self.cmd.append("GTOL %f" % tol)
        self.cmd.append("MERG l %s" % self._name)
        return self

    def mergeFaces(self, tol=1e-6):
        self.cmd.append("GTOL %f" % tol)
        self.cmd.append("MERG s %s" % self._name)
        return self

    def mergeAll(self, tol=1e-6):
        self.cmd.append("GTOL %f" % tol)
        self.cmd.append("MERG p %s" % self._name)
        self.cmd.append("MERG l %s" % self._name)
        self.cmd.append("MERG s %s" % self._name)
        return self

    def bias(self, bias):
        self.cmd.append("BIA %s %.3f" % (self._name, bias))
        return self

    def send(self):
        self.cmd.append("SEND %s abq nam" % self._name)
        return self

    def sendFilm(self):
        self.cmd.append("SEND %s abq film 1. 1." % self._name)
        return self

    def sendRadiate(self):
        self.cmd.append("SEND %s abq rad 1. 1." % self._name)
        return self

    def sendFlux(self):
        self.cmd.append("SEND %s abq dflux 1." % self._name)
        return self
