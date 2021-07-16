class PumpValve:
    def __init__(self,valve,pump,pvADR):
        self.valve = valve
        self.pump = pump
        self.pvADR = pvADR
        self.current_port = 1
        self.moveToPort(1)
        print('initialized valve at port 1')

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