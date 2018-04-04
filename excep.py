class UsedNameException(Exception):
    """Wyjątek, który informuje, że nazwa jest już używana."""
    def __init__(self, name):
        self.name = name


class UsedAddrException(Exception):
    """Wyjątek, który informuje, że adres jest już używany."""
    def __init__(self, addr):
        self.addr = addr
