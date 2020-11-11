# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:58:48 2020

@author: zefyr
"""

import sys
import math
import IMU

# IMU values
RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9         # Median filter table size for magnetometer. Higher = smoother but a longer delay

class PlayerPi:
    def __init__(self, playerId):
        try:
            # This is a dummy number, how do we set each player number distinctly
            # without hardcoding?
            self.playerId = 1
            self.imu = BerryIMU()
        except:
            print("An error occurred initializing PlayerPi")
            
    def getRotation(self):
        '''
        Gets rotation information from the BerryIMU.
        '''
        try:
            rotation = self.imu.getRotation()
            return rotation
        except:
            print("Error getting direction information from the camera")
    
    def pack(self, rotation):
        '''
        Packs a message for the central node containing player number and rotation.
        
        Returns the message for transmission.
        '''
        try:
            #0 is a dummy value, this should be updated with message packing code
            message = 0
            return message
        except:
            print("Error sending package to primary node")
    
    def unpack(self, package):
        '''
        Unpacks message from the central node to obtain permission to send more
        messages.
        
        Return true to give permission to PC to transmit messages again.
        '''
        try:
            # Message data may contain info that is only relevant for the
            # playerPC, so this is just looking for the current rotation
            # cooldown state. If on cooldown rotation, the pi can't send.
            # 1 is a dummy value
            canSend = 1
            return canSend
        except:
            print("Error getting package from primary node")

class BerryIMU:
    def __init__(self):
        try:
            self.acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
            self.acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
            self.acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
            self.acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
            self.acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
            self.acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
            
            self.oldXAccRawValue = 0
            self.oldYAccRawValue = 0
            self.oldZAccRawValue = 0
            
            IMU.detectIMU()     #Detect if BerryIMU is connected.
            if(IMU.BerryIMUversion == 99):
                print(" No BerryIMU found... exiting ")
                sys.exit()
            IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass
        except:
            print("Error initializing IMU")
            
    def getRotation(self):
        '''
        Looks for a rotation command, and when one is found, classifies and
        returns it.
        '''
        try:
            #Loop until retrieving a rotation
            while True:
                #Read the accelerometer,gyroscope and magnetometer values
                ACCx = IMU.readACCx()
                ACCy = IMU.readACCy()
                ACCz = IMU.readACCz()
                
                ###############################################
                #### Apply low pass filter ####
                ###############################################
                ACCx =  ACCx  * ACC_LPF_FACTOR + self.oldXAccRawValue*(1 - ACC_LPF_FACTOR);
                ACCy =  ACCy  * ACC_LPF_FACTOR + self.oldYAccRawValue*(1 - ACC_LPF_FACTOR);
                ACCz =  ACCz  * ACC_LPF_FACTOR + self.oldZAccRawValue*(1 - ACC_LPF_FACTOR);
            
                self.oldXAccRawValue = ACCx
                self.oldYAccRawValue = ACCy
                self.oldZAccRawValue = ACCz
                
                #########################################
                #### Median filter for accelerometer ####
                #########################################
                # cycle the table
                for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
                    self.acc_medianTable1X[x] = self.acc_medianTable1X[x-1]
                    self.acc_medianTable1Y[x] = self.acc_medianTable1Y[x-1]
                    self.acc_medianTable1Z[x] = self.acc_medianTable1Z[x-1]
            
                # Insert the lates values
                self.acc_medianTable1X[0] = ACCx
                self.acc_medianTable1Y[0] = ACCy
                self.acc_medianTable1Z[0] = ACCz
            
                # Copy the tables
                acc_medianTable2X = self.acc_medianTable1X[:]
                acc_medianTable2Y = self.acc_medianTable1Y[:]
                acc_medianTable2Z = self.acc_medianTable1Z[:]
            
                # Sort table 2
                acc_medianTable2X.sort()
                acc_medianTable2Y.sort()
                acc_medianTable2Z.sort()
            
                # The middle value is the value we are interested in
                ACCx = acc_medianTable2X[int(ACC_MEDIANTABLESIZE/2)];
                ACCy = acc_medianTable2Y[int(ACC_MEDIANTABLESIZE/2)];
                ACCz = acc_medianTable2Z[int(ACC_MEDIANTABLESIZE/2)];
                
                #Normalize accelerometer raw values.
                accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
                accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
                #accZnorm = ACCz/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
            
            
                #Calculate pitch and roll            
                pitch = math.asin(accXnorm)*RAD_TO_DEG
                roll = math.asin(accYnorm)*RAD_TO_DEG
                #zdir is not yaw. Corresponds to pi/2 rad or 90 deg when IMU is upright, negative when upside down.
                #zdir = math.asin(accZnorm)*RAD_TO_DEG
                #roll = -math.asin(accYnorm/math.cos(pitch))*RAD_TO_DEG
            
                rotation = 0
                #Simple classifier
                if roll > 50 and abs(pitch) < 30: rotation = "v"
                elif roll < -50 and abs(pitch) < 30: rotation = "^"
                elif pitch > 50 and abs(roll) < 30: rotation = "<"
                elif pitch < -50 and abs(roll) < 30: rotation = ">"
                
                if rotation:
                    return rotation
        except:
            print("Error getting rotation from IMU")