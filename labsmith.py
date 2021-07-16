
from uProcess_x64 import CEIB, C4VM

class EIB200:
    def __init__(self,COM):
        self.COM = COM
        self.eib = CEIB()
        self.eib.InitConnection(COM)
        self.dev_list = self.eib.CmdCreateDeviceList()
        self.ls4vm = self.dev_list[0]
class Valve:
    def __init__(self,ls4vm, channel,lock = None):
        self.ls4vm = ls4vm
        self.channel = channel
        self.lock = lock

    def moveToPort(self,port):
        moving = True
        while moving:
            if self.lock is not None:
                self.lock.acquire()
            _ = self.ls4vm.CmdSelect(self.channel, port)
            s = self.ls4vm.GetValveStatus(self.channel)
            if self.lock is not None:
                self.lock.release()
            moving = C4VM.IsMoving(s)
            print(moving, C4VM.GetSelection(s))

    def getStatus(self):
        return self.ls4vm.GetValveStatus(1)

    def setLock(self,lock):
        self.lock = lock
