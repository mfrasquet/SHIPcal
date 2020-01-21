#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 17:33:29 2019

@author: miguel
"""
import numpy as np

def Rec_loss(REC_type,DELTA_T,theta,DNI):
    if REC_type==1:
        #Schott PTR70 
        Q_loss_rec=0.00154*DELTA_T**2+0.2021*DELTA_T-24.899+((.00036*DELTA_T**2)+.2029*DELTA_T+24.899)*(DNI/900)*np.cos(theta)
        if Q_loss_rec<=0:
            Q_loss_rec=0
    return[Q_loss_rec]