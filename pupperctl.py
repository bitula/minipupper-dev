#!/usr/bin/python
from controller import Controller, Config

controller = Controller(Config())  

if __name__ == "__main__": 
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.shutdown()