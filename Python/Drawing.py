#
#

import MotorInterface
import LineDraw

__author__="John"
__date__ ="$Aug 9, 2011 5:08:47 PM$"

def Home(ser, start):
    MoveTo(ser, start, [0.0, 0.0])
    MotorInterface.MotorsOff(ser)

def MoveTo(ser, start, end):
    penPosition = start
    MotorInterface.PenUp(ser)
    steps = LineDraw.get_deltas(start[0], start[1], end[0], end[1])
    for delta in steps:
        MotorInterface.MoveDelta(ser, delta)
        penPosition[0] += delta[0]
        penPosition[1] += delta[1]
    if ((end[0] != 0) or (end[1] != 0)):
        MotorInterface.PenDown(ser)
    return penPosition

def LineTo(ser, start, end):
    penPosition = start
    steps = LineDraw.get_deltas(start[0], start[1], end[0], end[1])
    for delta in steps:
        MotorInterface.MoveDelta(ser, delta)
        penPosition[0] += delta[0]
        penPosition[1] += delta[1]
    return penPosition

def CurveTo(ser, start, cp1, cp2, end):
    penPosition = start
    t = 0.05
    while t < 1.01:
        currX = end[0]*(t**3) + 3*cp2[0]*((t**2)*(1-t)) + 3*cp1[0]*(t*((1-t)**2)) + start[0]*((1-t)**3)
        currY = end[1]*(t**3) + 3*cp2[1]*((t**2)*(1-t)) + 3*cp1[1]*(t*((1-t)**2)) + start[1]*((1-t)**3)
        steps = LineDraw.get_deltas(penPosition[0], penPosition[1], currX, currY)
        for delta in steps:
            MotorInterface.MoveDelta(ser, delta)
            penPosition[0] += delta[0]
            penPosition[1] += delta[1]
        t += .05
    return penPosition

if __name__ == "__main__":
    import serial
    foo = serial.Serial(0,4800)
    CurveTo(foo,[2585.8226, -158.20096000000001],[2746.6637999999998, -142.48086000000001],[2339.9112, 71.679393000000005],[2617.1536999999998, 59.412586000000005])