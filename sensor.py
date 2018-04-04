# Implementacja oprogramowania dla czujnika


import socket


class Sensor:
    """Sensor, które za pomocą socketu wysyła serwerowi dane."""
    def __init__(self, name, host = "localhost", port = 8001):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def data(self): # powinno być zależne od rodzaju sensora
        """Zbiera dane."""
        return input()

    def send(self, msg):
        """Przesyła dane do serwera."""
        self.sock.sendto(msg, (self.host, self.port))

    def run(self):
        """Główna pętla urządzenia, czyli zbierz-zakoduj-wyślij."""
        while True:
            msg = self.data()
            bmsg = str.encode(str(msg))
            self.send(bmsg)


# w celach testowych (przykład użycia):
if __name__ == "__main__":
    time = Sensor("timer", port = 8001)
    print(time.name, time.host, time.port)
    time.run()
