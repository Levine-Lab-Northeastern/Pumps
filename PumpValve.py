import threading
import time


class PumpValve:
    def __init__(self,valve,pump,pvADR):
        self.valve = valve
        self.pump = pump
        self.pvADR = pvADR
        self.current_port = 1
        self.moveToPort(1)
        print('initialized valve at port 1')
        self.running_seq = False
        self.seq_dict = None

    def moveToPort(self,port):
        if self.pump.getStatus() != 'halted':
            self.pump.stop()
        self.valve.moveToPort(port)
        self.current_port = port

    def runPumpPhase(self,rat,vol,direction):
        self.pump.singlePhaseProgram(rat,vol,direction)

    def RunAtPort(self,port,rat,vol,direction):
        self.moveToPort(port)
        self.runPumpPhase(rat,vol,direction)

    def runSequence(self, seq_dict):
        self.seq_dict = seq_dict
        self.running_seq = True
        def runSeq(_self,seq_dictionary):
            for phase in seq_dictionary["Phases"]:
                print("Current Phase:", phase)
                _self.RunAtPort(phase["port"], phase["rate"], phase["vol"], phase["dir"])
                time.sleep(int(phase["vol"] / (phase["rate"] / 60)))
                pump_Running = True
                while pump_Running:
                    status = _self.pump.getStatus()
                    if status == 'halted':
                        pump_Running = False
                _self.running_seq = False
                print("finished sequence")
        k = threading.Thread(target=runSeq, args=(self,seq_dict))
        k.start()