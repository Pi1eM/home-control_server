# Implementacja oprogramowania dla urządzenia


import socket


class Device:
    """Urządzenie, które za pomocą socketu odbiera dane od serwera
    i wykonuje swoje zadanie."""
    def __init__(self, name, host = "localhost", port = 8080):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

    def execute(self, data): # powinno być zależne od urządzenia
        """Wykonuje przysłane polecenie."""
        print(self.name, "Wykonaj: ", data)

    def receive(self, bufs):
        """Odbiera wiadomość."""
        return self.sock.recv(bufs)

    def run(self):
        """Główna pętla urządzenia, czyli odbierz-zdekoduj-wykonaj."""
        bufs = 16
        while True:
            bmsg = self.receive(16)
            msg = bmsg.decode("utf-8")
            self.execute(msg)


# w celach testowych (przykład użycia):
if __name__ == "__main__":
    t = Device("warmer", port = 8082)
    print(t.name, t.host, t.port)
    t.run()
