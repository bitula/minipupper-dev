import numpy as np

### TODO Refactor
from .Config import Configuration
from . import NOTController
from . import MovementGroup
from .MovementScheme import MovementScheme # TODO fix import
from modules.Kinematics import Kinematics
from . import State
from . import Command
from . import Utilities
###

from controller.module import BaseModule


def stance_controller(x: float, y:float, dt: float, state: State, config: Configuration):
    
    yaw = x * -config.max_yaw_rate

    pitch = y * config.max_pitch
    deadbanded_pitch = Utilities.deadband(pitch, config.pitch_deadband)
    pitch_rate = Utilities.clipped_first_order_filter(
        state.pitch,
        deadbanded_pitch,
        config.max_pitch_rate,
        config.pitch_time_constant,
    )
    pitch = state.pitch + dt * pitch_rate
    
    return yaw, pitch


class Controller(BaseModule):

    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)

        self.cmd = Command.Command()
        self.config = Configuration()
        self.state = State.State()

        # Create movement group scheme
        moves_list = []
        MovementGroup.appendDanceMovement(moves_list)
        self.movement_ctl = MovementScheme(moves_list)

        # Create controller and user input handles
        self.controller = NOTController.Controller(
            self.config,
            Kinematics.four_legs_inverse_kinematics,
        )
        
        joint_angles = self.shm_numpy_out("ActuatorsIO").joint_angles
        self.shmout_joint_angles = np.frombuffer(joint_angles, dtype=np.float64 ).reshape(3, 4)
        
        self.message_dt = 0.02 # remove this


    def on_tick(self) -> None:
        
        enabled = self.shm_read("SensorsIO", "enable")
        
        # TODO should be disbaled when pupper is back to neutral state from alt modifier
        self.shm_write("ActuatorsIO", "update_legs", enabled)
        
        if not enabled: 
            return
            
        self.cmd.activation = enabled

        height = self.shm_read("SensorsIO", "height")
        self.cmd.height = self.state.height - self.message_dt * self.config.z_speed * height

        roll = self.shm_read("SensorsIO", "roll")
        self.cmd.roll = self.state.roll + self.message_dt * self.config.roll_speed * roll


        yaw = self.shm_read("SensorsIO", "yaw")
        pitch = self.shm_read("SensorsIO", "pitch")
        self.cmd.yaw_rate, self.cmd.pitch = stance_controller(
            yaw, pitch,
            self.message_dt, 
            self.state, 
            self.config
            )

        velx = self.shm_read("SensorsIO", "velx")
        vely = self.shm_read("SensorsIO", "vely")
        _velx = velx * self.config.max_x_velocity
        _vely = vely * -self.config.max_y_velocity
        self.cmd.horizontal_velocity = np.array([_velx, _vely])
        
        self.cmd.trot_event = self.shm_read("SensorsIO", "trot") 
        self.cmd.hop_event = self.shm_read("SensorsIO", "hop")
        self.cmd.gait_switch_event = self.shm_read("SensorsIO", "gait_switch")
        self.cmd.dance_activate_event = self.shm_read("SensorsIO", "dance")
        self.cmd.dance_switch_event = self.shm_read("SensorsIO", "dance_switch")
        
        # print(self.cmd.horizontal_velocity)
        # print(self.cmd.height)
        # print(yaw, pitch)
        # print(mem_in.SensorsIO[0].yaw)

        self.movement_ctl.runMovementScheme(self.cmd.gait_switch_event)           
        food_location = self.movement_ctl.getMovemenLegsLocation()
        attitude_location = self.movement_ctl.getMovemenAttitude()
        robot_speed = self.movement_ctl.getMovemenSpeed()

        # update joint angles state
        self.controller.run(self.state, self.cmd, food_location, attitude_location, robot_speed)
        
        # write to shared array
        self.shmout_joint_angles[:] = self.state.joint_angles