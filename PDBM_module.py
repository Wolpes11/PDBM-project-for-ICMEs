import os
import re
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.io as scio
from scipy.optimize import bisect

def F_zero(t,gamma,r0,v0,r1,w):
    # compute F(w) as in Formula (4) of Napoletano et al. 2018
    Sol_rad= 695700.0 # [km]
    r0=r0*Sol_rad   # in [km]
    r1=r1*Sol_rad   # distance Sun-target in [km]
    # Different condition based on decelerated/accelerated regime
    if v0 < w:
        gamma=-gamma

    p1=1+gamma*(v0-w)*t
    Funz=(1.0/gamma)*math.log(p1)+w*t+r0-r1 #F(w)

    return Funz

def Zero(gamma,r0,v0,r1,w):
    T0=1.0           #in hours
    T1=4.0E4         #in hours
    T0=T0*3600   #in seconds
    T1=T1*3600   #in seconds
    #Starting Bisection routin
    Fw0=F_zero(T0,gamma,r0,v0,r1,w)
    Fw1=F_zero(T1,gamma,r0,v0,r1,w)
    if Fw0*Fw1 >0:
        return 60.0
    else:
        N_iter=20
        for i in range(0,N_iter):
            Th=(T0+T1)/2
            Fw0=F_zero(T0,gamma,r0,v0,r1,w)
#            print Fw0
            Fwh=F_zero(Th,gamma,r0,v0,r1,w)
#            print Fwh
            if Fw0*Fwh <0:
                T1=Th
            else:
                T0=Th
        #End of Bisection routine
        return ((T0+T1)/2)/3600                    #in hours

def DBM(v0,wind,gamma,r0=20.0,r1=1.0):
    ## Drag-Based Model function
    ##
    ## Compute the transit time and the arrival speed of an ICME at a given point
    ## in the inner heliosphere.
    ##
    ## Input
    ## - v0: initial CME speed (km/s).
    ## - wind: constant solar wind background speed (km/s).
    ## - gamma: drag parameter (1/km). In unit of 1e-7.
    ## - r0: CME initial position (solar radii). Default 20
    ## - r1: Arrival position of the CME (AU). Default 1AU
    ##
    ##
    ## Output
    ## - TT: CME transit time, in hours (length=N).
    ## - V1: CME arrival speed, in km/s (length=N).
    ##
    ##
    r1 = r1*215.0
    gamma = gamma*1e-7

    TT = Zero(gamma,r0,v0,r1,wind)

    DV = (v0-wind)
    if DV > 0:
        G=3600.0*gamma
    else:
        G=-3600.0*gamma

    V1 = (DV/(1.+G*DV*TT))+wind

    return TT, V1

def P_DBM(v0,sv0,w0,dw0,gam,R_start=20.0,dR_start=4.0,R_target=1.0,N=1000):
    ## Probabilistic Drag-Based Model function
    ##
    ## Compute the transit time and the arrival speed of an ICME at a given point
    ## in the inner heliosphere starting from an ensemble of 'synthetic' CMEs
    ## generated using commonly adopted PDFs
    ##
    ## Input
    ## - v0: mean value of initial CME speed (km/s).
    ## - sv0: sigma of the CME initial speed (km/s).
    ## - w0: mean value of the solar wind background speed (km/s).
    ## - dw0: sigma of the solar wind speed (km/s).
    ## - gam: mean value of drag parameter (1/km). In unit of 1e-7.
    ## - R_start: mean value of the CME initial position of CME (solar radii). Default 20
    ## - dR_start: sigma of the CME initial position (solar radii). Default 4
    ## - R_target: Arrival position of the CME (AU). Default 1AU
    ## - N: number of iterations (number of output samples). Default 1000
    ##
    ##
    ## Output
    ## - T_array: array of CME transit times, in hours (length=N).
    ## - V_array: array of CME arrival speed, in km/s (length=N).
    ##
    ##
    mu_g, sigma_g = np.log(gam), 1.01
    gamma_array = np.random.lognormal(mu_g, sigma_g, N) #Drag parameter from lognormal

    mu_w, sigma_w = w0, dw0
    wind_array=np.random.normal(mu_w, sigma_w, N) #Solar wind speed from Gaussian

    mu_v0, sigma_v0 = v0, sv0
    v0_array=np.random.normal(mu_v0, sigma_v0, N) #Initial speed from Gaussian

    mu_r0, sigma_r0 = R_start, dR_start
    r0_array=np.random.normal(mu_r0, sigma_r0, N) #Initial position from Gaussian

    r1_array=np.ones_like(gamma_array)*R_target #Arrival position is constant

    T_array=np.zeros_like(gamma_array)
    V_array=np.zeros_like(gamma_array)

    for i in range(0,len(r0_array)):
        T_array[i], V_array[i] = DBM(v0_array[i],wind_array[i],gamma_array[i],r0_array[i],r1_array[i])

    return T_array, V_array


## Examples
# TTa, V1a = DBM(1000,400,0.8)
# TTb, V1b = P_DBM(1000,100,400,33,0.8)
