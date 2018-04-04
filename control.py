# Kontrolka dla użytkownika, napisana z użyciem Gtk


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from xmlrpc.client import ServerProxy

from excep import *


class HomeControlWindow(Gtk.Window):
    """Kontrolka całego systemu."""
    def __init__(self):
        """Konfiguruje główne okno i ściąga pierwsze dane z serwera."""
        super(HomeControlWindow, self).__init__()
        self.set_title("Home Control")
        self.connect("destroy", Gtk.main_quit)

        # Główne pudło
        self.mainBox = Gtk.VBox()
        self.add(self.mainBox)

        # pudełka na fajne przyciski i na treść oraz "nagłówek"
        self.butBox = Gtk.HBox()
        self.ovrLab = Gtk.Label("Sensors, devices and tasks")
        self.datBox = Gtk.HBox()

        # fajne przyciski
        self.addSensBut = Gtk.Button(label = "add sensor")
        self.rmSensBut = Gtk.Button(label = "remove sensor")
        self.addDevBut = Gtk.Button(label = "add device")
        self.rmDevBut = Gtk.Button(label = "remove device")
        self.addTaskBut = Gtk.Button(label = "add task")
        self.rmTaskBut = Gtk.Button(label = "remove task")
        self.setDevBut = Gtk.Button(label = "set device")
        self.refBut = Gtk.Button(label = "refresh")

        self.addSensBut.connect("clicked", self.addSens_clicked)
        self.rmSensBut.connect("clicked", self.rmSens_clicked)
        self.addDevBut.connect("clicked", self.addDev_clicked)
        self.rmDevBut.connect("clicked", self.rmDev_clicked)
        self.addTaskBut.connect("clicked", self.addTask_clicked)
        self.rmTaskBut.connect("clicked", self.rmTask_clicked)
        self.setDevBut.connect("clicked", self.setDev_clicked)
        self.refBut.connect("clicked", self.ref_clicked)

        self.butBox.pack_start(self.addSensBut, True, True, 2)
        self.butBox.pack_start(self.rmSensBut, True, True, 2)
        self.butBox.pack_start(self.addDevBut, True, True, 2)
        self.butBox.pack_start(self.rmDevBut, True, True, 2)
        self.butBox.pack_start(self.addTaskBut, True, True, 2)
        self.butBox.pack_start(self.rmTaskBut, True, True, 2)
        self.butBox.pack_start(self.setDevBut, True, True, 2)
        self.butBox.pack_start(self.refBut, True, True, 2)

        self.mainBox.pack_start(self.butBox, False, False, 10)

        # nagłówek
        self.mainBox.pack_start(self.ovrLab, False, False, 10)

        # treść
        self.sensBox = Gtk.ListBox()
        self.devBox = Gtk.ListBox()
        self.taskBox = Gtk.ListBox()

        self.sensBox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.devBox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.taskBox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        def sort_func(row1, row2, data, notify_destroy):
            if row1.typ == row2.typ:
                return row1.name > row2.name 
            return row1.typ > row2.typ

        self.sensBox.set_sort_func(sort_func, None, False)
        self.devBox.set_sort_func(sort_func, None, False)

        self.datBox.pack_start(self.sensBox, False, False, 10)
        self.datBox.pack_start(self.devBox, False, False, 10)
        self.datBox.pack_start(self.taskBox, False, False, 10)

        self.mainBox.pack_start(self.datBox, False, False, 10)

        self.serverus = ServerProxy("http://localhost:8000", allow_none = True)
        self.refresh()
        self.show_all()


    # fajne przyciski cd.
    def addSens_clicked(self, addSensBut):
        addWin = addSensWindow(self.serverus)


    def rmSens_clicked(self, rmSensBut):
        row = self.sensBox.get_selected_row()
        if row is None:
            return
        self.serverus.rmSensor(row.name)
        self.refresh()


    def addDev_clicked(self, addDevBut):
        addWin = addDevWindow(self.serverus)


    def rmDev_clicked(self, rmDevBut):
        row = self.devBox.get_selected_row()
        if row is None:
            return
        self.serverus.rmDevice(row.name)
        self.refresh()


    def addTask_clicked(self, addTaskBut):
        addWin = addTaskWindow(self.serverus)


    def rmTask_clicked(self, rmTaskBut):
        row = self.taskBox.get_selected_row()
        if row is None:
            return
        self.serverus.rmTask(row.task)
        self.refresh()


    def setDev_clicked(self, setDevBut):
        """Ręczne ustawienie wartości danego urządzenia."""
        row = self.devBox.get_selected_row()
        if row is None:
            return
        setWin = setDevWindow(row.name, self.serverus)


    def ref_clicked(self, refBut):
        """Odświeżenie danych z serwera."""
        self.refresh()

    # inne
    def refresh(self):
        """Ściąga i wyświetla aktualne dane z serwera."""
        (state, tasks) = self.serverus.getData()
        (sensors, devices) = div(state)
        for row in self.sensBox:
            self.sensBox.remove(row)
        for row in self.devBox:
            self.devBox.remove(row)
        for row in self.taskBox:
            self.taskBox.remove(row)
        for sens in sensors:
            self.sensBox.add(ListBoxRowState(sens))
        for dev in devices:
            self.devBox.add(ListBoxRowState(dev))
        for task in tasks:
            self.taskBox.add(ListBoxRowTask(task))
        self.show_all()


def div(lis):
    """Dzieli zbiorczą listę na listy sensorów i urządzeń."""
    sens = ["time", "temp", "move"]
    s = []
    d = []
    for (name, (typ, state)) in lis:
        if typ in sens:
            s.append((name, (typ, state)))
        else:
            d.append((name, (typ, state)))
    return (s, d)



class ListBoxRowState(Gtk.ListBoxRow):
    """Pomocnicza klasa do wyświetlania czujników i urządzeń."""
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        (self.name, (self.typ, self.state)) = data
        end = ""
        if self.typ == "temp":
            end = " " + u"\u00B0" + "C"
        self.add(Gtk.Label("Name: " + self.name + "\tType: " + self.typ + "\tState: " + str(self.state) + end))


class ListBoxRowTask(Gtk.ListBoxRow):
    """Pomocnicza klasa do wyświetlania zadań."""
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.task = data
        (self.sensName, self.devName, (_, self.data)) = data
        if self.data is not None:
            self.add(Gtk.Label("Sensor: " + self.sensName + "\tDevice: " + self.devName + "\tWhen: " + str(self.data)))
        else:
            self.add(Gtk.Label("Sensor: " + self.sensName + "\tDevice: " + self.devName))



class addSensWindow(Gtk.Window):
    """Pomocnicze okno dialogowe."""
    def __init__(self, server):
        super(addSensWindow, self).__init__()
        self.set_title("Adding new sensor")
        self.serverus = server

        self.mainBox = Gtk.VBox()
        self.add(self.mainBox)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Name:\t")
        self.nameEnt = Gtk.Entry()
        self.nameEnt.set_text("")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.nameEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Type:\t")
        types = ["time", "temp", "move"]
        self.typeCombo = Gtk.ComboBoxText()
        self.typeCombo.set_entry_text_column(0)
        for typ in types:
            self.typeCombo.append_text(typ)
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.typeCombo, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Host:\t")
        self.hostEnt = Gtk.Entry()
        self.hostEnt.set_text("localhost")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.hostEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Port:\t")
        self.portEnt = Gtk.Entry()
        self.portEnt.set_text("8001")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.portEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        self.OKBut = Gtk.Button(label = "OK")
        self.OKBut.connect("clicked", self.OK_clicked)
        rowBox.pack_start(self.OKBut, True, True, 4)
        self.mainBox.pack_start(rowBox, False, False, 4)

        self.show_all()


    def OK_clicked(self, OKBut):
        name = self.nameEnt.get_text()
        typ = self.typeCombo.get_active_text()
        host = self.hostEnt.get_text()
        port = int(self.portEnt.get_text()) 
        exc = self.serverus.addSensor(name, typ, host, port)
        if exc is None:
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(exc))
            dialog.run()
            dialog.destroy()


class addDevWindow(Gtk.Window):
    """Pomocnicze okno dialogowe."""
    def __init__(self, server):
        super(addDevWindow, self).__init__()
        self.set_title("Adding new device")
        self.serverus = server

        self.mainBox = Gtk.VBox()
        self.add(self.mainBox)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Name:\t")
        self.nameEnt = Gtk.Entry()
        self.nameEnt.set_text("")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.nameEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Type:\t")
        types = ["light", "elec", "blind", "warm", "airc"]
        self.typeCombo = Gtk.ComboBoxText()
        self.typeCombo.set_entry_text_column(0)
        for typ in types:
            self.typeCombo.append_text(typ)
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.typeCombo, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Host:\t")
        self.hostEnt = Gtk.Entry()
        self.hostEnt.set_text("localhost")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.hostEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Port:\t")
        self.portEnt = Gtk.Entry()
        self.portEnt.set_text("8081")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.portEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        self.OKBut = Gtk.Button(label = "OK")
        self.OKBut.connect("clicked", self.OK_clicked)
        rowBox.pack_start(self.OKBut, True, True, 4)
        self.mainBox.pack_start(rowBox, False, False, 4)

        self.show_all()


    def OK_clicked(self, OKBut):
        name = self.nameEnt.get_text()
        typ = self.typeCombo.get_active_text()
        host = self.hostEnt.get_text()
        port = int(self.portEnt.get_text())
        exc = self.serverus.addDevice(name, typ, host, port)
        if exc is None:
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(exc))
            dialog.run()
            dialog.destroy()



class setDevWindow(Gtk.Window):
    """Pomocnicze okno dialogowe."""
    def __init__(self, name, server):
        super(setDevWindow, self).__init__()
        self.set_title("Setting device")
        self.serverus = server
        self.name = name

        self.mainBox = Gtk.VBox()
        self.add(self.mainBox)

        self.entry = Gtk.Entry()
        self.entry.set_text("")
        self.OKBut = Gtk.Button(label = "OK")
        self.OKBut.connect("clicked", self.OK_clicked)
        self.mainBox.pack_start(self.entry, True, True, 4)
        self.mainBox.pack_start(self.OKBut, True, True, 4)
        self.show_all()


    def OK_clicked(self, OKBut):
        arg = int(float(self.entry.get_text()))
        exc = self.serverus.setDevice(self.name, arg)
        if exc is None:
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(exc))
            dialog.run()
            dialog.destroy()


class addTaskWindow(Gtk.Window):
    """Pomocnicze okno dialogowe."""
    def __init__(self, server):
        super(addTaskWindow, self).__init__()
        self.set_title("Adding new task")
        self.serverus = server

        self.mainBox = Gtk.VBox()
        self.add(self.mainBox)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Sensor name:\t")
        self.senEnt = Gtk.Entry()
        self.senEnt.set_text("")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.senEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Device name:\t")
        self.devEnt = Gtk.Entry()
        self.devEnt.set_text("")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.devEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Type:\t")
        types = self.serverus.getTemp()
        self.typeCombo = Gtk.ComboBoxText()
        self.typeCombo.set_entry_text_column(0)
        for typ in types:
            self.typeCombo.append_text(typ)
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.typeCombo, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        label = Gtk.Label("Value (optional):\t")
        self.valEnt = Gtk.Entry()
        self.valEnt.set_text("")
        rowBox.pack_start(label, True, True, 2)
        rowBox.pack_start(self.valEnt, True, True, 2)
        self.mainBox.pack_start(rowBox, False, False, 4)

        rowBox = Gtk.HBox()
        self.OKBut = Gtk.Button(label = "OK")
        self.OKBut.connect("clicked", self.OK_clicked)
        rowBox.pack_start(self.OKBut, True, True, 4)
        self.mainBox.pack_start(rowBox, False, False, 4)

        self.show_all()


    def OK_clicked(self, OKBut):
        senName = self.senEnt.get_text()
        devName = self.devEnt.get_text()
        typ = self.typeCombo.get_active_text()
        value = self.valEnt.get_text()
        if value == "":
            value = None
        exc = self.serverus.letTask(senName, devName, typ, value)
        if exc is None:
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(exc))
            dialog.run()
            dialog.destroy()



# Uruchomienie kontrolki
if __name__ == "__main__":
    win = HomeControlWindow()
    Gtk.main()

