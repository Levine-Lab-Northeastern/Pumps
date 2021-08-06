import threading
import time


class PumpValve:
    def __init__(self,valve,pump,pvADR):
        """pump valve object is a pump and valve pair where the syringe is connected to the fixed port on the AV801
        init with a valve object, pump object, and address for the unit"""
        self.valve = valve
        self.pump = pump
        self.pvADR = pvADR
        self.current_port = 1
        self.moveToPort(1)
        print('initialized valve at port 1')
        self.running_seq = False
        self.seq_dict = None

    def moveToPort(self,port):
        """Moves valve to the port passed in, helper method for RunAtPort"""
        if self.pump.getStatus() != 'halted':
            self.pump.stop()
        self.valve.moveToPort(port)
        self.current_port = port

    def runPumpPhase(self,rat,vol,direction):
        """sends a single phase program to the pump, helper method for RunAtPort"""
        self.pump.singlePhaseProgram(rat,vol,direction)

    def RunAtPort(self,port,rat,vol,direction):
        """moves valve to the input port and sends a single phase program to pump"""
        self.moveToPort(port)
        self.runPumpPhase(rat,vol,direction)

    def runSequence(self, seq_dict):
        """Runs program for the pump valve unit,
        Takes in the program dictionary,
        launches a new thread that sends a sequence of RunAtPort commands
        and sleeps for the expected pump run time in between"""
        self.seq_dict = seq_dict
        self.running_seq = True

        def runSeq(_self,seq_dictionary):
            for loop in range(seq_dictionary["Loops"]):
                print("starting loop {}".format(loop))
                for phase in seq_dictionary["Phases"]:
                    print("Current Phase:", phase)
                    # if phase["port"] == -1:
                        #port =
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