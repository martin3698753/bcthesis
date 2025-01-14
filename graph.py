import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import math
import os
import glob
import pandas as pd
import pickdir
import maketab as mt
import makedata as md
import neuron
from neuron import window
from sklearn import preprocessing
import lstm

def norm(data):
    min_val = np.min(data)
    max_val = np.max(data)
    normalized_data = (data - min_val) / (max_val - min_val)
    return normalized_data

def denorm(normalized_data, original_min, original_max):
    """
    Denormalizes data that was previously normalized using min-max scaling.

    Args:
        normalized_data: The normalized data (NumPy array or single value).
        original_min: The minimum value of the original dataset.
        original_max: The maximum value of the original dataset.

    Returns:
        The denormalized data (NumPy array or single value).
    """

    denormalized_data = normalized_data * (original_max - original_min) + original_min
    return denormalized_data


if __name__ == '__main__':
    #path_dir = pickdir.choose_directory('data')+'/'
    #path_dir = 'data/26-11-24/'
    path_dir = 'data/8-1-1/'
    battery = mt.battery(path_dir)
    t = mt.time(path_dir)*0.001
    motor = mt.readcsv(path_dir+'motor.csv')
    motor = motor = (motor/65535)*100
    thr = mt.thrust(path_dir)
    av = mt.ang_vel(path_dir)
    #me = thr*0.05*av*0.1
    me = ((thr[1]/4)*av[1] + (thr[2]/4)*av[2] + (thr[3]/4)*av[3] + (thr[4]/4)*av[4])*0.047*0.1*0.05
    mech = np.sum(me)

    mech_pred = 61*t -92

    # work = norm(work)
    # battery = norm(battery)
    #work = mt.sum_ar(energy)
    # work = norm(work)
    # x, y = window(power, battery)
    # neuron.train_lin(x, y)
    # pred = neuron.predict_lin(power)
    # plt.plot(t, av[1], label='m1 RPM')
    # plt.plot(t, av[2], label='m2 RPM')
    # plt.plot(t, av[3], label='m3 RPM')
    # plt.plot(t, av[4], label='m4 RPM')
    #plt.plot(t, me, label='Výkon (W)')
    #plt.plot(t, energy, label='battery energy (J)')
    #plt.plot(t, work, label='work (J)')
    #plt.plot(t, battery, label='baterie (V)')
    plt.plot(t, mt.sum_ar(me), label='Energie (J)')
    #plt.plot(t, mech_pred, label='61*t-92')
    #plt.scatter(t, pred, s=.5, label='prediction')
    #plt.ylim(2.5,4.5)
    #plt.xlim(50000, 60000)
    plt.xlabel("čas (s)")
    #plt.text(1, 1, ('Flight time = ', battery.size*0.1/60, ' s\n', 'Consumed power = ', work_sum[-1], ' J'), fontsize=12, color='red')
    #plt.legend(title=('Čas letu byl '+str(round(battery.size*0.1/60, 3))+' min\n'+'Energie = '+str(round(mech, 3))+' J'))
    #plt.legend(title=('A = '+str(round(slope))+'\n'+'B = '+str(round(intercept))))
    plt.legend()
    plt.show()
    #lstm.init(t, battery)

    # net = LNU()
    # result = net.train(power, battery)
    #
    # print("Model Performance:")
    # print(f"Mean Squared Error: {result['mse']:.4f}")
    # print(f"Mean Absolute Error: {result['mae']:.4f}")
    # net.visual(result)
