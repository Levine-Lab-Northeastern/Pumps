import threading
import datetime

import json
import math



def twoPulseType(PV,params):
    """Runs program for the pump valve unit using complex script here,
            launches a new thread that sends a sequence of RunAtPort commands
            and sleeps for the expected pump run time in between"""
    #self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """Loop 2x
            1.1)withdraw loading material + extra loaded
            1.2)infuse extra to waste
            1.3)infuse low pulse (30s)
            1.4)infuse slow flow (19.5 min)
            1.5)infuse to waste
           Loop 1x
            2.1)withdraw loading material + extra loaded
            2.2)infuse extra to waste
            2.3)infuse HIGH pulse (60s)
            2.4)infuse slow flow (19 min)
            2.5)infuse to waste"""

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 6:
                flag = RunAtPort_threadCheck(_PV, p=3, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=100, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            """40 min to 60 min"""
            flag = True
            i = 0
            while flag and i < 48:
                flag = RunAtPort_threadCheck(_PV, p=4, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=100, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def wash_7_port(PV,params):
    """Runs program for the pump valve unit using complex script here,
            launches a new thread that sends a sequence of RunAtPort commands
            and sleeps for the expected pump run time in between

            6 times pull 1ml from all ports exept 6 then dispense to port 6"""
    print('made it into script')
    #self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        print('made it into thread')
        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60)) +4 # added 4 sec to stabilize the flow before moving the valve
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 2:
                flag = RunAtPort_threadCheck(_PV, p=1, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=3, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=4, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=5, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=7, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=800, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=800, v=6800, d='Infuse')


                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()


def Pluronic_4d(PV,params):
    """loads 200ul and dispenses 50ul/min/device 20 times, then washes with s-media 1.5ml at 100ul/min/device"""

    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        """pluronic wash section"""
        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=1000, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=20, v=1000, d='Infuse')
                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()


def Pluronic_4d_p6(PV,params):
    """loads 200ul and dispenses 50ul/min/device 20 times, then washes with s-media 1.5ml at 100ul/min/device"""

    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        """pluronic wash section"""
        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=6, r=200, v=1000, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=20, v=1000, d='Infuse')
                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def p_4d_op50(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 5 = ~1min x 5  = ~ 5min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=2, r=500, v=200, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=400, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=500, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=500, v=50, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()
def p_2d_op50(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 5 = ~1min x 5  = ~ 5min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=2, r=400, v=200, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=200, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=400, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=400, v=50, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def S_wash_4d(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 6:
                flag = RunAtPort_threadCheck(_PV, p=2, r=500, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=500, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=500, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=500, v=50, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def op50(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 20:
                flag = RunAtPort_threadCheck(_PV, p=6, r=75, v=75, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=100, d='Infuse')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def op50flow(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 31:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=8, v=60, d='Infuse')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def op50flow_16f_200p(PV,params):
    ## todo fix the name because the flow program has been changed

    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 25:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=16, v=320, d='Infuse')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def op50flow_p6(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 20:
                flag = RunAtPort_threadCheck(_PV, p=6, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=12, v=60, d='Infuse')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def one_bact_flow(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
                # params['hours']
        for hour in range(12):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=84, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=384, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=8, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()


def matt420(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        def wait_(_PV, time):
            _PV.thread_kill.wait(timeout=time*60)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            return True
                # params['hours']
        for hour in range(14):
            flag = True
            i = 0
            while flag and i < 1:

                flag = RunAtPort_threadCheck(_PV, p=7, r=500, v=500, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=500, d='Infuse') and \
                       wait_(_PV,12.5) and\
                       RunAtPort_threadCheck(_PV, p=4, r=500, v=500, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=5, r=500, v=1100, d='Withdraw') and \
                       wait_(_PV, 5.5) and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=600, d='Infuse')

            i += 1
            if _PV.thread_kill.is_set():
                break

            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=8, r=500, v=500, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=500, d='Infuse') and \
                       wait_(_PV, 12.5) and \
                       RunAtPort_threadCheck(_PV, p=4, r=500, v=500, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=5, r=500, v=1100, d='Withdraw') and \
                       wait_(_PV, 5.5) and \
                       RunAtPort_threadCheck(_PV, p=2, r=50, v=600, d='Infuse')

            i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def two_bact_flow(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(10):
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=260, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()


def two_bact_flow_sync_s2(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(10):
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=260, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break


        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()


def one_bact_wdr_flow_sync(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(12):
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=8, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def one_bact_wdr_flow_sync_s2(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(10):
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\s2_wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def one_bact_switch_wdr_sync_78(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']

        for h in range(3):
            hour = h+2
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\prog_78_wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        flag = True
        i = 0
        while flag and i < 1:
            flag = RunAtPort_threadCheck(_PV, p=5, r=800, v=1000, d='Infuse') and \
                   RunAtPort_threadCheck(_PV, p=4, r=800, v=1000, d='Withdraw')
            i += 1

        for h in range(7):

            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=8, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            hour = h + 5
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\prog_78_wash_num_{}.txt'.format(hour),
                      'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()
def one_bact_switch_wdr_sync_87(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']

        for h in range(3):
            hour = h+2

            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=8, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\prog_87_wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        flag = True
        i = 0
        while flag and i < 1:
            flag = RunAtPort_threadCheck(_PV, p=5, r=800, v=1000, d='Infuse') and \
                   RunAtPort_threadCheck(_PV, p=4, r=800, v=1000, d='Withdraw')
            i += 1

        for h in range(7):
            hour = h+5

            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\prog_87_wash_num_{}.txt'.format(hour), 'x') as f:
                f.write('Create a new text file!')
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def one_bact_wdr_flow(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(10):
            #with open(r'C:\Users\LevineLab\Documents\python notebooks\file_com\wash_num_{}.txt'.format(hour), 'x') as f:
                #f.write('Create a new text file!')

            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=8, r=300, v=300, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=48, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=600, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=300, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=600, v=360, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def wdr_prime_8ports(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(1):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=1, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=2, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=3, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=4, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=4, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=5, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=5, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=7, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=500, v=1000, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=500, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=8, r=500, v=1000, d='Withdraw')


                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()
def wdr_2_bact_2_dev(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(6):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=1, r=200, v=100, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=8, v=80, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=7, r=200, v=100, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=7, r=12, v=54, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=200, v=100, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=12, v=54, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def wdr_1_bact_4_dev(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
                return True
                # params['hours']
        for hour in range(6):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=1, r=200, v=100, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=8, v=40, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 11:
                flag = RunAtPort_threadCheck(_PV, p=8, r=200, v=100, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=8, r=12, v=54, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def two_bact_flow_wash(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        #params['hours']
        for hour in range(16):
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=6, r=200, v=300, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=10, v=120, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=8, r=200, v=300, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            flag = True
            i = 0
            while flag and i < 4:
                flag = RunAtPort_threadCheck(_PV, p=3, r=200, v=125, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=4, r=200, v=125, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=5, r=200, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=50, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=12, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=50, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=200, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=8, r=200, v=100, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()
def Overnight(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+4
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 9:
                flag = RunAtPort_threadCheck(_PV, p=6, r=200, v=500, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=20, v=1000, d='Infuse')
                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()
def two_bact_simp(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+6
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 3:
                flag = RunAtPort_threadCheck(_PV, p=3, r=200, v=125, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=4, r=200, v=125, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=5, r=200, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=50, v=150, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=200, v=200, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=200, v=100, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def no_valve_2d(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))+6
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True

        for hour in range(params['hours']):
            flag = True
            i = 0
            while flag and i < 30:
                flag = RunAtPort_threadCheck(_PV, p=6, r=150, v=150, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=6, v=120, d='Infuse')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def jub39_r_switch_g(PV,params):
    """Runs program for the pump valve unit using complex script here,
                launches a new thread that sends a sequence of RunAtPort commands
                and sleeps for the expected pump run time in between"""
    # self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeqScript(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        """ Loop 20 = ~1.5min x 20  = ~ 30min
            1.1)withdraw loading material
            1.2)infuse to device
            1.3)infuse to waste
            1.4)withdraw buffer
            """

        def RunAtPort_threadCheck(_PV, p, r, v, d):
            _PV.RunAtPort(p, r, v, d)
            expect_time = int(int(v) / (int(r) / 60))
            _PV.thread_kill.wait(timeout=expect_time)
            if _PV.thread_kill.is_set():
                print("killing thread inner")
                return False
            pump_Running = True
            while pump_Running:
                status = _PV.pump.getStatus()
                if status == 'halted':
                    pump_Running = False
            return True
        for hour in range(4):
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=3, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=100, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            """40 min to 60 min"""
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=3, r=300, v=250, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        for hour in range(8):
            flag = True
            i = 0
            while flag and i < 5:
                flag = RunAtPort_threadCheck(_PV, p=4, r=300, v=150, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=100, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            """40 min to 60 min"""
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=4, r=300, v=250, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=6, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=6, r=5, v=50, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=7, r=100, v=25, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeqScript, args=(PV, params))
    PV.k.start()

def prog_from_json1(PV,params):
    """there a re 3 types of steps.
    'make_schedule': will read the list of cycle times, note the current time and make a file with the schedule
        for each cycle given the current start time.
    'notify': will write a line to a file noting what whash cycle it is now starting
    'pvflow': will send code to pumps valves"""
    PV.running_seq = True

    def runStep_threadCheck(_PV,step_dict):
        log_fname = 'pump_{}_prog_log.txt'.format(_PV.pvADR)
        with open(log_fname, 'a') as file:
            file.write('{} {}\n'.format(datetime.datetime.now(),step_dict))
        if step_dict['type'] == 'make_schedule':
            now = datetime.datetime.now()
            for delta_t in step_dict['cycle_times']:
                now = now + datetime.timedelta(minutes = float(delta_t))
                fname = '{}_{}.txt'.format(step_dict['file_name'],_PV.pvADR)
                with open(fname, 'a') as file:
                    file.write('{} \n'.format(now))
        elif step_dict['type'] == 'notify':
            fname = '{}_{}.txt'.format(step_dict['com_file'],_PV.pvADR)
            with open(fname, 'a') as file:
                file.write('{} notify_step: {}\n'.format(datetime.datetime.now(),step_dict['message']))
        elif step_dict['type'] == 'pvflow':
            _PV.RunAtPort(port = step_dict['p'], rat = step_dict['r'], vol = step_dict['v'], direction = step_dict['d'])
            expect_time = math.ceil(int(step_dict['v']) / int(step_dict['r']) * 60) +int(step_dict['post_wait'])
            _PV.thread_kill.wait(timeout=expect_time)

        if _PV.thread_kill.is_set():
            print("killing thread inner")
            return False
        pump_Running = True
        while pump_Running:
            status = _PV.pump.getStatus()
            if status == 'halted':
                pump_Running = False
        return True

    def runSeqScript(_PV,seq_list):
        flag = True
        step_num = 0
        while flag and step_num < len(seq_list):
            flag = runStep_threadCheck(_PV, sequence_steps[step_num])
            step_num += 1
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    with open(params['file_path'], 'r') as f:
        prog_dict = json.load(f)
    sequence_steps = prog_dict['sequence_steps']
    if len(sequence_steps)>0:
        PV.thread_kill = threading.Event()
        PV.k = threading.Thread(target=runSeqScript, args=(PV, sequence_steps))
        PV.k.start()
    else:
        print('seq length 0')

def prog_from_json2(PV,params):
    """there a re 3 types of steps.
    'make_schedule': will read the list of cycle times, note the current time and make a file with the schedule
        for each cycle given the current start time.
    'notify': will write a line to a file noting what whash cycle it is now starting
    'pvflow': will send code to pumps valves"""
    PV.running_seq = True

    def runStep_threadCheck(_PV,step_dict):
        log_fname = 'pump_{}_prog_log.txt'.format(_PV.pvADR)
        with open(log_fname, 'a') as file:
            file.write('{} {}\n'.format(datetime.datetime.now(), step_dict))
        if step_dict['type'] == 'make_schedule':
            now = datetime.datetime.now()
            for delta_t in step_dict['cycle_times']:
                now = now + datetime.timedelta(minutes = float(delta_t))
                fname = '{}_{}.txt'.format(step_dict['file_name'],_PV.pvADR)
                with open(fname, 'a') as file:
                    file.write('{} \n'.format(now))
        elif step_dict['type'] == 'notify':
            fname = '{}_{}.txt'.format(step_dict['com_file'],_PV.pvADR)
            with open(fname, 'a') as file:
                file.write('{} notify_step: {}\n'.format(datetime.datetime.now(),step_dict['message']))
        elif step_dict['type'] == 'pvflow':
            _PV.RunAtPort(port = step_dict['p'], rat = step_dict['r'], vol = step_dict['v'], direction = step_dict['d'])
            expect_time = math.ceil(int(step_dict['v']) / int(step_dict['r']) * 60) +int(step_dict['post_wait'])
            _PV.thread_kill.wait(timeout=expect_time)

        if _PV.thread_kill.is_set():
            print("killing thread inner")
            return False
        pump_Running = True
        while pump_Running:
            status = _PV.pump.getStatus()
            if status == 'halted':
                pump_Running = False
        return True

    def runSeqScript(_PV,seq_list):
        flag = True
        step_num = 0
        while flag and step_num < len(seq_list):
            flag = runStep_threadCheck(_PV, sequence_steps[step_num])
            step_num += 1
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    with open(params['file_path'], 'r') as f:
        prog_dict = json.load(f)
    sequence_steps = prog_dict['sequence_steps']
    if len(sequence_steps)>0:
        PV.thread_kill = threading.Event()
        PV.k = threading.Thread(target=runSeqScript, args=(PV, sequence_steps))
        PV.k.start()
    else:
        print('seq length 0')

def prog_from_json3(PV,params):
    """there a re 3 types of steps.
    'make_schedule': will read the list of cycle times, note the current time and make a file with the schedule
        for each cycle given the current start time.
    'notify': will write a line to a file noting what whash cycle it is now starting
    'pvflow': will send code to pumps valves"""
    PV.running_seq = True

    def runStep_threadCheck(_PV,step_dict):
        log_fname = 'pump_{}_prog_log.txt'.format(_PV.pvADR)
        with open(log_fname, 'a') as file:
            file.write('{} {}\n'.format(datetime.datetime.now(), step_dict))
        if step_dict['type'] == 'make_schedule':
            now = datetime.datetime.now()
            for delta_t in step_dict['cycle_times']:
                now = now + datetime.timedelta(minutes = float(delta_t))
                fname = '{}_{}.txt'.format(step_dict['file_name'],_PV.pvADR)
                with open(fname, 'a') as file:
                    file.write('{} \n'.format(now))
        elif step_dict['type'] == 'notify':
            fname = '{}_{}.txt'.format(step_dict['com_file'],_PV.pvADR)
            with open(fname, 'a') as file:
                file.write('{} notify_step: {}\n'.format(datetime.datetime.now(),step_dict['message']))
        elif step_dict['type'] == 'pvflow':
            _PV.RunAtPort(port = step_dict['p'], rat = step_dict['r'], vol = step_dict['v'], direction = step_dict['d'])
            expect_time = math.ceil(int(step_dict['v']) / int(step_dict['r']) * 60) +int(step_dict['post_wait'])
            _PV.thread_kill.wait(timeout=expect_time)

        if _PV.thread_kill.is_set():
            print("killing thread inner")
            return False
        pump_Running = True
        while pump_Running:
            status = _PV.pump.getStatus()
            if status == 'halted':
                pump_Running = False
        return True

    def runSeqScript(_PV,seq_list):
        flag = True
        step_num = 0
        while flag and step_num < len(seq_list):
            flag = runStep_threadCheck(_PV, sequence_steps[step_num])
            step_num += 1
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    with open(params['file_path'], 'r') as f:
        prog_dict = json.load(f)
    sequence_steps = prog_dict['sequence_steps']
    if len(sequence_steps)>0:
        PV.thread_kill = threading.Event()
        PV.k = threading.Thread(target=runSeqScript, args=(PV, sequence_steps))
        PV.k.start()
    else:
        print('seq length 0')
