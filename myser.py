import serial
import io
import re
import time
import json
import logging
import atexit
import sys
import threading
from PyQt5 import QtGui, QtCore,  QtWidgets
# test comment master origin


def main_ui():
    try:
        if (len(sys.argv)>1):
            fp = open(sys.argv[1])
        else:
            fp = open('mypumps3.json')
        pump_config = json.load(fp)
        fp.close()
    except IOError:
        print ('config file not found')
        sys.exit(0)

    programs = {x['name']:x for x in pump_config['programs']}
    ser = serial.Serial(baudrate=19200,timeout=0.1,port='COM4')
    print(ser.is_open)

    pumps = []
    for c in pump_config['pumps']:
        pumps.append(pm.Pump(ser,c))

    app = QtWidgets.QApplication(sys.argv)
    ex = pc.PumpControl(ser,pumps,programs)
    ret = app.exec_()
    ex.t.cancel()
    sys.exit(ret)


def main_test(sleeptime=None):
    try:
        if (len(sys.argv)>1):
            fp = open(sys.argv[1])
        else:
            fp = open('mypumps1.json')
        pump_config = json.load(fp)
        fp.close()
    except IOError:
        print ('config file not found')
        sys.exit(0)

    ser = serial.Serial(baudrate=19200,timeout=0.1,port='COM4')
    print(ser.is_open)

    pumps = []
    for c in pump_config['pumps']:
        pumps.append(pm.Pump(ser,c))

    for p in pumps:
        p.setDirection('infuse')
        #p.run()


        p.sendCommand('PHN  1')
        p.sendCommand('FUN RAT')
        p.sendCommand('RAT {} {}'.format(str(10), 'UM'))
        p.sendCommand('VOL {}'.format(str(5)))
        p.sendCommand('DIR INF')
        # ('phase 2')

        p.sendCommand('PHN  2')
        p.sendCommand('FUN RAT')
        p.sendCommand('RAT {} {}'.format(str(150), 'UM'))
        p.sendCommand('VOL {}'.format(str(50)))
        p.sendCommand('DIR INF')
        # print('phase 3')

        p.sendCommand('PHN  3')
        p.sendCommand('FUN LOP 2')
        # print('phase 4')

        p.sendCommand('PHN  4')
        p.sendCommand('FUN STP')
        p.run()
    allrates = [[]]*3

    for l in range(30):# get rate
        for i,p in enumerate(pumps):
            allrates[i].append(p.getRate())   # (str(p.getAddress()) +' '+ str(p.getRate()))
        time.sleep(2)
    print(allrates)


        #print(p.getDirection())

    # if sleeptime is not None:
    #     print('running...')
    #     time.sleep(sleeptime)
    #     print('timer done')
    #     for p in pumps:
    #         print(p.getStatus())
    #         if p.getStatus() != 'halted':
    #             p.stop()
    #             print('I had to stop pump {} at exit.'.format(p.getAddress()))
    #     print('pump at ADR {} infused {}'.format(p.getAddress(),p.getInfused()))

    # ser.close()
    # print(ser.is_open)
    for p in pumps:
        p.stop()

    ser.close()

    return ser, pumps


if __name__ == '__main__':
    # from Pump import*
    # from PumpControl import*
    import Pump as pm
    import PumpControl as pc
    #main_test(10)
    main_ui()