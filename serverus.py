# Serwer


from socket import *
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
from queue import Queue
from threading import Thread
from time import sleep
from datetime import datetime
import csv

from excep import *


class AsyncServer(ThreadingMixIn, SimpleXMLRPCServer):
    """Wielowątkowy aplikacyjny serwer asynchroniczny."""
    pass

# typ: "time", "temp", "move", "light", "elec", "blind", "warm", "airc"

class HomeControl:
    """Klasa, której instancja jest wrzucana do serwera. Klasa
    zbiera dane z czujników, przetwarza je i wysyła polecenia do
    urządzeń autonomicznie lub pod kontrolą użytkownika."""
    def __init__(self):
        self.sensors = {}   # słownik: name:(typ, socket)
        self.devices = {}   # słownik: name:(typ, socket)
        self.address = []   # lista używanych adresów: (host, port)
        self.taskTemp = {"tempTask":self.tempTask, "moveTask1":self.moveTask1, "moveTask2":self.moveTask2, "moveTask3":self.moveTask3, "timeTask":self.timeTask}
                            # słownik szablonów zadań
        self.taskList = []  # lista zadań: (sensName, devName, (function, data))
        self.state = {}     # słownik stanu sensorów i urządzeń
                            # name:(typ, state)
        self.dataQ = Queue() # kolejka nieprzetworzonych danych z sensorów
        self.sendQ = Queue() # kolejka danych do wysłania urządzeniom
        self.listen = {}    # słownik wątków odbierających dane
        self.dataUper = Thread(target = self.dataUp)
        self.sender = Thread(target = self.sendDevData)
        self.dataUper.start()
        self.sender.start()
        print("Serverus running")


    def addSensor(self, name, typ, host, port):
        """Dodaje sensor o zadanej nazwie i gnieździe (socket)."""
        print("addSensor", name, typ, host, port)
        addr = (host, port)
        if name in self.state:
            return UsedNameException(name)
        if addr in self.address:
            return UsedAddrException(addr)
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(addr)
        self.address.append(addr)
        self.sensors[name] = (typ, sock)
        self.state[name] = (typ, 0)
        self.listen[name] = Thread(target = self.recvSensData, args = (name,))
        self.listen[name].start()
        

    def rmSensor(self, name):
        """Usuwa sensor o zadanej nazwie."""
        print("rmSensor", name)
        print(self.sensors)
        if name not in self.sensors:
            raise BadNameException(name)
        (_, sock) = self.sensors[name]
        addr = sock.getsockname()
        print("shutting down socket")
        try:        
            sock.shutdown(SHUT_RDWR)
            sock.close()
        except:
            pass
        del self.sensors[name]
        del self.state[name]
        del self.listen[name]
        self.taskList = delKey(self.taskList, name)
        (ad, port) = addr
        if ad == "127.0.0.1":
            addr = ("localhost", port) 
        self.address.remove(addr)


    def addDevice(self, name, typ, host, port):
        """Dodaje urządzenie o danej nazwie i gnieździe."""
        print("addDevice", name, typ, host, port)
        addr = (host, port)
        if name in self.state:
            return UsedNameException(name)
        if addr in self.address:
            return UsedAddrException(addr)
        self.address.append(addr)
        self.devices[name] = (typ, addr)
        self.state[name] = (typ, 0)


    def rmDevice(self, name):
        """Usuwa urządzenie o zadanej nazwie."""
        print("rmDevice", name)
        if name not in self.devices:
            return BadNameException(name)
        (_, addr) = self.devices[name]
        del self.devices[name]
        del self.state[name]
        self.taskList = delKey(self.taskList, name)
        (ad, port) = addr
        if ad == "127.0.0.1":
            addr = ("localhost", port)
        self.address.remove(addr)


    def letTask(self, sensName, devName, funName, data):
        """Zleca automatyczną interprerację danych z zadanego
        sensora jako mających związek z zadanym urządzeniem."""
        print("letTask", sensName, devName, funName, data)
        if sensName not in self.sensors:
            return BadNameException(sensName)
        if devName not in self.devices:
            return BadNameException(devName)
        function = self.taskTemp[funName]
        if data is not None:
            task = lambda x: function(devName, data, x)
        else:
            task = lambda x: function(devName, x)
        self.taskList.append((sensName, devName, (task, data))) 
        

    def rmTask(self, task):
        """Anuluje dane zadanie."""
        print("rmTask", task)
        (sName, dName, (_, val)) = task
        for t in self.taskList:
            (isN, idN, (_, ival)) = t
            if isN == sName and idN == dName and ival == val:
                self.taskList.remove(t)


    def dataUp(self):
        """Ściąga z kolejki dane, aktualizuje stan
        oraz zleca wykonanie zadań."""
        print("dataUp")
        while True:
            (name, msg) = self.dataQ.get()
            if name not in self.state:
                continue
            (typ, _) = self.state[name]
            self.state[name] = (typ, msg)
            tasks = findKey(self.taskList, name)
            for (task, _) in tasks:
                send = task(msg)
                if send is not None:
                    self.sendQ.put(send)


    def recvSensData(self, name):
        """Czeka na dane od zadanego sensora i wrzuca do kolejki."""
        print("recvSensData", name)
        (_, sock) = self.sensors[name]
        bufs = 16
        while True:
            bmsg = sock.recv(bufs)
            if not bmsg: 
                break
            msg = bmsg.decode("utf-8")
            self.dataQ.put((name, msg))


    def sendDevData(self):
        """Wysyła urządzeniu polecenie z kolejki."""
        sock = socket(AF_INET, SOCK_DGRAM)
        while True:
            print("sendSensData")
            (name, data) = self.sendQ.get()
            (typ, addr) = self.devices[name]
            self.state[name] = (typ, data)
            bmsg = str.encode(str(data))
            sock.sendto(bmsg, addr)
            

   
    # zależności sensor - urządzenie

    def tempTask(self, device, letTemp, actTemp):
        """Utrzymuje zadaną temperaturę."""
        print("tempTask", device, letTemp, actTemp)
        if device not in self.state:
            return None
        (typ, power) = self.state[device]
        if typ == "warm":
            if letTemp < actTemp:
                power -= 25
            if letTemp > actTemp:
                power += 10
        if typ == "airc":
            if letTemp < actTemp:
                power += 10
            if letTemp > actTemp:
                power -= 25
        return (device, power)


    def moveTask1(self, device, move):
        """Zapala/gasi (podnosi/opuszcza rolety) przy przejściu przez drzwi."""
        print("moveTask1", device, move)
        if device not in self.state:
            return None
        (typ, on) = self.state[device]
        if typ == "light" or typ == "elec" or typ == "blind":
            if move == '1':
                on = 1 - on
        return (device, on)


    def moveTask2(self, device, move):
        """Zapala przy ruchu (gaszenie ręczne)."""
        print("moveTask2", device, move)
        if device not in self.state:
            return None
        (typ, on) = self.state[device]
        if typ == "light" or typ == "elec":
            if move == '1':
                on = 1
        return (device, on)


    def moveTask3(self, device, move):
        """Zapala przy ruchu, gasi przy bezruchu."""
        print("moveTask3", device, move)
        if device not in self.state:
            return None
        (typ, on) = self.state[device]
        if typ == "light" or typ == "elec":
            if move == '1':
                on = 1
            else:
                on = 0
        return (device, on)


    def timeTask(self, device, data, actTime):
        """Włącza/wyłącza urządzenie (wezęł, światło, roletę) o zadanej godzinie."""
        print("timeTask", device, data, actTime)
        if device not in self.state:
            return None
        (letTime, up) = data
        (typ, on) = self.state[device]
        if typ == "elec" or typ == "light" or typ == "blind":
            if actTime == letTime:
                on = up
        return (device, on)

    # inne
    def getData(self):
        """Wysyła stan i listę zadań do wyświetlania."""
        print("getData")
        stateList = [ (k,v) for k, v in self.state.items() ]
        print(stateList)
        print(self.taskList)
        return (stateList, self.taskList)


    def getTemp(self):
        """Wysyła szablony tasków."""
        print("getTemp")
        return [ k for k in self.taskTemp.keys() ]


    def setDevice(self, name, arg):
        """Wybiera urządzenie z listy i przekazuje arg dalej."""
        print("setDevice", name, arg)
        if name not in self.devices:
            return BadNameException(name)
        (typ, _) = self.devices[name]
        if typ == "airc" or typ == "warm":
            self.setPower(name, arg)
        if typ == "light":
            self.setLight(name, arg)
        if typ == "elec":
            self.setElec(name, arg)
        if typ == "blind":
            self.setBlind(name, arg)


    def setPower(self, name, power):
        """Zadaje danemu urządzeniu jakąś moc (procentowo)."""
        print("setPower", name, power)
        if power > 100:
            power = 100
        if power < 0:
            power = 0
        self.sendQ.put((name, power))


    def setLight(self, name, on):
        """Zapala/gasi światło."""
        print("setLight", name, on)
        if on >= 0.5:
            on = 1
        self.sendQ.put((name, on))


    def setElec(self, name, on):
        """Włącza/wyłącza prąd w danym węźle."""
        print("setElec", name, on)
        if on >= 0.5:
            on = 1
        self.sendQ.put((name, on))


    def setBlind(self, name, on):
        """Zasłania/odsłania roletę/y."""
        print("setBlind", name, on)
        if on >= 0.5:
            on = 1
        self.sendQ.put((name, on))


# pomocnicze

def findKey(lis, key):
    """W liście trzykrotek szuka key jako pierwszego
    lub drugiego elementu i zwraca trzeci element."""
    ret = []
    for (fst, snd, trd) in lis:
        if fst == key or snd == key:
            ret.append(trd)
    return ret


def delKey(lis, key):
    """Zwraca z listy trzykrotek wpisy, w       
    których klucz nie jest pierwszym ani drugim elementem."""
    ret = []
    for (fst, snd, trd) in lis:
        if fst != key and snd != key:
            ret.append((fst, snd, trd))
    return ret


# Przygotowanie serverusa
if __name__ == "__main__":
    serverus = SimpleXMLRPCServer(("localhost", 8000), allow_none = True)
    serverus.register_instance(HomeControl())
    serverus.serve_forever()

