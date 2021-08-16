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
# test comment for valves1/origin


def main_ui():
    try:
        if (len(sys.argv)>1):
            fp = open(sys.argv[1])
        else:
            fp = open('mypumps1.json')
            pc = open('myprograms.json')
            main = open('main_config.json')
        pump_config = json.load(fp)
        prog_config = json.load(pc)
        main_config = json.load(main)
        fp.close()
        pc.close()
        main.close()
    except IOError:
        print ('config file not found')
        sys.exit(0)
    """Init pumps"""
    programs = {x['name']:x for x in prog_config['programs']}
    pumpPort = main_config["PumpCOM"]
    ser = serial.Serial(baudrate=19200,timeout=0.1,port=pumpPort) # com 1 for scope comp, com 4 for bench comp
    print(ser.is_open)


    pumpsdict = {}
    for p in range(main_config['NumPumps']):
        pump = main_config["Pumps"][p]
        pumpsdict[pump["address"]] = pm.Pump(ser,pump)

    # for c in pump_config['pumps']:
    #     pumps.append(pm.Pump(ser,c))

    """Init the labsmith objects """
    valvePort = main_config["ValveCOM"]
    eib = ls.EIB200(COM=5) # com 5 for bench comp

    valves = []
    PVunits = []
    for v in range(main_config["NumValves"]):
        valve = main_config["Valves"][v]
        valves.append(ls.Valve(eib.ls4vm,channel = valve["ValveChannel"]))
    print(valves)
        # init pv unit here
        #PVunits.append(PumpValve.PumpValve(valves[-1],pumpsdict[valves["pumpADR"]]))

    #valves_COM_lock = threading.Lock()
    #pumps_COM_lock = threading.Lock()
    #myValve1 = ls.Valve(eib.ls4vm, channel = 1)#, lock=valves_COM_lock)
    #myValve2 = ls.Valve(eib.ls4vm, channel = 2)
    #valves = [myValve1]#,myValve2]

    #print('valves', valves)
    """need to create a list of units: pv units and solo pumps"""
    app = QtWidgets.QApplication(sys.argv)
    ex = pvc.PumpValveControl(ser,pumpsdict.values(),valves,programs)
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


    for p in pumps:
        p.stop()

    ser.close()

    return ser, pumps


def testvalve():
    """open the json"""
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

    """Open serial port to pumps and init pump objects"""
    ser = serial.Serial(baudrate=19200,timeout=0.1,port='COM4')
    print(ser.is_open)

    pumps = []
    for c in pump_config['pumps']:
        pumps.append(pm.Pump(ser,c))
    """Init the labsmith objects """
    eib = ls.EIB200(COM = 5)

    valves_COM_lock = threading.Lock()
    pumps_COM_lock = threading.Lock()

    myPump1 = pumps[0]
    myPump1.setLock(pumps_COM_lock)
    myValve1 = ls.Valve(eib.ls4vm,channel = 1, lock = valves_COM_lock)
    myPV1 = PumpValve(myValve1,myPump1,1)


    """run the test"""
    myPV1.moveToPort(7)
    myPV1.runPumpPhase(100,100,'Infuse')

    #pumps[2].singlePhaseProgram(100,200,'Withdraw')



if __name__ == '__main__':
    # from Pump import*
    # from PumpControl import*
    import Pump as pm
    import PumpValveControl as pvc

    import labsmith as ls
    import PumpValve
    import threading
    from PumpValve import PumpValve
    #main_test(10)
    main_ui()

    #print(sys.argv[0])


    #testvalve()