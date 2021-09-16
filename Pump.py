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


log = logging.getLogger(__name__)

# (Error messages, taken from other project)

class PumpError(Exception):
    '''
    General pump error
    '''

    def __init__(self, code, mesg=None):
        self.code = code
        self.mesg = mesg

    def __str__(self):
        result = '%s\n\n%s' % (self._todo, self._mesg[self.code])
        if self.mesg is not None:
            result += ' ' + self.mesg
        return result

class PumpCommError(PumpError):
    '''
    Handles error messages resulting from problems with communication via the
    pump's serial port.
    '''

    _mesg = {
            # Actual codes returned by the pump
            ''      : 'Command is not recognized',
            'NA'    : 'Command is not currently applicable',
            'OOR'   : 'Command data is out of range',
            'COM'   : 'Invalid communications packet received',
            'IGN'   : 'Command ignored due to new phase start',
            # Custom codes
            'NR'    : 'No response from pump',
            'SER'   : 'Unable to open serial port',
            'UNK'   : 'Unknown error',
            }

    _todo = 'Unable to connect to pump.  Please ensure that no other ' + \
            'programs that utilize the pump are running and try ' + \
            'try power-cycling the entire system (rack and computer).'

class PumpHardwareError(PumpError):

    '''Handles errors specific to the pump hardware and firmware.'''

    _mesg = {
            'R'     : 'Pump was reset due to power interrupt',
            'S'     : 'Pump motor is stalled',
            'T'     : 'Safe mode communication time out',
            'E'     : 'Pumping program error',
            'O'     : 'Pumping program phase out of range',
            }

    _todo = 'Pump has reported an error.  Please check to ensure pump ' + \
            'motor is not over-extended and power-cycle the pump.'

class PumpUnitError(Exception):
    '''Occurs when the pump returns a value in an unexpected unit
    '''

    def __init__(self, expected, actual, cmd):
        self.expected = expected
        self.actual = actual
        self.cmd = cmd

    def __str__(self):
        mesg = '%s: Expected units in %s, receved %s'
        return mesg % (self.cmd, self.expected, self.actual)

#####################################################################
# Pump Class
#####################################################################

class Pump(object):
    '''
    Initiating a pump is done with a dictionary that contains any of 'rate,'diameter','rate-units', and 'address'. If any is missing, a default value is assigned. 
    For now I'm assuming only infusion.
    '''

    ETX = '\x03'    # End of packet transmission
    STX = '\x02'    # Start of packet transmission
    CR  = '\x0D'    # Carriage return

    DEFAULTS = dict(baudrate=19200, bytesize=8, parity='N',
            stopbits=1, timeout=.1, xonxoff=0, rtscts=0, writeTimeout=1,
            dsrdtr=None, interCharTimeout=None)

    STATUS = dict(I='infusing', W='withdrawing', S='halted', P='paused',
                  T='in timed pause', U='waiting for trigger', X='purging')

    RATE_UNIT = {'UM':'ul/min','MM':'ml/min','UH':'ul/h','MH':'ml/h'}
    VOL_UNIT = {'UL':'ul','ML':'ml'}

    DIR_MODE = {
        'INF': 'Infuse',
        'WDR': 'Withdraw',
        'REV': 'Reverse',
    }

    mmsg=''

    REV_DIR_MODE = dict((v, k) for k, v in DIR_MODE.items())

    _response = re.compile('\x02' + '(?P<address>\d+)' + \
                                 '(?P<status>[IWSPTUX]|A\?)' + \
                                 '(?P<data>.*)' + '\x03')
    _dispensed = re.compile('I(?P<infuse>[\.0-9]+)' + \
                            'W(?P<withdraw>[\.0-9]+)' + \
                            '(?P<units>[MLU]{2})')

    def __init__(self,ser,config,lock=None):
        mmsg = ''
        self._ser = ser
        self._lock = lock
        self._check_lock = lock is not None
        self._direction = None
        if 'rate' in config:
            self._rate = config['rate']
        else:
            self._rate = 10
        if 'diameter' in config:
            self._diameter = config['diameter']
        else:
            self._diameter = 14.3
        if 'rate-units' in config:
            self._rate_units = config['rate-units']
        else:
            self._rate_units = 'UM'
        if 'address' in config:
            self._address = config['address']
        else:
            self._address = 0
        if 'volume' in config:
            self._volume = config['volume']
        else:
            self._volume = 100
        if 'vol-units' in config:
            self._volume_unit = config['vol-units']
        else:
            self._volume_unit = 'UL'
        try:
            mmsg = self._write_read('AL 0')    # Turn audible alarm on. -- for some reason fails in some pumps.
            self._write_read('DIA ' + str(self._diameter))
            self._write_read('VOL ' + str(self._volume))
            self._write_read('VOL ' + self._volume_unit)
            self._write_read('RAT ' + str(self._rate) + ' ' + self._rate_units) #'UM') #
            print('Initialized pump {} {}'.format(self._address,mmsg))
            self._lastInfused = 0
            self._lastWithdrawn = 0
            self.resetDispensed()
            atexit.register(self.disconnect)

            #  ((self._read_check('DIA',_self.diameter),
            #         self._read_check('VOL',_self.volume),
            #         self._read_check('RAT',str(_self.rate)+self._rate_units)))
        except PumpHardwareError as e:
            # We want to trap and dispose of one very specific exception code,
            # 'R', which corresponds to a power interrupt.  This is almost
            # always returned when the pump is first powered on and initialized
            # so it really is not a concern to us.  The other error messages are
            # of concern so we reraise them..
            print('0 {} {}'.format(mmsg,self._address))
            if e.code != 'R':
                raise e
        except NameError as e:
            # Raised when it cannot find the global name 'SERIAL' (which
            # typically indicates a problem connecting to COM1).  Let's
            # translate this to a human-understandable error.
            print('1 {} {}'.format(mmsg,self._address))
            log.exception(e)
            raise PumpCommError('SER')

    def _write_read(self, cmd, check_lock=True):
        if check_lock and self._check_lock:
            self._lock.acquire()
        cmd = str(self._address) + ' ' + cmd + '\r'
        self._ser.write(cmd.encode('utf-8'))
        res=self._ser.readline()
        if res == '':
            raise PumpCommError('NR', cmd)
        match = self._response.match(res.decode('utf-8'))
        if match is None:
            raise PumpCommError('NR')
        if match.group('status') == 'A?':
            raise PumpHardwareError(match.group('data'), cmd)
        elif match.group('data').startswith('?'):
            print(match,match.group)
            raise PumpCommError(match.group('data')[1:], cmd)
        if check_lock and self._check_lock:
            self._lock.release()
        return match.groupdict()


    def sendCommand(self,cmd):
        '''send any command'''
        self._write_read(cmd,check_lock=False)

    def singlePhaseProgram(self,rat,vol,direction):
        """intended for runManual in PumpControl, takes rate,vol,dir"""
        self._lock.acquire()
        self._write_read('PHN  1', check_lock=False)
        self._write_read('FUN RAT',check_lock=False)
        self._write_read('RAT {} {}'.format(str(rat), 'UM'), check_lock=False)
        self._write_read('VOL {}'.format(str(vol)), check_lock=False)
        #self._write_read('DIR {}'.format(dir), check_lock=False) # dir must be 'inf' or 'wdr'
        #'DIR {}'.format(self.REV_DIR_MODE[direction])
        self._write_read('DIR {}'.format(self.REV_DIR_MODE[direction]), check_lock=False)

        self._write_read('PHN  2', check_lock=False)
        self._write_read('FUN STP', check_lock=False)

        #self._write_read('RUN', check_lock=False)
        self._lock.release()
        self._write_read('RUN', check_lock=True)

    def _read_check(self,ser, adr, cmd, value):
        cmd = str(self._address) + ' ' + cmd + '\r'
        res = self._write_read(cmd)
        if cmd =='DIS':
            res=_dispensed.match(res['data'].decode('utf-8'))
            res = res.groupdict()
            return(res[self._direction]==str(value))
        return(res['data']==str(value))


    def disconnect(self):
        ''' Stop pump and close serial port. Automatically called when Python exits. '''
        try:
            if self.getStatus() != 'halted':
                self.stop()
        finally:
            if self._ser.is_open:
                self._ser.close()
            return # Don't reraise error conditions, just quit silently     b b
    def run(self):
        ''' Starts the pump. '''
        self._write_read('RUN')
    def stop(self):
        ''' Stop the pump. Raises PumpError if the pump is already stopped. '''
        self._write_read('STP')
    def setDirection(self, direction):
        ''' Set direction of the pump. Valid directions are 'infuse', 'withdraw' and 'reverse'. '''
        self._direction = direction
        self._write_read('DIR {}'.format(self.REV_DIR_MODE[direction]))
    def getDirection(self):
        ''' Get current direction of the pump. Response will be either 'infuse' or 'withdraw'. '''
        return self.DIR_MODE[self._write_read('DIR')['data']]
    def getRate(self):
        ''' Get current rate of the pump. '''
        return self._write_read('RAT')['data']
        #self.DIR_MODE[self._write_read('RAT')['data']]
    def setRate(self, rate):
        ''' Set current rate of the pump. '''
        return self._write_read('RAT {} {}'.format(rate, self._rate_units))
    def setVolume(self, volume, unit=None):
        ''' Set current volume of the pump '''
        return self._write_read('VOL {}'.format(volume))
    def getVolume(self, unit=None):
        ''' Get current volume of the pump -- not tested'''
        if SIM: return
        return self._write_read('VOL')['data']

    def getDispensed(self,units = True):#, direction):
        res = self._dispensed.match(self._write_read('DIS')['data'])#.decode('utf-8'))
        res = res.groupdict()
        #print(res)
        if units:
            return res[self._direction.lower()]+res['units']
        else:
            return res[self._direction.lower()]

    def resetDispensed(self):
        ''' Reset dispense measures '''
        self._lastInfused   = 0
        self._lastWithdrawn = 0
        self._write_read('CLD INF')
        self._write_read('CLD WDR')
    def getInfused(self):
        ''' Get total volume withdrawn '''
        return self._getDispensed('infuse') + self._lastInfused
    def getWithdrawn(self):
        ''' Get total volume dispensed. '''
        return self._getDispensed('withdraw') + self._lastWithdrawn
    def setDiameter(self, diameter):
        ''' Set diameter (unit must be mm). '''
        self._lastInfused   += self._getDispensed('infuse'  )
        self._lastWithdrawn += self._getDispensed('withdraw')
        self._write_read('DIA {}'.format(diameter))
    def getDiameter(self):
        ''' Get diameter setting in mm. '''
        return self._write_read('DIA')
    def getAddress(self):
        ''' Get diameter setting in mm. '''
        return self._address
    # def getTTL(self):
    #     ''' Get status of TTL trigger. '''
    #     tr = self._write_read('IN 2')
    #     if tr in ['0','1']:
    #         data = bool(eval(tr))
    #     else:
    #         raise PumpCommError('', 'IN 2')

    # getStatus is tested
    def getStatus(self):
        return self.STATUS[self._write_read('')['status']]
    def setLock(self,lock):
        self._lock = lock
        self._check_lock = True
