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
from PumpValve import PumpValve

# from Pump import *

#####################################################################
# GUI
#####################################################################

class PumpValveControl(QtWidgets.QWidget):

    syringes = {'1 ml BD':'4.699',
                '3 ml BD':'8.585',
                '10 ml BD':'14.60',
                '30ml BD':'21.59'}
   
    def __init__(self, ser, pumps, valves, prog_dict):
        super(PumpValveControl, self).__init__()
        self._ser = ser
        self._pumps = pumps
        self._valves = valves
        self._pv_units = []
        for j,(p,v) in enumerate(zip(pumps,valves)):
            self._pv_units.append(PumpValve(v, p, j))

        self._prog_dict = prog_dict
        self._update_status_time = 4
        self.initUI()
        
    def initUI(self):      
        
        # set grid layout
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        
        # setup two buttons along top
        # self.runbtn = QtWidgets.QPushButton('does nothing',self)
        # grid.addWidget(self.runbtn,1,2)
        # self.runbtn.setCheckable(True)
        # # self.runbtn.clicked.connect(self.run_update)
        #
        # self.stopbtn = QtWidgets.QPushButton('also nothing',self)
        # grid.addWidget(self.stopbtn,1,3)
        # self.stopbtn.setCheckable(False)
        # # self.stopbtn.clicked.connect(self.stop_all)

        # optional column labels
        grid.addWidget(QtWidgets.QLabel('Pump number'),2,0)
        grid.addWidget(QtWidgets.QLabel('Program'),2,1)
        grid.addWidget(QtWidgets.QLabel('Valve Port'),2,2)
        grid.addWidget(QtWidgets.QLabel('Direction'), 2, 3)
        grid.addWidget(QtWidgets.QLabel('Contents'),2,4)
        grid.addWidget(QtWidgets.QLabel('Volume ul'),2,5)
        grid.addWidget(QtWidgets.QLabel('Flow rate ul/min'), 2, 6)
        grid.addWidget(QtWidgets.QLabel('Cur rate ul/min'),2,7)
        grid.addWidget(QtWidgets.QLabel('vol dispensed'),2,8)
          
        # interate over pumps, adding a row for each
        self.mapper = QtCore.QSignalMapper(self) # programs
        self.portmapper = QtCore.QSignalMapper(self) # ports
        self.dirmapper = QtCore.QSignalMapper(self) # direction
        self.runmapper = QtCore.QSignalMapper(self)   # run program
        self.runmanmapper = QtCore.QSignalMapper(self) # run manual
        self.stopmapper = QtCore.QSignalMapper(self) # stop
        self.currflow = []
        self.voldis = []
        self.vol = []
        self.rates = []
        # self.prime_btns = dict()
        self.run_btns = []
        self.run_man_btns = []
        self.stop_btns = []

        self._prog = list(range(len(self._pumps)))
        self._port = list(range(len(self._valves)))
        self._dir = list(range(len(self._pumps)))

        self._pump_lock = threading.Lock()
        self._valve_lock = threading.Lock()

        for i,unit in enumerate(self._pv_units):
            unit.pump.setLock(self._pump_lock)
            unit.valve.setLock(self._valve_lock)
            row = 3+i
            
            # add pump number
            pumplab = QtWidgets.QLabel('Pump #{}'.format(unit.pump.getAddress()))
            pumplab.setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(pumplab,row,0)

            # # add syringe pulldown
            # combo = QtWidgets.QComboBox(self)
            # [combo.addItem(s) for s in sorted(PumpControl.syringes)]
            # self.mapper.setMapping(combo,i)
            # combo.activated.connect(self.mapper.map)
            # grid.addWidget(combo,row,1)

            # add programs pulldown
            # prog pulldown
            combo = QtWidgets.QComboBox(self)
            for prog in self._prog_dict:
                combo.addItem(prog)
            self.mapper.setMapping(combo,i)
            combo.activated.connect(self.mapper.map)
            grid.addWidget(combo,row,1)
            self.set_program(i)

            # add ports pulldown
            combo_port = QtWidgets.QComboBox(self)
            for p in range(8):
                combo_port.addItem(str(p+1))
            self.portmapper.setMapping(combo_port, i)
            combo_port.activated.connect(self.portmapper.map)
            grid.addWidget(combo_port, row, 2)
            self.set_port(i)

            # add direction pulldown
            combo_dir = QtWidgets.QComboBox(self)
            combo_dir.addItem('Infuse')
            combo_dir.addItem('Withdraw')
            self.dirmapper.setMapping(combo_dir, i)
            combo_dir.activated.connect(self.dirmapper.map)
            grid.addWidget(combo_dir, row, 3)
            self.set_dir(i)

            # add textbox to put syring contents
            grid.addWidget(QtWidgets.QLineEdit(),row,4)

            self.vol.append(QtWidgets.QLineEdit(self))
            grid.addWidget(self.vol[i],row,5)

            # add textbox to enter flow rates
            self.rates.append(QtWidgets.QLineEdit(self))
            grid.addWidget(self.rates[i],row,6)

            # add label to show current flow rates
            self.currflow.append(QtWidgets.QLabel(self))
            self.currflow[i].setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(self.currflow[i],row,7)

            # add label to show current flow rates
            self.voldis.append(QtWidgets.QLabel(self))
            self.voldis[i].setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(self.voldis[i], row, 8)

            # add run button
            btn = QtWidgets.QPushButton('Run Prog',self)
            btn.setCheckable(True)# makes the button toggleable
            self.runmapper.setMapping(btn,i)
            btn.clicked.connect(self.runmapper.map)
            grid.addWidget(btn,row,9)
            self.run_btns.append(btn)

            # add run manual button
            btn = QtWidgets.QPushButton('Run Man at port',self)
            btn.setCheckable(True)
            self.runmanmapper.setMapping(btn,i)
            btn.clicked.connect(self.runmanmapper.map)
            grid.addWidget(btn,row,10)
            self.run_man_btns.append(btn)


            # add stop button
            btn = QtWidgets.QPushButton('Stop',self)
            btn.setCheckable(False)# makes the button toggleable
            self.stopmapper.setMapping(btn,i)
            btn.clicked.connect(self.stopmapper.map)
            grid.addWidget(btn,row,11)
            self.stop_btns.append(btn)

            """
            # # add prime button
            # btn = QtWidgets.QPushButton('Prime',self)
            # btn.setCheckable(True)# makes the button toggleable
            # self.primemapper.setMapping(btn,i)
            # btn.clicked.connect(self.primemapper.map)
            # grid.addWidget(btn,row,8)
            # self.prime_btns[i] = btn
            """

        # mapper thing
        self.mapper.mapped.connect(self.set_program)
        self.portmapper.mapped.connect(self.set_port)
        self.dirmapper.mapped.connect(self.set_dir)
        self.runmapper.mapped.connect(self.run_pump_prog)
        self.runmanmapper.mapped.connect(self.run_pump_manual)
        self.stopmapper.mapped.connect(self.stop_pump)
         # self.primemapper.mapped.connect(self.prime_pumps)

        # set up the status bar
        self.curr_state = 'add later'
        self.statusbar = QtWidgets.QLabel(self)
        grid.addWidget(self.statusbar,1,4)
        self.statusbar.setText('Status: '+self.curr_state)

        # set up the error bar
        self.error_state = 'None'
        self.errorbar = QtWidgets.QLabel(self)
        grid.addWidget(self.errorbar,1,5)
        self.errorbar.setText('Error: '+self.error_state)
        
        # set up the last command bar
        self.commandbar = QtWidgets.QLabel(self)
        grid.addWidget(self.commandbar,row+1,0,1,4)
        
        # make the prime state: a set containing the priming pumps
        self.prime_state = set()

        #initialize: set all flow rates to zero
        # self.run_update()
        # self.stop_all()
        # [self.update_syringe(p) for p in self._pumps]
        self.commandbar.setText('where is this')

        # keyboard shortcuts
        # QtWidgets.QShortcut(QtGui.QKeySequence('Space'),self,self.stop_all)

        # format the page
        self.setLayout(grid)
        self.setWindowTitle('Pump Valve control')
        #self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint) # always on top
        self.show()

        serial_lock = threading.Lock()

        #  launch the thread here
        ## This is the end, __init__
        self.check_rates_loop()
        self.t = threading.Timer(self._update_status_time,self.check_rates_loop)
        self.t.start()

    def set_program(self, i):
        self._prog[i] = self.mapper.mapping(i).currentText()
        #self._prog_dict[]
        print('just change the program of pump {} to {}'.format(i,self._prog[i]))
    def set_port(self,i):
        self._port[i] = self.portmapper.mapping(i).currentText()
        self._pv_units[i].moveToPort(int(self._port[i]))
    def set_dir(self, i):
        self._dir[i] = self.dirmapper.mapping(i).currentText()
        self._pumps[i]._direction = self._dir[i]

    def set_vol(self,i): # must be reset the run command to take effect
        self._vol[i] = self.mappervol.mapping(i).currentText()

    def run_pump_prog(self, i):
        # temporary thing. this thing should actually run the program
        # still need to add check if volume written
        print('trying pump {} '.format(i))
        print(self.run_btns[i].isChecked())
        if self.run_btns[i].isChecked():
            if self.run_man_btns[i].isChecked():
                self.run_man_btns[i].setChecked(False)
                if self._pumps[i].getStatus() != 'halted':
                    self._pumps[i].stop()
                else:
                    print('pump halted but button is checked')
            print('I''m running pump {} '.format(i))
            # send seq of commands
            if self._prog[i] != 'pulse w/ w' and self._prog[i] != 'wash' and self._prog[i] != 'chai' and self._prog[i] != 'capstone':
                print('got to 1')
                this_prog = self._prog_dict[self._prog[i]]
                print('got to 2')
                volploop = this_prog['pulse rate'] * this_prog['pulse duration'] + this_prog['flow rate'] * this_prog['pulse frequency']
                print('got to 3')
                '''check to see if there is enough volume for a loop'''
                if int(str(self.vol[i].text())) <= volploop*2:
                    self.run_btns[i].setChecked(False)
                    self.error_state = 'pump {}: not enough vol for prog'.format(i)
                    self.errorbar.setText('Error: ' + self.error_state)
                    print('got to 3.5')
                else:
                    loops = round(int(str(self.vol[i].text()))/volploop) - 1
                    print('got to 4')
                    self._lock.acquire()
                    self._pumps[i].sendCommand('PHN  1')
                    self._pumps[i].sendCommand('FUN RAT')
                    self._pumps[i].sendCommand('RAT {} {}'.format(this_prog['pulse rate'],'UM'))
                    self._pumps[i].sendCommand('VOL {}'.format(this_prog['pulse rate'] * this_prog['pulse duration']))
                    self._pumps[i].sendCommand('DIR INF')
                #('phase 2')

                    self._pumps[i].sendCommand('PHN  2')
                    self._pumps[i].sendCommand('FUN RAT')
                    self._pumps[i].sendCommand('RAT {} {}'.format(this_prog['flow rate'],'UM'))
                    self._pumps[i].sendCommand('VOL {}'.format(this_prog['flow rate'] * this_prog['pulse frequency']))
                    self._pumps[i].sendCommand('DIR INF')
                #print('phase 3')

                    self._pumps[i].sendCommand('PHN  3')
                    self._pumps[i].sendCommand('FUN LOP {}'.format(loops))
                #print('phase 4')

                    self._pumps[i].sendCommand('PHN  4')
                    self._pumps[i].sendCommand('FUN STP')
                    self._lock.release()
                    self._pumps[i].run()

            elif self._prog[i] == 'pulse w/ w': ## not complete
                pasT = 3
                self._lock.acquire()

                self._pumps[i].sendCommand('PHN  1')
                self._pumps[i].sendCommand('FUN LPS')

                self._pumps[i].sendCommand('PHN  2')
                self._pumps[i].sendCommand('FUN PAS 60')

                self._pumps[i].sendCommand('PHN  3')
                self._pumps[i].sendCommand('FUN LOP 3') # loop the 60s pause 5 times

                self._pumps[i].sendCommand('PHN  4') # pulse flow 1
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(100), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(34)))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  5') # reg flow1
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(3), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(59)))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  6')  # pulse flow 2
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(100), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(34)))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  7')  # reg flow 2
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(3), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(59)))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  8')  # pulse flow 3
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(100), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(34)))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  9')  # reg flow 3
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(3), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(int(round(3*(19.5-pasT),0)))))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  10')
                self._pumps[i].sendCommand('FUN LOP 15')
                # print('phase 4')

                self._pumps[i].sendCommand('PHN  11')
                self._pumps[i].sendCommand('FUN STP')

                self._lock.release()
                self._pumps[i].run()

            elif self._prog[i] == 'chai':  ## not complete; good enough
                self._lock.acquire()
                print('got to 1')


                self._pumps[i].sendCommand('PHN  1')
                self._pumps[i].sendCommand('FUN LPS')
                print('got to 2')
                self._pumps[i].sendCommand('PHN  2')
                self._pumps[i].sendCommand('FUN LPS')

                print('got to 3')
                self._pumps[i].sendCommand('PHN  3') # phase 2-4 are pull species x
                print('')
                self._pumps[i].sendCommand('FUN RAT')
                print('got to 3.1')
                self._pumps[i].sendCommand('RAT 300 UM')
                print('got to 3.2')
                self._pumps[i].sendCommand('VOL 25')
                print('got to 3.3')
                self._pumps[i].sendCommand('DIR WDR')
                print('got to 4')
                self._pumps[i].sendCommand('PHN  4')
                self._pumps[i].sendCommand('FUN  BEP') # switch species valve here
                print('got to 5')

                self._pumps[i].sendCommand('PHN  5')
                self._pumps[i].sendCommand('FUN  PAS 10')

                self._pumps[i].sendCommand('PHN  6')
                self._pumps[i].sendCommand('FUN LOP 4') #4 species rotations

                self._pumps[i].sendCommand('PHN  7')
                self._pumps[i].sendCommand('FUN  BEP') # switch syringe valve here

                self._pumps[i].sendCommand('PHN  8')
                self._pumps[i].sendCommand('FUN  BEP')

                self._pumps[i].sendCommand('PHN  9')
                self._pumps[i].sendCommand('FUN  PAS 10')

                self._pumps[i].sendCommand('PHN  10')  # Infusing sequence of species
                self._pumps[i].sendCommand('FUN  RAT')
                self._pumps[i].sendCommand('RAT 20 UM')

                self._pumps[i].sendCommand('VOL 100')
                self._pumps[i].sendCommand('DIR inf')
                print('got to 10')

                self._pumps[i].sendCommand('PHN  11')
                self._pumps[i].sendCommand('FUN  BEP')  # finished round of infusing

                self._pumps[i].sendCommand('PHN  12')
                self._pumps[i].sendCommand('FUN  BEP')

                self._pumps[i].sendCommand('PHN  13')
                self._pumps[i].sendCommand('FUN  BEP')

                self._pumps[i].sendCommand('PHN  14')
                self._pumps[i].sendCommand('FUN  PAS 15')

                self._pumps[i].sendCommand('PHN  15')
                self._pumps[i].sendCommand('FUN LOP 5')

                self._pumps[i].sendCommand('PHN  16')
                self._pumps[i].sendCommand('FUN STP')
                print('got to 16')
                self._lock.release()

                self._pumps[i].run()
            elif self._prog[i] == 'capstone':  # not complete, hardcoded, not using json
                # totalVolume = 100 UL
                self._lock.acquire()
                bacteria1 = 25  # userinput
                bacteria2 = 25  # userinput
                bacteria3 = 50  # userinput
                volumeInc = 5  # userinput
                volume1 = bacteria1 / volumeInc
                volume2 = bacteria2 / volumeInc
                volume3 = bacteria3 / volumeInc
                rate1 = volume1 * 60
                rate2 = volume2 * 60
                rate3 = volume3 * 60
                #add total run volume
                print('got to 1')

                self._pumps[i].sendCommand('PHN  1')
                self._pumps[i].sendCommand('FUN LPS')

                self._pumps[i].sendCommand('PHN  2')
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(int(rate1)), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(int(volume1))))
                self._pumps[i].sendCommand('DIR WDR')

                self._pumps[i].sendCommand('PHN  3')
                self._pumps[i].sendCommand('FUN PAS 1')  # time is valve moving time?
                print('got to 2')
                self._pumps[i].sendCommand('PHN  4')
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(int(rate2)), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(int(volume2))))
                self._pumps[i].sendCommand('DIR WDR')

                self._pumps[i].sendCommand('PHN  5')
                self._pumps[i].sendCommand('FUN PAS 1')  # time is valve moving time?

                self._pumps[i].sendCommand('PHN  6')
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(int(rate3)), 'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(int(volume3))))
                self._pumps[i].sendCommand('DIR WDR')

                self._pumps[i].sendCommand('PHN  7')
                self._pumps[i].sendCommand('FUN PAS 1')  # time is valve moving time?

                self._pumps[i].sendCommand('PHN  8')
                self._pumps[i].sendCommand('FUN LOP 5')  # number of times u pull
                print('got to 3')

                self._pumps[i].sendCommand('PHN  9')
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT 20 UM')
                self._pumps[i].sendCommand('VOL 100')
                self._pumps[i].sendCommand('DIR INF')

                #add loop for total time scale

                self._pumps[i].sendCommand('PHN  10')
                self._pumps[i].sendCommand('FUN STP')

                self._lock.release()
                print('got to 4')
                self._pumps[i].run()
                print('got to 5')


            elif self._prog[i] == 'wash': # not complete, hardcoded, not using json
                #loopVol = pulseRate*pulseTime + flowRate*flowTime
                #loops = 10 # self.vole[i] / loopVol

                pasT = 3  #min
                self._lock.acquire()
                self._pumps[i].sendCommand('PHN  1')
                self._pumps[i].sendCommand('FUN RAT')
                self._pumps[i].sendCommand('RAT {} {}'.format(str(50),'UM'))
                self._pumps[i].sendCommand('VOL {}'.format(str(int(round(50*pasT,0)))))
                self._pumps[i].sendCommand('DIR INF')

                self._pumps[i].sendCommand('PHN  2')
                self._pumps[i].sendCommand('FUN LPS')

                self._pumps[i].sendCommand('PHN  3')
                self._pumps[i].sendCommand('FUN PAS 60') #change loop time

                self._pumps[i].sendCommand('PHN  4')
                self._pumps[i].sendCommand('FUN LOP 57') # loop the 60s pause 55 times

                self._pumps[i].sendCommand('PHN  5')
                self._pumps[i].sendCommand('FUN LOP 15') #15 hour loop

                self._pumps[i].sendCommand('PHN  6')
                self._pumps[i].sendCommand('FUN STP')
                self._lock.release()
                self._pumps[i].run()
            else:
                if self._pumps[i].getStatus() != 'halted':
                    self._pumps[i].stop()

        else:
            if self._pumps[i].getStatus() != 'halted':
                self._pumps[i].stop()

    def run_pump_manual(self, i): ## STILL NEED TO ADD: if there is not rate entered do nothing
        print('trying pump manual {} '.format(i))
        try:
            if int(self.vol[i].text()) == 0 or  self.vol[i].text() == '':
                raise ValueError
            if self.run_man_btns[i].isChecked():
                print('run man pump {}'.format(i))
                if self.run_btns[i].isChecked():
                    self.run_btns[i].setChecked(False)
                if self._pumps[i].getStatus() != 'halted':
                    self._pumps[i].stop()
                rate = str(self.rates[i].text())
                vol = str(self.vol[i].text())
                print('rate is {}'.format(rate)) #str(self.rates[i].text())))
                print('vol to dispense {}'.format(vol)) #str(self.vol[i].text())))
                self._valves[i].moveToPort(self._port[i])
                self._pumps[i].singlePhaseProgram(rate,vol,self._dir[i])
            else:
                if self._pumps[i].getStatus() != 'halted':
                    self._pumps[i].stop()
        except ValueError:
             self.error_state = 'volume  for pump {} must be a non zero int'.format(i)
             print('volume  for pump {} must be a non zero int'.format(i))
             self.run_man_btns[i].setChecked(False)
             self.errorbar.setText('Error: ' + self.error_state)

    def stop_pump(self, i):
        print('Trying to stop pump {} '.format(i))
        self.run_btns[i].setChecked(False)
        self.run_man_btns[i].setChecked(False)
        if self._pumps[i].getStatus() != 'halted':
            print('Stopping pump {} '.format(i))
            self._pumps[i].stop()
            #self.run_btns[i].setChecked(False)

    def check_rates_loop(self):
        for i,p in enumerate(self._pumps):
            #voldisp = p.get
            stat = p.getStatus()
            if stat != 'infusing' and stat != 'withdrawing':
                self.currflow[i].setText(str(0))
                self.run_man_btns[i].setChecked(False)
            else:
                self.currflow[i].setText(p.getRate())
                self.voldis[i].setText(p.getDispensed())
        self.t = threading.Timer(self._update_status_time,self.check_rates_loop)
        self.t.start()

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
    ser = serial.Serial(baudrate=19200,timeout=0.1,port='COM1')
    print(ser.is_open)

    pumps = []
    for c in pump_config['pumps']:
        pumps.append(Pump(ser,c))

    app = QtWidgets.QApplication(sys.argv)
    ex = PumpControl(ser,pumps,programs)
    ret = app.exec_()
    ex.t.cancel()
    sys.exit(ret)

