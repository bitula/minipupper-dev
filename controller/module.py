import time
from ctypes import Structure, c_bool


class StateIO(Structure):
    _fields_ = [
        ("shutdown", c_bool)
    ]


class SharedMemInit:
     def __init__(self, shmem, memlist):
        for memory in memlist:
            setattr(self, memory, shmem[memory])


class BaseModule:
    def __init__(self, args, shmem, in_list, out_list) -> None:
        """Do Not start any threads/processes here, use on_start"""
        # set default values from config Attributes
        for key, value in args.items():
            setattr(self, key, value)

        # init shared memory
        self.ctl_state = SharedMemInit(shmem, ["StateIO"])
        self.shmem_in = SharedMemInit(shmem, in_list)
        self.shmem_out = SharedMemInit(shmem, out_list)

        # controller attributes 
        self.INIT_NAME  = "BaseModule"
        self.IS_MAIN    = None      # 0, on init
        self.IS_THREAD  = None      # 1    
        self.IS_PROCESS = None      # 2
        self.IS_RUNNING = False     # set by controller, before start
        self.SHUTDOWN   = None      # shared value
        self.T_DELTA    = 0.016     # TODO should be set by config attributes on init

    def on_start(self) -> None:
        pass

    def on_tick(self) -> None:
        pass

    def on_stop(self):
        pass

    def _start(self):
        print(" {0} subprocess starting".format(self.INIT_NAME))
        self.on_start()
        
    def _stop(self):
        print(" {0} subprocess stoping".format(self.INIT_NAME))
        self.on_stop()

    def timeout(self, ms=0):
        try:
            time.sleep(self.T_DELTA + ms)
        except KeyboardInterrupt:
            pass

    def _tick(self) -> None:
        self._start()
        while not self.ctl_state.StateIO[0].shutdown and not self.SHUTDOWN.value:
            # print(self.INIT_NAME)
            try:
                self.on_tick()
                self.timeout()

            except Exception as e:
                print("fatal error at {0} with message: {1}".format(self.INIT_NAME, e))
                # TODO should be in config shutdown controller or shutdow process only
                self.ctl_state.StateIO[0].shutdown = True
                break
        self._stop()

    def exit(self):
        '''
            stop and exit calling instance
        '''
        self.SHUTDOWN.value = True

    def shutdown(self):
        '''
            stop all instances and exit from main
        '''
        self.ctl_state.StateIO[0].shutdown = True
    
    def shm_numpy_out(self, name):
        attr = getattr(self.shmem_out, name)
        return attr[0]

    def shm_numpy_in(self, name):
        attr = getattr(self.shmem_in, name)
        return attr[0]

    def shm_write(self, name, key, value) -> None:
        attr = getattr(self.shmem_out, name)
        if key:
            setattr(attr[0], key, value)
            return
        setattr(attr[0], name, value)

    def shm_read(self, name, key) -> any:
        attr = getattr(self.shmem_in, name)
        return getattr(attr[0], key)

    def __str__(self):
        # TODO improve formating to make it more compact msg
        print("="*20)
        for key, value in self.__dict__.items():
            if type(value).__module__ == 'numpy':
                print("{0}:\n{1}".format(key, value))
            else:
                print("{0}: {1}".format(key, value))
        return "="*20
    
    # TODO move this to __str__
    def mem_print(self, mem):
        print("="*20)
        print(self.INIT_NAME)
        _mem = mem[0]
        for m in dir(_mem):
            if m[0] != '_':
                print(m, getattr(_mem, m))
        print("="*20)