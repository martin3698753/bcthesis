import logging
import sys
import os
import time
import numpy as np
from threading import Event
import random
import datetime
import read

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

current_time = time.localtime()
current_path = 'data/'+str(current_time.tm_mday)+'-'+str(current_time.tm_mon)+'-'+str(current_time.tm_hour)+'-'+str(current_time.tm_min)+'-'+str(current_time.tm_sec)

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def acc_callback(timestamp, data, logconf):
    print(data)

    filename = current_path+'/'+logconf.name+'.csv'
    names = np.array(list(data.items()))
    names = names[:,0]

    if not os.path.exists(filename):
        f = open(filename, 'w')
        f.write('time,')
        for n in names:
            f.write(n+',')
        f.write('\n')
        f.close()

    f = open(filename, 'a')
    f.write(str(timestamp)+',')
    for n in names:
        f.write(str(data[n])+',')
    f.write('\n')
    f.close()

def move_prep(scf):
    #IDK what this actually do
    scf.cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    scf.cf.param.set_value('kalman.resetEstimation', '0')
    time.sleep(2)

    # Arm the Crazyflie
    scf.cf.platform.send_arming_request(True)
    time.sleep(1.0)

    for y in range(10):
        scf.cf.commander.send_hover_setpoint(0, 0, 0, y / 25)
        time.sleep(0.1)
    print('Taking off')

    for _ in range(20):
        scf.cf.commander.send_hover_setpoint(0, 0, 0, 0.4)
        time.sleep(0.1)
    print('In air')


if __name__ == '__main__':
    joystick = read.main()

    #Create dir with date
    if not os.path.exists(current_path):
        os.makedirs(current_path)
    else:
        print("Data path already exist, WTF is happenin?")
        sys.exit()

    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        acconf = LogConfig(name='acceleration', period_in_ms=10)
        acconf.add_variable('acc.x', 'float')
        acconf.add_variable('acc.y', 'float')
        acconf.add_variable('acc.z', 'float')
        scf.cf.log.add_config(acconf)
        acconf.data_received_cb.add_callback(acc_callback)

        posconf = LogConfig(name='position', period_in_ms=10)
        posconf.add_variable('stateEstimate.x', 'float')
        posconf.add_variable('stateEstimate.y', 'float')
        posconf.add_variable('stateEstimate.z', 'float')
        scf.cf.log.add_config(posconf)
        posconf.data_received_cb.add_callback(acc_callback)

        batconf = LogConfig(name='battery', period_in_ms=10)
        batconf.add_variable('pm.vbat', 'float')
        scf.cf.log.add_config(batconf)
        batconf.data_received_cb.add_callback(acc_callback)

        move_prep(scf)

        acconf.start()
        posconf.start()
        batconf.start()


        height = 0.4
        while not (read.stop(joystick)):
            c = 8
            height += read.up_down(joystick)
            x, y, z = read.read(joystick)
            scf.cf.commander.send_zdistance_setpoint(x*c, y*c, z*c, height)
        print('Landing')

        # for _ in range(50):
        #     cf.commander.send_hover_setpoint(0.5, 0, -36 * 2, 0.4)
        #     time.sleep(0.1)
        #
        # for _ in range(20):
        #     cf.commander.send_hover_setpoint(0, 0, 0, 0.4)
        #     time.sleep(0.1)
        #
        for y in range(10):
            scf.cf.commander.send_hover_setpoint(0, 0, 0, (10 - y) / 25)
            time.sleep(0.1)

        scf.cf.commander.send_stop_setpoint()
        # Hand control over to the high level commander to avoid timeout and locking of the Crazyflie
        scf.cf.commander.send_notify_setpoint_stop()

        acconf.stop()
        posconf.stop()
        batconf.stop()