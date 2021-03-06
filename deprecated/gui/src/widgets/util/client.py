# #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module ...

__author__ = "Magnus Kvendseth Øye"
__copyright__ = "Copyright 2019, Sparkie Quadruped Robot"
__credits__ = ["Magnus Kvendseth Øye", "Petter Drønnen", "Vegard Solheim"]
__version__ = "1.0.0"
__license__ = "MIT"
__maintainer__ = "Magnus Kvendseth Øye"
__email__ = "magnus.oye@gmail.com"
__status__ = "Development"
"""

# Importing package
import socket
from threading import Thread
import time


class Client(Thread):
    """doc"""
    
    def __init__(self, host='127.0.0.1', port=5056, rate=0.2):
        Thread.__init__(self)
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isConnected = False
        self.rate = rate
    
    def run(self):
        """doc"""
        self.connect()
        while self.isConnected:
            # Do something
            pass
    
    def connect(self):
        """doc"""
        try:
            self.socket.connect(self.address)
            self.isConnected = True
        except OSError:
            pass
            
    def disconnect(self):
        """doc"""
        self.socket.close()
        self.isConnected = False
    
    def read(self):
        """doc"""
        try:
            payload = self.socket.recv(4096)
            return payload.decode('latin-1')
        except OSError:
            return False
    
    def write(self, payload):
        """doc"""
        payload = payload + '\n'
        self.socket.sendall(payload.encode())
    



# Example of usage
if __name__ == "__main__":
    c1 = Client('10.10.10.219', 8089, 0.2)
    c1.connect()
    while c1.isConnected:
        sad = c1.read()
        print(sad)