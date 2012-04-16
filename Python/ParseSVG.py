#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      John
#
# Created:     08/02/2012
# Copyright:   (c) John 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from xml.dom.minidom import parse
from xml.dom import Node
import Drawing
import Tkinter
import tkFileDialog
import serial
import array

SVGPointRelative = 0
SVGPointAbsolute = 1

def DrawSVG():
    currPos = [0.0, 0.0]
    transform = array.array('f',[1, 0, 0, 0, 1, 0, 0, 0, 1])
    svgs = mainWindow.dom.getElementsByTagName("svg")
    for svg in svgs:
        currPos = ProcessTree(svg, currPos, transform)
    Drawing.Home(mainWindow.ser, currPos)

def ProcessTree(treeNode, currPos, transform):
    for child in treeNode.childNodes:
        if ((child.nodeType == Node.ELEMENT_NODE) and (child.nodeName.rstrip() == "g")):
            currPos = ProcessTree(child, currPos, UpdateTransform(child.getAttribute('transform'), transform))
        elif ((child.nodeType == Node.ELEMENT_NODE) and (child.nodeName.rstrip() == "path")):
            pass
            currPos = ProcessPath(child, currPos, UpdateTransform(child.getAttribute('transform'), transform))
    return currPos

def UpdateTransform(transString, transform):
    myTrans = array.array('f',[1,0,0,0,1,0,0,0,1])
    opsString = transString.split('(')
    if opsString[0] == "matrix":
        coords = opsString[1].split(',')
        myTrans[0] = float(coords[0])
        myTrans[1] = float(coords[2])
        myTrans[2] = float(coords[4])
        myTrans[3] = float(coords[1])
        myTrans[4] = float(coords[3])
        myTrans[5] = float(coords[5].rstrip(')'))
    elif opsString[0] == "translate":
        coords = opsString[1].split(',')
        myTrans[2] = float(coords[0])
        myTrans[5] = float(coords[1].rstrip(')'))
    elif opsString[0] == "scale":
        coords = opsString[1].split(',')
        myTrans[0] = float(coords[0])
        myTrans[4] = float(coords[1].rstrip(')'))
    elif opsString[0] == "rotate":
        pass
    elif opsString[0] == "skewX":
        pass
    elif opsString[0] == "skewY":
        pass
    return matrixMult(transform, myTrans)

def matrixMult(t1, t2):
    t3 = array.array('f',[0,0,0,0,0,0,0,0,0])
    t3[0] = t1[0]*t2[0]+t1[1]*t2[3]+t1[2]*t2[6]
    t3[1] = t1[0]*t2[1]+t1[1]*t2[4]+t1[2]*t2[7]
    t3[2] = t1[0]*t2[2]+t1[1]*t2[5]+t1[2]*t2[8]
    t3[3] = t1[3]*t2[0]+t1[4]*t2[3]+t1[5]*t2[6]
    t3[4] = t1[3]*t2[1]+t1[4]*t2[4]+t1[5]*t2[7]
    t3[5] = t1[3]*t2[2]+t1[4]*t2[5]+t1[5]*t2[8]
    t3[6] = t1[6]*t2[0]+t1[7]*t2[3]+t1[8]*t2[6]
    t3[7] = t1[6]*t2[1]+t1[7]*t2[4]+t1[8]*t2[7]
    t3[8] = t1[6]*t2[2]+t1[7]*t2[5]+t1[8]*t2[8]
    return t3

def ToTouple(string, matrix, absRelFlag):
    temptouple = [0.0, 0.0, 0.0]
    toupleOut = [0.0, 0.0]
    stringBits = string.split(',')
    temptouple[0] = float(stringBits[0])
    temptouple[1] = float(stringBits[1])
    temptouple[2] = absRelFlag
    toupleOut[0] = matrix[0]*temptouple[0]+matrix[1]*temptouple[1]+matrix[2]*temptouple[2]
    toupleOut[1] = matrix[3]*temptouple[0]+matrix[4]*temptouple[1]+matrix[5]*temptouple[2]
    return toupleOut

def AddTouple(t1, t2):
    t3 = [0.0, 0.0]
    t3[0] = t1[0] + t2[0]
    t3[1] = t1[1] + t2[1]
    return t3

def ProcessPath(path, currPos, transform):
    firstPoss = [0,0]
    lastCommand = ''
    pointData = path.attributes['d'].value
    points = pointData.split()
    i = 0
    while(i < len(points)):
        if points[i].isalpha():
            thisCommand = points[i]
            i += 1
        else:
            thisCommand = lastCommand
        print "---------- " + thisCommand + " ----------"
        print currPos
        if thisCommand == 'M':
            coords1 = ToTouple(points[i], transform, SVGPointAbsolute)
            print coords1
            currPos = Drawing.MoveTo(mainWindow.ser, currPos, coords1)
            firstPoss[0] = currPos[0]
            firstPoss[1] = currPos[1]
            i += 1
            lastCommand = 'L'
        elif thisCommand == 'L':
            coords1 = ToTouple(points[i], transform, SVGPointAbsolute)
            print coords1
            currPos = Drawing.LineTo(mainWindow.ser, currPos, coords1)
            i += 1
            lastCommand = 'L'
        elif thisCommand == 'm':
            if i == 1:
                coords1 = ToTouple(points[i], transform, SVGPointAbsolute)
            else:
                coords1 = AddTouple(ToTouple(points[i], transform, SVGPointRelative), currPos)
            print coords1
            currPos = Drawing.MoveTo(mainWindow.ser, currPos, coords1)
            firstPoss[0] = currPos[0]
            firstPoss[1] = currPos[1]
            i += 1
            lastCommand = 'l'
        elif thisCommand == 'l':
            coords1 = AddTouple(ToTouple(points[i], transform, SVGPointRelative), currPos)
            print coords1
            currPos = Drawing.LineTo(mainWindow.ser, currPos, coords1)
            i += 1
            lastCommand = 'l'
        elif thisCommand == 'c':
            coords1 = AddTouple(ToTouple(points[i], transform, SVGPointRelative), currPos)
            coords2 = AddTouple(ToTouple(points[i+1], transform, SVGPointRelative), currPos)
            coords3 = AddTouple(ToTouple(points[i+2], transform, SVGPointRelative), currPos)
            print coords1
            print coords2
            print coords3
            currPos = Drawing.CurveTo(mainWindow.ser, currPos, coords1, coords2, coords3)
            i += 3
            lastCommand = 'c'
        elif thisCommand == 'C':
            coords1 = ToTouple(points[i], transform, SVGPointAbsolute)
            coords2 = ToTouple(points[i+1], transform, SVGPointAbsolute)
            coords3 = ToTouple(points[i+2], transform, SVGPointAbsolute)
            print coords1
            print coords2
            print coords3
            currPos = Drawing.CurveTo(mainWindow.ser, currPos, coords1, coords2, coords3)
            i += 3
            lastCommand = 'C'
        elif thisCommand == 'z':
            print firstPoss
            currPos = Drawing.LineTo(mainWindow.ser, currPos, firstPoss)
            lastCommand = ''
        else:
            print "unrecongized command " + thisCommand
            i += 1
            lastCommand = ''
    return currPos

def AllDone():
    mainWindow.destroy()

def OpenFile():
    file = tkFileDialog.askopenfilename(initialdir="C:\\Documents and Settings\\John\\My Documents\\My Pictures")
    mainWindow.dom = parse(file)

def MainWindow():
    global mainWindow
    mainWindow = Tkinter.Tk()
    mainWindow.title("SVG Sketch")
    goButton = Tkinter.Button(mainWindow, text="Draw", command=DrawSVG)
    goButton.pack(side='left')
    mainWindow.go = goButton
    openButton = Tkinter.Button(mainWindow, text="Open", command=OpenFile)
    openButton.pack(side='left')
    mainWindow.opb = openButton
    stopButton = Tkinter.Button(mainWindow, text="Exit", command=AllDone)
    stopButton.pack(side='left')
    mainWindow.stop = stopButton
    mainWindow.ser = serial.Serial(0, 4800)

if __name__ == "__main__":
    MainWindow()
    mainWindow.mainloop()
