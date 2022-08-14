import os
import sys
import signal
import threading
import multiprocessing 
import atexit
import time
from ctypes import c_bool

from .module import StateIO
from .config import Config
    

class Controller: 
    def __init__(self, config: Config) -> None:

        args, self.cfg = config.load()
        self.pidfile_path = '/tmp/controller.pids' # should be config ?

        # make sure self.on_exist is always called
        atexit.register(self.on_shutdown)

        self.procmem = {"StateIO": multiprocessing.Array(StateIO, 1)}
        self.threads = {}
        self.processes = {}
        
        # parse config and import modules classes
        self.modules_classes = {}
        self.args_import(args)
        
        # initialize all modules
        self.modules_instances = [None]*99
        self.modules_init()


    def _module_init(self, mtype):

        mclass = self.modules_classes[mtype]["ModuleName"]
        args = self.modules_classes[mtype]["Attributes"]
        init_order = self.modules_classes[mtype]["RunPriority"]
        in_list = self.modules_classes[mtype]["InputMem"]
        out_list = self.modules_classes[mtype]["OutputMem"]

        # initialize BaseModule class
        module = mclass(args, self.procmem, in_list, out_list)
        module.INIT_NAME = mtype
        module.INIT_ORDER = init_order
        module.SHUTDOWN = multiprocessing.Value(c_bool, False)
        # TODO tick_delta should be here with info msg if it is here

        run_type = self.modules_classes[mtype]["RunType"]
        if run_type == 0:
            module.IS_MAIN = True
        elif run_type == 1:
            module.IS_THREAD = True
        elif run_type == 2:
            module.IS_PROCESS = True
        else:
            print("fatal error: incorect RunType config at:\n module: {0}".format(module.INIT_NAME))
            sys.exit(1)

        if self.modules_instances[init_order]:
            _name = self.modules_instances[init_order].INIT_NAME
            print("fatal error: equal RunPriority config at modules:\n"
                  "module{0}\nmodule: {1}".format(_name, module.INIT_NAME))
            sys.exit(1)
        
        self.modules_instances.pop(init_order)
        self.modules_instances.insert(init_order, module)
        
        print(" {0} initilized".format(module.INIT_NAME))


    def modules_init(self):

        for key in self.modules_classes:
            
            asycn_init = self.modules_classes[key]["AsyncInit"]
            
            if asycn_init:
                thread = threading.Thread(
                    target=self._module_init, 
                    args=([key])
                    )
                thread.daemon = True
                thread.start()

            else:
                self._module_init(key)

        self.modules_instances = [ inst for inst in self.modules_instances if inst is not None ]
        index = list(range(len(self.modules_instances)))
        for instance, n in zip(self.modules_instances, index):
            instance.INIT_ORDER = n


    def start(self):

        self.kill_processes() # FIXME make sure only one instance is running
        
        # save main pid
        with open(self.pidfile_path, "w") as pidfile:
            pid0 = str(os.getpid())
            pidfile.write("%s\n" % (pid0))
            print(" controller started with PID(s):", pid0)
        
        tmp = []
        while not self.procmem["StateIO"][0].shutdown:
            # TODO test if class_import works here (hot reload), should be async call when updating instances
            # TODO add nice arg to processes 
            # FIXME on_start is out of order

            for instance in self.modules_instances:

                # print("tick:",instance.INIT_NAME)
                shutdown = instance.SHUTDOWN.value
                
                if not instance.IS_RUNNING:
                    if instance.IS_PROCESS and not shutdown:
                        instance.IS_RUNNING = True
                        proc = multiprocessing.Process(target=instance._tick)
                        proc.name = instance.INIT_NAME
                        self.processes[proc.name] = proc
                        proc.start()
                        # TODO should save here process pids

                    elif instance.IS_THREAD and not shutdown:
                        instance.IS_RUNNING = True
                        thread = threading.Thread(target=instance._tick)
                        thread.name = instance.INIT_NAME
                        thread.daemon = True
                        self.threads[thread.name] = thread
                        thread.start()

                    elif not instance.IS_MAIN and not shutdown:
                        instance.IS_RUNNING = True
                        instance._start()

                if instance.IS_MAIN and not shutdown:
                    try:
                        instance.on_tick()
                    except Exception as e:
                        # TODO error reporing format
                        print(instance.INIT_NAME)
                        print(e)

                if shutdown:
                    tmp.append(instance.INIT_ORDER)
                    # FIXME process is still be visible in top with 0 mem, when it is shutdown
            
            tmp.reverse()
            for n in tmp:

                name = self.modules_instances[n].INIT_NAME
                
                if self.modules_instances[n].IS_PROCESS:
                    self.processes[name].kill()
                    self.processes[name].join(timeout=0.001)
                    self.processes[name].close()
                    del self.processes[name]
                    
                elif self.modules_instances[n].IS_THREAD:
                    del self.threads[name]

                elif self.modules_instances[n].IS_MAIN:
                    self.modules_instances[n]._stop()

                self.modules_instances.remove(self.modules_instances[n])
                print(" {0} is removed".format(name))

            tmp.clear()

            # t_instances = len(self.modules_instances) + 1
            # t_threads = len(self.threads)
            # t_processes = len(self.processes)
            # t_main = t_instances - t_threads - t_processes

            # print(" main process instence(s): {0}\n"
            #       " thread instance(s):       {1}\n"
            #       " subprocess instance(s):   {2}\n"
            #       " total running instances:  {3}"\
            #         .format(t_main, 
            #                 t_threads, 
            #                 t_processes, 
            #                 t_instances
            #                 ))

            time.sleep(1)


    def on_shutdown(self):
        """
            Called each time application is exiting throught atexit
        """
        # TODO make sure threads are exited correctly
        # TODO wait for processes to exit, check for zombie processes
        pass
    

    def shutdown(self):
        self.procmem["StateIO"][0].shutdown = True


    def kill_processes(self):
        pid = None
        if os.path.exists(self.pidfile_path):
            with open(self.pidfile_path, "r") as pidfile:
                pids = pidfile.readlines()
                pidfile.close()
            
            for _pid in pids[::-1]:
                
                pid = _pid[:-1]
                
                while True:
                    if os.path.exists("/proc/" + pid):
                        print("Attempting to shutdown existing controller:", pid)
                        # FIXME hcitool will hangd when sending SIGINT  
                        os.kill(int(pid), signal.SIGINT)
                        continue
                    break


    def class_import(self, mtype, arg, mname=None):
        # TODO check if configs class(s) is already imported in config
        try:
            print(mtype, arg, mname)        
            class_cfg = self.cfg[mtype][mname][arg]
            module_name = class_cfg["ModuleName"]
            cls_name = mtype[:3] + ":" + arg[:3] + ":" + mname + ":" + module_name

        except KeyError:
            print("import error: unknown module class name:", arg)
            sys.exit(1)
        
        self.modules_classes[cls_name] = class_cfg

        try:
            
            if module_name != 'BaseModule': 
                folder_name = mtype[:-1]
                module_path = 'modules.'+ module_name + '.' + folder_name
                class_name = folder_name.capitalize()
                module = __import__(module_path, fromlist=[class_name])
                self.modules_classes[cls_name]["ModuleName"] = getattr(module, class_name)
            else:
                # used for testing
                module_path = 'controller'
                module = __import__(module_path, fromlist=['BaseModule'])
                self.modules_classes[cls_name]["ModuleName"] = getattr(module, 'BaseModule')
        
        except AttributeError:
            print("import error: failed to import class:", cls_name, 'modules.'+ module_name + '.' + mtype[:-1])
            sys.exit(1)
        
        try:
            for m in self.modules_classes[cls_name]['InputMem']:
                if not m in self.procmem:
                    module = __import__('modules.structures', fromlist=[m])
                    mem = getattr(module, m)
                    self.procmem[m] = multiprocessing.Array(mem, 1)
                    print(" shared memory {0} intialized".format(m))

        except AttributeError:
            print("import error: failed to import input shared memory class:", m)
            sys.exit(1)

        try:
            for m in self.modules_classes[cls_name]['OutputMem']:
                if not m in self.procmem:
                    module = __import__('modules.structures', fromlist=[m])
                    mem = getattr(module, m)
                    # mem = getattr(self.imported, m)
                    self.procmem[m] = multiprocessing.Array(mem, 1)
                    print(" shared memory {0} intialized".format(m))

        except AttributeError:
            print("import error: failed to import output shared memory class:", m)
            sys.exit(1)


    def _parse_module_args(self, const):
        if const != 'default':
            args = const.split(":")
            return args[0], args[1]
        else:
            return const, const


    def args_import(self, args):
        if len(sys.argv) == 1:
            # TODO add default args, when no argements provided
            print("default args are not implemented!")
            sys.exit(1)

        if args.stop:
            self.kill_processes()
            sys.exit(0)

        # reset sys args to avoid interference with other modules
        sys.argv = [sys.argv[0]]

        if args.hardware_only:
            self.class_import("interfaces", args.hardware_only, "hardware")
            return

        if args.display_only:
            interface, controller = self._parse_module_args(args.display_only)
            self.class_import("interfaces",  interface, "display")
            self.class_import("controllers", controller, "display") 
            return

        if args.sound_only:
            interface, controller = self._parse_module_args(args.sound_only)
            self.class_import("interfaces", interface, "speaker")
            self.class_import("controllers", controller, "speaker")
            return

        if not args.no_hardware:
            self.class_import("interfaces", 'default', "hardware")

        # must below hardware, to support no-hardware flag
        if args.actuators_only:
            interface, controller = self._parse_module_args(args.actuators_only)
            self.class_import("interfaces", interface, "actuators")
            self.class_import("controllers", controller, "actuators")
            return

        if not args.actuators_only:
            self.class_import("interfaces", 'default', "actuators")
            self.class_import("controllers", 'default', "actuators")

        if not args.no_display:
            self.class_import("interfaces", 'default', "display")
            self.class_import("controllers",'default', "display") 

        if not args.no_sound:
            self.class_import("interfaces", 'default', "speaker")
            self.class_import("controllers", 'default', "speaker")
            
        if args.keyboard:
            self.class_import("interfaces", args.keyboard, "keyboard")
            
        if args.joystick:
            self.class_import("interfaces", args.joystick, "joystick")



