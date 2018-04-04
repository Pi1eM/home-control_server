from xmlrpc.client import ServerProxy
from excep import *


server = ServerProxy("http://localhost:8000", allow_none = True)

server.addSensor("timer", "time", "localhost", 8001)
server.addSensor("temper", "temp", "localhost", 8002)
server.addSensor("temp2", "temp", "localhost", 8003)
server.addSensor("temp3", "temp", "localhost", 8004)
server.addSensor("temp4", "temp", "localhost", 8005)
server.addSensor("temp5", "temp", "localhost", 8006)
server.addSensor("move1", "move", "localhost", 8010)
server.addSensor("move2", "move", "localhost", 8011)
server.addSensor("move3", "move", "localhost", 8012)
server.addSensor("move4", "move", "localhost", 8013)

server.addDevice("blinds", "blind", "localhost", 8081)
server.addDevice("warmer", "warm", "localhost", 8082)
server.addDevice("cooler", "airc", "localhost", 8083)
server.addDevice("energy", "elec", "localhost", 8084)
server.addDevice("lights", "light", "localhost", 8085)

server.letTask("timer", "energy", "timeTask", ("08:00:00", 1))
server.letTask("timer", "blinds", "timeTask", ("08:00:00", 1))
server.letTask("move1", "lights", "moveTask1", None)
server.letTask("temper", "warmer", "tempTask", 20)
server.letTask("temper", "cooler", "tempTask", 20)
