#!/usr/bin/env python3

from .set import Set
import numpy as np
import sys

class Cgx(object):
    def __init__(self):
        self.cmd = []

    def cleanAll(self):
        for instance in Set.unnamedSets[:]:
            instance.delete()

    def clear(self):
        del(self.cmd[:])

    def write(self, filename=None):
        self.cleanAll()
        if filename is None:
            for command in self.cmd:
                print(command)
        else:
            with open(filename, 'w') as fobj:
                for command in self.cmd:
                    print(command, file=fobj)

    def addCmd(self, command):
        self.cmd.append(command)

    def mesh(self):
        self.cmd.append("MESH all")

    def meshLinear(self):
        self.cmd.append("ELTY all")
        self.cmd.append("ELTY all he8")
        self.mesh()

    def meshQuadratic(self):
        self.cmd.append("ELTY all")
        self.cmd.append("ELTY all he20")
        self.mesh()

    def sendMesh(self):
        self.cmd.append("SEND all abq")

    def read(self, filename):
        self.cmd.append("READ %s" % filename)

    def makeSet(self, name=None, otherSet=None):
        newSet = Set(name, otherSet, self.cmd)
        return newSet

    def makePoint(self, x, y, z, name=None):
        newSet = self.makeSet(name)
        self.cmd.append("PNT %s %.9f %.9f %.9f" % (newSet, x, y, z) )
        newSet.add(newSet, 'p')
        return newSet

    def makeLine(self, p1, p2, div=4, bias=1, elbia=1., name=None):
        newSet = self.makeSet(name)
        if elbia < 0:
            elbia = -1 / elbia
        if div > 99:
            div = 98
        self.cmd.append("LINE %s %s %s %d %f" % (newSet, p1, p2, div, elbia))
        newSet.add(newSet, 'l')
        return newSet

    def makeArc(self, p1, p2, pc, div=4, name=None):
        newSet = self.makeSet(name)
        if elbia < 0:
            elbia = -1 / elbia
        if div > 99:
            div = 98
        self.cmd.append("LINE %s %s %s %s %d" % (newSet, p1, p2, pc, self.div))
        newSet.add(newSet, 'l')
        return newSet

    def makeWire(self, Lines, signes=None, name=None):
        newSet = self.makeSet(name)
        if signes is None:
            signes = len(Lines) * "+"
        allLines = ""
        for sign, Line in zip(signes, Lines):
            allLines += "%s %s " % (sign, Line)
        self.cmd.append("LCMB %s %s" % (newSet, allLines))
        newSet.add(newSet, 'c')
        return newSet

    def makeSurface(self, lines, name=None):
        newSet = self.makeSet(name)
        self.cmd.append("SURF %s %s" % (newSet, ' '.join([str(i) for i in lines])))
        newSet.add(newSet, 's')
        return newSet

    def makeBody(self, faces, name=None):
        newSet = self.makeSet(name)
        self.cmd.append("BODY %s %s" % (newSet, ' '.join([str(i) for i in faces])))
        newSet.add(newSet, 'b')
        return newSet

    def makeBoxDXDYDZ(self, origin, dimension, div=[2,2,2], bias=[1., 1., 1.], name=None):
        newSet = self.makeSet(name)

        point = self.makePoint(origin[0], origin[1], origin[2])
        dim = dimension

        faces = []
        for i in [2,1,0]:
            min = self.makeSet()
            max = self.makeSet()
            vector = 3 * [0.]
            vector[i] = dim[i]

            min.add(point)
            min.up()
            min.translate(vector, max, div[i])

            min.down()
            max.down()

            faces.append(min)
            faces.append(max)

        newSet.minZ = faces[0]
        newSet.maxZ = faces[1]
        newSet.minY = faces[2]
        newSet.maxY = faces[3]
        newSet.minX = faces[4]
        newSet.maxX = faces[5]

        newSet.add(point)
        newSet.up()
        newSet.down()

#
#        for i in range(0, 3):
#            biasN = self.makeSet()
#            biasN.add(newSet)
#            biasN.rm(newSet.f[ face_names[2*i] ])
#            biasN.rm(newSet.f[ face_names[2*i+1] ])
#            biasN.bias(bias[i])

        biasN = self.makeSet()
        biasN.add(newSet)
        biasN.rm(newSet.minX)
        biasN.rm(newSet.maxX)
        biasN.bias(bias[i])

        biasN = self.makeSet()
        biasN.add(newSet)
        biasN.rm(newSet.minY)
        biasN.rm(newSet.maxY)
        biasN.bias(bias[i])

        biasN = self.makeSet()
        biasN.add(newSet)
        biasN.rm(newSet.minZ)
        biasN.rm(newSet.maxZ)
        biasN.bias(bias[i])

        return newSet

    def makeBigBox(self, origin, dimension, div, name=None):
        newSet = self.makeSet(name)

        nBoxes = []
        for divI in div:
            nBoxes.append(int(divI/99 + 1))

        boxSize = np.array(dimension) / np.array(nBoxes)
        boxDiv = [int(x) for x in (np.array(div) / np.array(nBoxes)) / 2 * 2]

#        for i in range(0, 6):
#            newSet.f[i] = self.makeSet()
        newSet.minX = self.makeSet()
        newSet.minY = self.makeSet()
        newSet.minZ = self.makeSet()
        newSet.maxX = self.makeSet()
        newSet.maxY = self.makeSet()
        newSet.maxZ = self.makeSet()


        for boxXI in range(0, nBoxes[0]):
            for boxYI in range(0, nBoxes[1]):
                for boxZI in range(0, nBoxes[2]):
                    originI = np.array(origin) + boxSize * [boxXI, boxYI, boxZI]
                    boxI = self.makeBoxDXDYDZ(originI, boxSize, boxDiv)
                    newSet.add(boxI)
                    if boxXI == 0:
                        newSet.minX.add(boxI.minX)
                    if boxYI == 0:
                        newSet.minY.add(boxI.minY)
                    if boxZI == 0:
                        newSet.minZ.add(boxI.minZ)
                    if boxXI == nBoxes[0]-1:
                        newSet.maxX.add(boxI.maxX)
                    if boxYI == nBoxes[1]-1:
                        newSet.maxY.add(boxI.maxY)
                    if boxZI == nBoxes[2]-1:
                        newSet.maxZ.add(boxI.maxZ)

        newSet.mergeAll()

        return newSet

    def makeBoxTwoPnt(self, pnt1, pnt2, div, name=None):
        return self.makeBigBox(pnt1, np.array(pnt2)-np.array(pnt1), div, name=name)

    def makeHeatsink(self, origin, dimension, n, fin_width, base_height, div, name=None):
        newSet = self.makeSet(name)

#        for i in range(0, 6):
#            newSet.f[i] = self.makeSet()
        newSet.minX = self.makeSet()
        newSet.minY = self.makeSet()
        newSet.minZ = self.makeSet()
        newSet.maxX = self.makeSet()
        newSet.maxY = self.makeSet()
        newSet.maxZ = self.makeSet()
        newSet.inside = self.makeSet()

        gap_width = (dimension[1] - n*fin_width)/(n-1)
        fin_height = dimension[2] - base_height

        fin_div = div[1]
        gap_div = int(fin_div/fin_width*gap_width)

        for finI in range(0, n):
            y_pos = finI*(gap_width + fin_width)
            fin_base = self.makeBoxDXDYDZ(
                [origin[0], origin[1] + y_pos, origin[2]],
                [dimension[0], fin_width, base_height],
                [div[0], fin_div, 2]
            )
            newSet.add(fin_base)
            newSet.minZ.add(fin_base.minZ)
            newSet.minX.add(fin_base.minX)
            newSet.maxX.add(fin_base.maxX)

            fin = self.makeBigBox(
                [origin[0], origin[1] + y_pos, origin[2] + base_height],
                [dimension[0], fin_width, fin_height],
                div
            )
            newSet.add(fin)
            newSet.maxZ.add(fin.maxZ)
            newSet.minX.add(fin.minX)
            newSet.maxX.add(fin.maxX)

            if finI > 0:
                base = self.makeBigBox(
                    [origin[0], origin[1] + y_pos - gap_width, origin[2]],
                    [dimension[0], gap_width, base_height],
                    [div[0], fin_div, 4]
                )
                newSet.add(base)
                newSet.minZ.add(base.minZ)
                newSet.minX.add(base.minX)
                newSet.maxX.add(base.maxX)
                newSet.inside.add(base.maxZ)
                if finI == n-1:
                    newSet.maxY.add(fin_base.maxY)
                    newSet.maxY.add(fin.maxY)
                    newSet.inside.add(fin.minY)
                else:
                    newSet.inside.add(fin.minY)
                    newSet.inside.add(fin.maxY)
            else:
                newSet.minY.add(fin_base.minY)
                newSet.minY.add(fin.minY)
                newSet.inside.add(fin.maxY)

        newSet.mergeAll()
        newSet.inside.down()

        return newSet

    def makeRing(self, origin, inner_radius, outer_radius, height, div=[2, 360, 2], name=None):
        newSet = self.makeSet(name)

        newSet.open()

        base = self.makePoint(origin[0]+inner_radius, origin[1], origin[2])
        base.translate([outer_radius-inner_radius, 0, 0], base, div[0])
        base.up()


        po = self.makePoint(origin[0], origin[1], origin[2])
        pz = self.makePoint(origin[0], origin[1], origin[2]+0.001)
        base.rotate(po, pz, 90, base, div[1]/4)
        base.up()

        base.rotate(po, pz, 90, base)
        base.up()
        base.rotate(po, pz, 180, base)
        base.up()

        base.mergeAll()

        top = self.makeSet()
        base.translate([0, 0, height], top, div[2])

        newSet.close()

        newSet.minZ = base
        newSet.maxZ = top

        return newSet


if __name__ == "__main__":
    c1 = Cgx()
#    p1 = c1.makePoint(0, 0, 0)
#    p1.translate([1, 0, 0], p1, div=2)
#    p2 = c1.makePoint(1, 0, 0)
#    l1 = c1.makeLine(p1, p2)
#
#    b1 = c1.makeBigBox([0,0,0], [1,1,1], [2,2,350])
#
#    b2 = c1.makeBoxTwoPnt([-1, -1, -1], [0, 0, 0], [2,2,350])

    h1 = c1.makeHeatsink([0., 0., 0.], [0.015, 0.042, 0.005], 10, .002, 0.0015, [4,4,4])
    s1 = c1.makeSet("minX")
    s2 = c1.makeSet("minY")
    s3 = c1.makeSet("minZ")
    s4 = c1.makeSet("maxX")
    s5 = c1.makeSet("maxY")
    s6 = c1.makeSet("maxZ")
    s7 = c1.makeSet("in")

    s1.add(h1.minX)
    s2.add(h1.minY)
    s3.add(h1.minZ)
    s4.add(h1.maxX)
    s5.add(h1.maxY)
    s6.add(h1.maxZ)
    s7.add(h1.inside)

    c1.write()
    c1.write('test.fbd')

