import threading

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
            while flag and i < 20:
                flag = RunAtPort_threadCheck(_PV, p=2, r=200, v=100, d='Infuse') and \
                       RunAtPort_threadCheck(_PV, p=2, r=12, v=60, d='Infuse')

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

