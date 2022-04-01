"""
This module is meant as a testing sandbox for other modules, during implementation.
"""

import numpy as np
import time
import math
from threading import Thread

import environment
import simulaton
import calculations 
import mappers
import dynamixel
import planning


if __name__ == "__main__":

    #region PATH PLANNING
    # pathPlanner = planning.PathPlanner()
    # path = pathPlanner.calculateSpiderBodyPath([0.5, 0.5], [5.5, 3.5], 0.05)
    # bestParams = [0.0323541 , 0.38081064, 0.58683527]
    # selectedPins = pathPlanner.calculateSpiderLegsPositionsFF(path, bestParams)
    # print(selectedPins)
    #endregion

    #region LEG MOVEMENT AND POSITION READING.
    goalPositions = [0.35, 0, 0.035]
    kinematics = calculations.Kinematics()
    spider = environment.Spider()
    trajectoryPlanner = planning.TrajectoryPlanner()
    matrixCalculator = calculations.MatrixCalculator()
    
    motorsIds = [[11, 12, 13], [21, 22, 23], [31, 32, 33], [41, 42, 43], [51, 52, 53]]
    motorsDriver = dynamixel.MotorDriver(motorsIds)

    for motorId in np.array(motorsIds).flatten():
        # motorsDriver.setMotorBaudRate(motorId, 3)
        motorsDriver.setVelocityProfile(motorId, 100, 300)
        motorsDriver.setPositionPids(motorId, 2000, 200, 80)
    
    motorsDriver.enableMotors()
    

    # # for i in range(spider.NUMBER_OF_LEGS):
    # #     motorsDriver.moveLeg(i, goalPositions)  
    # # time.sleep(1)
    # # goalPositions = [0.35, 0, -0.035]
    # # for i in range(spider.NUMBER_OF_LEGS):
    # #     motorsDriver.moveLeg(i, goalPositions)  
    # # time.sleep(1)

    # #endregion

    # #region PARALLEL PLATFORM

    # FIRST MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, 0, 0.038, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, 0, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    
    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)

    # SECOND MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, 0, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, 0.1, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)

    # # THIRD MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, 0.1, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0.1, 0, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    
    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)
    
    # FOURTH MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0.1, 0, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, -0.1, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)

    # FIFTH MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, -0.1, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [-0.1, 0, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)

    # SIXTH MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [-0.1, 0, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, 0.1, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)
    
    # SEVENTH MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, 0.1, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, 0, 0.2, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)

    # EIGHT MOVE
    startLegPositions = [motorsDriver.readLegPosition(legId) for legId in range(spider.NUMBER_OF_LEGS)]
   
    startPose = [0, 0, 0.2, 0, 0, 0]
    T_GS = matrixCalculator.transformMatrixFromGlobalPose(startPose)

    pins = []
    for idx, t in enumerate(spider.T_ANCHORS):
        anchorInGlobal = np.dot(T_GS, t)
        pinMatrix = np.array([
            [1, 0, 0, startLegPositions[idx][0]],
            [0, 1, 0, startLegPositions[idx][1]],
            [0, 0, 1, startLegPositions[idx][2]],
            [0, 0, 0, 1]])
        pinInGlobal = np.dot(anchorInGlobal, pinMatrix)
        pins.append(pinInGlobal[:,3][0:3])

    goalPose = [0, 0, 0.035, 0, 0, 0]
    
    trajectory = trajectoryPlanner.platformLinearTrajectory(startPose, goalPose)
    

    for idx, pose in enumerate(trajectory):
        motorsDriver.movePlatform(pose, pins)
        time.sleep(0.01)
    
    # motorsDriver.disableMotors()

    #endregion

