# This implements an algorithm to draw a raster line given the end points
# It does so without using floating point multiplication or division.
# The algorithm was developed by Jack E. Bresenham in 1962 at IBM.
# This implementation was written in Python by John A. Anderson in May 2011.
#
# The Python version implemented here takes four integers as parameters, and
# returns a list of tuples begining with the start point and ending with the
# end point. The body consists of all the interveining pixels on the line.
#
#  This is pseudo code for the algorithm, rhe setPixel funtion building the
#  output list.
#
#  function line(x0, y0, x1, y1)
#   dx := abs(x1-x0)
#   dy := abs(y1-y0)
#   if x0 < x1 then sx := 1 else sx := -1
#   if y0 < y1 then sy := 1 else sy := -1
#   err := dx-dy
#
#   loop
#     setPixel(x0,y0)
#     if x0 = x1 and y0 = y1 exit loop
#     e2 := 2*err
#     if e2 > -dy then
#       err := err - dy
#       x0 := x0 + sx
#     end if
#     if e2 <  dx then
#       err := err + dx
#       y0 := y0 + sy
#     end if
#   end loop

import math

__author__="John A. Anderson"
__date__ ="$May 24, 2011 4:24:39 PM$"

def get_line(spx, spy, epx, epy):
    line = []
    dx = abs(epx - spx)
    dy = abs(epy - spy)
    if (spx < epx):
        sx = 1
    else:
        sx = -1
    if (spy < epy):
        sy = 1
    else:
        sy = -1
    err = dx - dy
    while 1:
        line.append((spx, spy))
        if (abs(spx - epx) < 0.707) and (abs(spy - epy) < 0.707):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            spx += sx
        if e2 < dx:
            err += dx
            spy += sy
    return line

def get_deltas(spx, spy, epx, epy):
    line = []
    dx = abs(epx - spx)
    dy = abs(epy - spy)
    if (spx < epx):
        sx = 1
    else:
        sx = -1
    if (spy < epy):
        sy = 1
    else:
        sy = -1
    err = dx - dy
    while 1:
        oldx = spx
        oldy = spy
        if math.sqrt(((spx - epx) * (spx - epx)) + ((spy - epy) * (spy - epy))) < 1.0:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            spx += sx
        if e2 < dx:
            err += dx
            spy += sy
        line.append((spx-oldx, spy-oldy))
    return line

if __name__ == "__main__":
    print get_deltas(0, 0, 3.3333333, 7.536888473762)
