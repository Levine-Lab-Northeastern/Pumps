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
from PV_seq_script import *
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
        self._update_status_time = 3
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
        #grid.addWidget(QtWidgets.QLabel('vol dispensed'),2,9)
          
        # interate over pumps, adding a row for each
        self.mapper = QtCore.QSignalMapper(self) # programs
        self.portmapper = QtCore.QSignalMapper(self) # ports
        self.dirmapper = QtCore.QSignalMapper(self) # direction
        self.runmapper = QtCore.QSignalMapper(self)   # run program
        self.runmanmapper = QtCore.QSignalMapper(self) # run manual
        self.stopmapper = QtCore.QSignalMapper(self) # stop
        self.dir_pulldown = []
        self.ports_pulldown = []
        self.currflow = []
        self.voldis = []
        self.vol = []
        self.rates = []
        self.unitPhase = []
        self.unitPhaseVolRemainder = []
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
            row = 3+2*i
            
            # add pump number
            pumplab = QtWidgets.QLabel('Pump #{}'.format(unit.pump.getAddress()))
            pumplab.setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(pumplab,row,0)

            # add label to show the current phase
            self.unitPhase.append(QtWidgets.QLabel(self))
            self.unitPhase[i].setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(self.unitPhase[i], row+1, 0,1,2)

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

            # label to show the remainder volume in phase
            self.unitPhaseVolRemainder.append(QtWidgets.QLabel(self))
            self.unitPhaseVolRemainder[i].setAlignment(QtCore.Qt.AlignHCenter)
            grid.addWidget(self.unitPhaseVolRemainder[i], row + 1, 3)

            # add ports pulldown
            combo_port = QtWidgets.QComboBox(self)
            for p in range(8):
                combo_port.addItem(str(p+1))
            self.ports_pulldown.append(combo_port)
            self.portmapper.setMapping(combo_port, i)
            combo_port.activated.connect(self.portmapper.map)
            grid.addWidget(combo_port, row, 2)
            self.set_port(i)

            # add direction pulldown
            combo_dir = QtWidgets.QComboBox(self)
            combo_dir.addItem('Infuse')
            combo_dir.addItem('Withdraw')
            self.dir_pulldown.append(combo_dir)
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
        self.curr_state = ''
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
        grid.addWidget(self.commandbar,row+2,0,1,4)
        
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
        #self.check_rates_loop()
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
        entry_params = {"port": self._port[i], "rate": self.rates[i].text(),"vol": self.vol[i].text(), "dir": self._dir[i]}
        print('entry params {}'.format(entry_params))
        print('trying pump {} '.format(i))
        print(self.run_btns[i].isChecked())
        if self.run_btns[i].isChecked():
            if self.run_man_btns[i].isChecked():
                self.run_man_btns[i].setChecked(False)
                if self._pumps[i].getStatus() != 'halted':
                    self._pumps[i].stop()
                else:
                    print('pump halted but button is checked')
            print('starting program on unit {} '.format(i))
            # send seq of commands
            if self._prog_dict[self._prog[i]]["type"] == "pumpValve":
                self._pv_units[i].runSequence(self._prog_dict[self._prog[i]], entry_params)

            elif self._prog_dict[self._prog[i]]["type"] == "pumpOnly":
            #
            # if self._prog[i] == 'sequence':
            #     print("starting PV sequence")
            #     self._pv_units[i].runSequence(self._prog_dict[self._prog[i]])
            #
            # if self._prog[i] == 'seq fill400':
            #     print("starting PV2 sequence")
            #     self._pv_units[i].runSequence(self._prog_dict[self._prog[i]])
            #
            # if self._prog[i] == 'Pull bleach wash':
            #     print("starting wash sequence")
            #     self._pv_units[i].runSequence(self._prog_dict[self._prog[i]])
            #
            # if self._prog[i] == 'prime port':
            #     print("starting seq: {} {}".format(self._prog_dict[self._prog[i]],self._port[i]))
            #     self._pv_units[i].runSequence(self._prog_dict[self._prog[i]], entry_params)
            #
            # if self._prog[i] == 'dir vol rat all ports':
            #     print("starting seq: {}".format(self._prog[i]))
            #     self._pv_units[i].runSequence(self._prog_dict[self._prog[i]], entry_params)
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
                    print('Not enough vol entered for a loop')
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

            elif self._prog_dict[self._prog[i]]["type"] == "python code":
                #getattr(self._pv_units[i], self._prog_dict[self._prog[i]]["name"])()
                # test_script(self._pv_units[i],self._prog_dict[self._prog[i]]["Params"])
                # print(self._prog_dict[self._prog[i]]["name"])
                # #locals()[self._prog_dict[self._prog[i]]["name"]](self._pv_units[i],self._prog_dict[self._prog[i]]["Params"])
                # print('got here')
                #params = self._prog_dict[self._prog[i]]["Params"]
                #_7_port_wash(self._pv_units[i], self._prog_dict[self._prog[i]]["Params"])
                eval(self._prog_dict[self._prog[i]]["name"] + '(self._pv_units[i],self._prog_dict[self._prog[i]]["Params"])')

                # this calls locals()['funcName'](paramsForFunc)
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
                #self._valves[i].moveToPort(self._port[i])
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
        if self._pumps[i].getStatus() != 'halted' or self._pv_units[i].running_seq:
            print('Stopping pump {} '.format(i))
            self._pumps[i].stop()
            if self._pv_units[i].running_seq:
                self._pv_units[i].thread_kill.set()
            #self.run_btns[i].setChecked(False)

    def check_rates_loop(self):
        for i,um in enumerate(self._pv_units):
            pump_status = um.pump.getStatus()
            if not um.running_seq and pump_status != 'infusing' and pump_status != 'withdrawing':
                self.currflow[i].setText(str(0))
                self.run_man_btns[i].setChecked(False)
                self.run_btns[i].setChecked(False)
                self.unitPhase[i].setText('')
                self.unitPhaseVolRemainder[i].setText("V remain"+str(int(um.phaseTargetDispense-float(um.pump.getDispensed(units = False)))))

            elif um.running_seq:
                if pump_status == 'infusing' or pump_status == 'withdrawing':
                    self.dir_pulldown[i].setCurrentText(str(um.pump.getDirection()))
                    self.currflow[i].setText(um.pump.getRate())
                self.ports_pulldown[i].setCurrentText(str(um.valve.current_port))
                self.voldis[i].setText(um.pump.getDispensed())
                self.unitPhase[i].setText(str(um.current_phase))
                self.unitPhaseVolRemainder[i].setText("V remain"+str(int(um.phaseTargetDispense-float(um.pump.getDispensed(units = False)))))

            else:
                self.currflow[i].setText(um.pump.getRate())
                self.voldis[i].setText(um.pump.getDispensed())
                self.unitPhase[i].setText(um.current_phase)
                #print("4424245"+ um.current_phase)
        self.t = threading.Timer(self._update_status_time,self.check_rates_loop)
        self.t.start()

# def main_ui():
#     try:
#         if (len(sys.argv)>1):
#             fp = open(sys.argv[1])
#         else:
#             fp = open('mypumps3.json')
#         pump_config = json.load(fp)
#         fp.close()
#     except IOError:
#         print ('config file not found')
#         sys.exit(0)
#
#     programs = {x['name']:x for x in pump_config['programs']}
#     ser = serial.Serial(baudrate=19200,timeout=0.1,port='COM1')
#     print(ser.is_open)
#
#     pumps = []
#     for c in pump_config['pumps']:
#         pumps.append(Pump(ser,c))
#
#     app = QtWidgets.QApplication(sys.argv)
#     ex = PumpControl(ser,pumps,programs)
#     ret = app.exec_()
#     ex.t.cancel()
#     sys.exit(ret)

