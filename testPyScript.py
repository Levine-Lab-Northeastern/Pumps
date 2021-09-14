import threading


def pulse20and60(PV,params):
    """Runs program for the pump valve unit using complex script here,
            launches a new thread that sends a sequence of RunAtPort commands
            and sleeps for the expected pump run time in between"""
    #self.seq_dict = seq_dict
    PV.running_seq = True

    def runSeq(_PV, params):  # ,thread_kill):# port = None, dir = None, vol = None, rat = None):
        for hour in range(params['num_hours']):
            def RunAtPort_threadCheck(_PV,p,r,v,d):
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
            """1.1"""
            #for l in range(2):
            # need to loop this section
            phase = {'p': 1, 'r': 100, 'v': 25, 'd': 'Withdraw'}
            if not RunAtPort_threadCheck(_PV, phase['p'], phase['r'], phase['v'], phase['d']):
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
            #if _PV.thread_kill.is_set():

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
            # print("starting loop {}".format(loop))
            # print(seq_dictionary)
            # for phase in seq_dictionary["Phases"]:
            #     print("Current Phase:", phase)
            #     # if the prog dict has -1 or 'entry', use the entered parameters passed this this function an entry params dict
            #
            #     # old way thats now commented had dict phases that was somehow being reused:
            #     # if first run is with infuse then next run will also have infused because "entry" will be overwriten
            #     # could also use a copy dictionary
            #     if phase["port"] == -1:
            #         p = int(entry_params["port"])
            #     else:
            #         p = phase["port"]
            #     if phase["rate"] == -1:
            #         r = int(entry_params["rate"])
            #     else:
            #         r = phase["rate"]
            #     if phase["vol"] == -1:
            #         v = int(entry_params["vol"])
            #     else:
            #         v = phase["vol"]
            #     if phase["dir"] == "Entry":
            #         d = entry_params["dir"]
            #     else:
            #         d = phase["dir"]
            #only need the outter thread kill if there is a double for loop
            # if _PV.thread_kill.is_set():
            #     print("killing thread outter")
            #     break
        _PV.running_seq = False
        _PV.thread_kill.clear()
        print("finished sequence")

    PV.thread_kill = threading.Event()
    PV.k = threading.Thread(target=runSeq, args=(PV, params))
    PV.k.start()
