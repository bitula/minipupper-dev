import argparse
 

class Config:
    def __init__(self, cfg_path=None, cfg_name=None):

        # TODO read from file default config from default path

        self.default ={
                        "controllers": {
                            "actuators": {
                                "default": {
                                    "ModuleName": "Kinematics",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 30,
                                    "InputMem": ["SensorsIO"],
                                    "OutputMem": ["ActuatorsIO"],
                                    }
                                },
                            "display": {
                                "default": {
                                    "ModuleName": "Display",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 21,
                                    "InputMem": ["SensorsIO"],
                                    "OutputMem": ["DisplayIO"],
                                    }
                                },
                            "speaker": {
                                "default": {
                                    "ModuleName": "BaseModule",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 20,
                                    "InputMem": [],
                                    "OutputMem": [],
                                    }
                                },
                            },
                        "interfaces": {
                            "hardware": {
                                "default": {
                                    "ModuleName": "MiniPupperHW",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 0,
                                    "InputMem": ["ActuatorsIO"],
                                    "OutputMem": ["HardwareIO"],
                                    }
                                },
                            "speaker": {
                                "default": {
                                    "ModuleName": "BaseModule",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 1,
                                    "RunPriority": 1,
                                    "InputMem": [],
                                    "OutputMem": [],
                                    }
                                },
                            "display": {
                                "default": {
                                    "ModuleName": "LCD_ST7789",
                                "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 2,
                                    "InputMem": ["DisplayIO"],
                                    "OutputMem": [],
                                    }
                                },
                            "actuators": {
                                "default": {
                                    "ModuleName": "MiniPupperLegs",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 3,
                                    "InputMem": ["HardwareIO", "ActuatorsIO"],
                                    "OutputMem": [],
                                    }
                                },
                            "joystick": {
                                "default": {
                                    "ModuleName": "PS4Joystick",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 10,
                                    "InputMem": [],
                                    "OutputMem": ["SensorsIO"],
                                    }
                                },
                            "keyboard": {
                                "default": {
                                    "ModuleName": "MouseKeyboard",
                                    "Attributes": {},
                                    "AutoImport": True,
                                    "AsyncInit": False,
                                    "RunType": 2,
                                    "RunPriority": 11,
                                    "InputMem": [],
                                    "OutputMem": ["SensorsIO"],
                                    }
                                },
                            }
                        }

    def _parse_args(self):
            
        # TODO autocomplication https://kislyuk.github.io/argcomplete/#
                
        parser = argparse.ArgumentParser()
        
        # Optional Arguments
        parser.add_argument( 
            "--no-display",
            help="Run MiniPupper with display off",
            action='store_true'
            )

        parser.add_argument( 
            "--no-sound",
            help="Run MiniPupper with sound off",
            action='store_true'
            )

        parser.add_argument( 
            "--no-actuators",
            help="Run MiniPupper with servos off",
            action='store_true'
            )

        parser.add_argument( 
            "--no-hardware",
            help="Run MiniPupper with servos off",
            action='store_true'
            )

        parser.add_argument( 
            "-d",
            "--daemon", 
            help="Stop MiniPupper daemon",
            nargs='?', const=True
            )

        parser.add_argument( 
            "-q",
            "--quiet", 
            help="Suppress stdout and stderr messages",
            nargs='?', const=True
            )

        # Exclusive Arguments (only one argument can be passed)
        args_group = parser.add_mutually_exclusive_group(required=False)

        args_group.add_argument( 
            "stop", 
            help="Stop Daemon",
            nargs='?', const=True
            )
        
        args_group.add_argument(
            "-k", 
            "--keyboard", 
            help="Keyboard input through ssh X Forwarding or direct",
            nargs='?', const="default"
            )

        args_group.add_argument(
            "-j", 
            "--joystick",
            help="Joystick input connected to minipupper bluetooth device",
            nargs='?', const="default"
            )

        args_group.add_argument(
            "-c", 
            "--calibrate",
            nargs='?', const="tui", choices=['gui', 'tui'],
            help="console or graphical calibration  tool"
            )

        args_group.add_argument( 
            "--actuators-only",
            help="Run pupper with servo command and terminate",
            nargs='?', const="default"
            )

        args_group.add_argument( 
            "--hardware-only",
            help="Run pupper with servo command and terminate",
            nargs='?', const="default"
            )

        args_group.add_argument( 
            "--display-only",
            help="Start minipupper with display enabled and servos and sound disabled",
            nargs='?', const="default"
            )

        args_group.add_argument( 
            "--sound-only",
            help="Start pupper app with sound output only",
            nargs='?', const="default"
            )

        args = parser.parse_args()

        if args.daemon:
            
            import ctypes
            
            if args.quiet:
                ctypes.CDLL(None).daemon(0, 0)
                return args

            ctypes.CDLL(None).daemon()
        
        return args   


    def load(self):
        cfg = self.default
        args = self._parse_args()
        return args, cfg
