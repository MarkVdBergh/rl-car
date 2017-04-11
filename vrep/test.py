# Import Libraries:
import vrep
import sys
import time
import numpy as np
import math
import matplotlib.pyplot as plt


class RlBot(object):
    def __init__(self):
        # just in case, close all opened connections
        vrep.simxFinish(-1)

        self.client_id = vrep.simxStart(
            '127.0.0.1', 19997, True, True, 5000, 5)

        if self.client_id != -1:  # check if client connection successful
            print('Connected to remote API server')
        else:
            print('Connection not successful')
            sys.exit('Could not connect')

        # Restart the simulation
        vrep.simxStopSimulation(self.client_id, vrep.simx_opmode_blocking)
        vrep.simxStartSimulation(self.client_id, vrep.simx_opmode_blocking)

        # Get handles
        self.get_handles()

    def get_handles(self):
        # retrieve motor  handles
        _, self.left_motor_handle = vrep.simxGetObjectHandle(
            self.client_id, 'Pioneer_p3dx_leftMotor', vrep.simx_opmode_blocking)
        _, self.right_motor_handle = vrep.simxGetObjectHandle(
            self.client_id, 'Pioneer_p3dx_rightMotor', vrep.simx_opmode_blocking)

        # empty list for handles
        self.proxy_sensors = []

        # for loop to retrieve proxy sensor arrays and initiate sensors
        for i in range(16):
            _, sensor_handle = vrep.simxGetObjectHandle(
                self.client_id, 'ultrasonic_sensor#' + str(i),
                vrep.simx_opmode_blocking)
            # Append to the list of sensors
            self.proxy_sensors.append(sensor_handle)

        # empty list for handles
        self.light_sensors = []

        # for loop to retrieve light sensor arrays and initiate sensors
        for i in range(8):
            _, sensor_handle = vrep.simxGetObjectHandle(
                self.client_id, 'light_sensor#' + str(i),
                vrep.simx_opmode_blocking)
            # Append to the list of sensors
            self.light_sensors.append(sensor_handle)

    def distroy(self):
        vrep.simxStopSimulation(self.client_id, vrep.simx_opmode_blocking)

    def reset(self):
        # Restart the simulation
        vrep.simxStopSimulation(self.client_id, vrep.simx_opmode_blocking)
        vrep.simxStartSimulation(self.client_id, vrep.simx_opmode_blocking)

    def step(self, action):
        observations = {}
        observations['proxy_sensor_vals'] = []
        observations['light_sensor_vals'] = []

        # fetch the vals of proxy sensors
        for sensor in self.proxy_sensors:
            _, _, detectedPoint, _, _ = vrep.simxReadProximitySensor(
                self.client_id, sensor, vrep.simx_opmode_blocking)
            # Append to list of values
            observations['proxy_sensor_vals'].append(
                np.linalg.norm(detectedPoint))

        # fetch the vals of light sensors
        for sensor in self.light_sensors:
            # Fetch the initial value in the suggested mode
            _, _, image = vrep.simxGetVisionSensorImage(
                self.client_id, sensor, 1, vrep.simx_opmode_blocking)
            # Append to the list of values
            observations['light_sensor_vals'].append(image)

        # Activate the motors
        vrep.simxSetJointTargetVelocity(
            self.client_id, self.left_motor_handle, action[0], vrep.simx_opmode_blocking)
        vrep.simxSetJointTargetVelocity(
            self.client_id, self.right_motor_handle, action[1], vrep.simx_opmode_blocking)

        return observations


rl_bot = RlBot()

for i in range(10000):
    observations = rl_bot.step([1, 1])
    print(observations['proxy_sensor_vals'])
    print(observations['light_sensor_vals'])

rl_bot.distroy()