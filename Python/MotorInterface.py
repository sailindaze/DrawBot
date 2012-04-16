# The Arduino controller responds to 5 commands
# R - Take one step counter clockwise
# L - Take one step clockwise
# 0 - Deenergize all motor coils
# 1 - Energize motor coils
# P - Move the pen
#-------------------
# Each of these commands takes a second character parameter
# R, L, 0, and 1 take a motor number as the second character
# Looking at the front of the bot, 0 is the left motor and 1 the right
# so to move the right hand motor one step clockwise the command would be L1
# The P command takes an up/down parameter 1 is up and 0 is down
# Commands are not followed by any line terminator - just send the two characters
# The Arduino will respond with a '+' when the command is complete

import binascii
import time

__author__ = "John"
__date__ = "$Jul 31, 2011 11:28:21 AM$"
__comm_on__ = 1

DeltaLook = [['','02 02'],['02','02'],['02 02',''],['03','02'],['',''],['02','03'],['03 03',''],['03','03'],['','03 03']]

def Sleep(length):
    startTime = time.clock()
    while ((time.clock() - startTime) < length):
        pass

def PenUp(serialLink):
    if(__comm_on__):
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('03'))
        serialLink.write(binascii.unhexlify('02'))
        Sleep(.6)

def PenDown(serialLink):
    if(__comm_on__):
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('03'))
        serialLink.write(binascii.unhexlify('03'))
        Sleep(.6)

def MoveDelta(serialLink, dp):
    (dx, dy) = dp
    MotorsStep(serialLink, DeltaLook[(( int(dy) + 1 ) * 3 ) + int(dx) + 1])

def MotorsStep(serialLink, directions):
    foo = directions[0].split()
    for move in foo:
        if(__comm_on__):
            serialLink.write(binascii.unhexlify('80'))
            serialLink.write(binascii.unhexlify('02'))
            serialLink.write(binascii.unhexlify(move.strip()))
    foo = directions[1].split()
    for move in foo:
        if(__comm_on__):
            serialLink.write(binascii.unhexlify('80'))
            serialLink.write(binascii.unhexlify('01'))
            serialLink.write(binascii.unhexlify(move.strip()))

def MotorsOff(serialLink):
    if(__comm_on__):
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('01'))
        serialLink.write(binascii.unhexlify('01'))
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('02'))
        serialLink.write(binascii.unhexlify('01'))

def MotorsOn(serialLink):
    if(__comm_on__):
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('01'))
        serialLink.write(binascii.unhexlify('00'))
        serialLink.write(binascii.unhexlify('80'))
        serialLink.write(binascii.unhexlify('02'))
        serialLink.write(binascii.unhexlify('00'))

if __name__ == "__main__":
    print "Hello World"
