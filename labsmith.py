
from uProcess_x64 import CEIB

class EIB200:
    def __init__(self,COM):
        self.COM = COM
        self.eib = CEIB()
        self.eib.InitConnection(COM)
        self.dev_list = self.eib.CmdCreateDeviceList()
        self.ls4vm = self.dev_list[0]
class Valve:
    def __init__(self,ls4vm,channel):
        self.ls4vm = ls4vm
        self.channel = channel

    def moveToPort(self,port):
        return self.ls4vm.CmdSelect(self.channel,port)

    def getStatus(self):
        return self.ls4vm.GetValveStatus(1)
