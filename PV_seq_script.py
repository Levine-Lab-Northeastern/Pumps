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

        for hour in range(params['num_hours']):
            flag = True
            i = 0
            while flag and i < 2:
                flag = RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')

                i += 1
            if _PV.thread_kill.is_set():
                break
            """40 min to 60 min"""
            flag = True
            i = 0
            while flag and i < 1:
                flag = RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw') and \
                       RunAtPort_threadCheck(_PV, p=1, r=100, v=25, d='Withdraw')
                i += 1
            if _PV.thread_kill.is_set():
                break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSecScript, args=(PV, params))
    PV.k.start()

def twoPulseTypeOld(PV,params):
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

        for hour in range(params['num_hours']):

            for l in range(2):
                """1.1"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
                """1.2"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
                """1.2"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
                """1.3"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
                """1.4"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
                """1.5"""
                phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
                if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                    break
            if _PV.thread_kill.is_set():
                break

            """2.1"""
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                break
            """2.2"""
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                break
            """2.3"""
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                break
            """2.4"""
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                break
            """2.5"""
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
                break

        _PV.running_seq = False
        _PV.thread_kill.clear()
        _PV.current_phase = "no seq"
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSecScript, args=(PV, params))
    PV.k.start()
