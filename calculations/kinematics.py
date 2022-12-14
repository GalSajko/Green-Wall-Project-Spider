"""Module for all kinematics calculations.
"""
import math
import numpy as np
import itertools as itt
import numba

from environment import spider
from calculations import transformations as tf
from calculations import mathtools as mathTools


def legForwardKinematics(jointsValues):
    """Calculate forward kinematics for spiders leg, using transformation matrices.  

    :param jointValues: Joint values in radians.
    :return: Transformation matrix from base to end effector.

    Args:
        legId (int):Leg id.
        jointsValues (list): Joints values in radians.

    Returns:
        numpy.ndarray: 4x4 transformation matrix from base to end effector.
    """
    q1, q2, q3 = jointsValues
    L1 = spider.LEGS_DIMENSIONS[0]
    L2 = spider.LEGS_DIMENSIONS[1]
    L3 = spider.LEGS_DIMENSIONS[2]

    return np.array([
        [math.cos(q1) * math.cos(q2 + q3), -math.cos(q1) * math.sin(q2 + q3), math.sin(q1), math.cos(q1) * (L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3))],
        [math.cos(q2 + q3) * math.sin(q1), -math.sin(q1) * math.sin(q2 + q3), -math.cos(q1), (L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.sin(q1)],
        [math.sin(q2 + q3), math.cos(q2 + q3), 0, L2 * math.sin(q2) + L3 * math.sin(q2 + q3)],
        [0, 0, 0, 1]
    ], dtype = np.float32)

def legBaseToThirdJointForwardKinematics(jointValues):
    """Calculate forward kinematics from leg base to third joint.

    Args:
        legId (int): Leg id.
        jointValues (list): Joints values in radians.

    Returns:
        numpy.ndarray: 4x4 transformation matrix from leg-base to third joint.
    """
    q1, q2, _ = jointValues
    L1 = spider.LEGS_DIMENSIONS[0]
    L2 = spider.LEGS_DIMENSIONS[1]

    return np.array([
        [math.cos(q1) * math.cos(q2), -math.cos(q1) * math.sin(q2), math.sin(q1), math.cos(q1) * (L1 + L2 * math.cos(q2))],
        [math.cos(q2) * math.sin(q1), -math.sin(q1) * math.sin(q2), -math.cos(q1), (L1 + L2 * math.cos(q2)) * math.sin(q1)],
        [math.sin(q2), math.cos(q2), 0, L2 * math.sin(q2)],
        [0, 0, 0, 1]
    ], dtype = np.float32)

@numba.njit
def legInverseKinematics(endEffectorPosition, legsDimensions = spider.LEGS_DIMENSIONS):
    """Calculate inverse kinematics for leg, using geometry.

    Args:
        endEffectorPosition (list): Desired position of end effector in leg-base origin.

    Returns:
        tuple: Angles in radians in first, second and third joint.
    """
    L1 = legsDimensions[0]
    L2 = legsDimensions[1]
    L3 = legsDimensions[2]

    # Angle in first joint.
    q1 = math.atan2(endEffectorPosition[1], endEffectorPosition[0])
    # Allow passing from upper workspace of the leg (Xe > 0), to the lower (Xe < 0).
    if endEffectorPosition[0] < 0.0:
        q1 = math.atan2(-endEffectorPosition[1], -endEffectorPosition[0])

    # Position of second joint in leg-base origin.
    secondJointPosition = np.array([
        L1 * math.cos(q1),
        L1 * math.sin(q1),
        0], dtype = np.float32)

    # Vector from second joint to end effector.
    secondJointToEndVector = endEffectorPosition - secondJointPosition

    # Distance between second joint and end effector.
    r = np.linalg.norm(secondJointToEndVector)
    # Angle in third joint, note Pi - acos(x) = acos(-x).
    q3 =  -math.acos(np.round((r**2 - L2**2 - L3**2) / (2 * L2 * L3), 4))
    # Angle in second joint.
    alpha = abs(math.atan2(L3 * math.sin(q3), L2 + L3 * math.cos(q3)))
    xy = np.linalg.norm(secondJointToEndVector[0:2]) if endEffectorPosition[0] >= secondJointPosition[0] else -np.linalg.norm(secondJointToEndVector[0:2])
    gamma = math.atan2(secondJointToEndVector[2], xy)
    q2 = alpha + gamma
    
    return q1, q2, q3

def platformForwardKinematics(legsIds, legsGlobalPositions, legsLocalPoses):
    """Calculate forward kinematics of platform. Use only those legs, that are in contact with pins.

    Args:
        legsIds (list): Ids of used legs.
        legsGlobalPositions (list): Global positions of used legs.
        legsLocalPoses (list):4x4 transformation matrices, representing a legs poses in legs-local origins.

    Returns:
        list: 1x6 list with global xyzrpy values.
    """

    if len(legsIds) != 3 or len(legsGlobalPositions) != 3 or len(legsLocalPoses) != 3:
        print("Use exactly three legs for calculations of forward kinematics.")
        return False
    
    legsLocalPoses = np.array(legsLocalPoses)
    legsGlobalPositions = np.array(legsGlobalPositions)
    l1, l2, l3 = legsLocalPoses
    p1, p2, _ = legsGlobalPositions

    # Compute coordinate system of a wall-plane (in spider's origin)
    l12 = l2[:,3][:3] - l1[:,3][:3]
    l13 = l3[:,3][:3] - l1[:,3][:3]
    l23 = l3[:,3][:3] - l2[:,3][:3]
    n = [
        np.cross(l12, l13) if np.cross(l12, l13)[2] >= 0.0 else np.cross(l13, l12),
        np.cross(l12, l23) if np.cross(l12, l23)[2] >= 0.0 else np.cross(l23, l12),
        np.cross(-l13, -l23) if np.cross(-l13, -l23)[2] >= 0.0 else np.cross(-l23, -l13)
    ]
    n = np.mean(n, axis = 0)
    ez = n / np.linalg.norm(n)
    ex = l12 / np.linalg.norm(l12)
    ey = np.cross(ez, ex)
    P = np.array([ex, ey, ez])

    p12 = p2 - p1
    phi = mathTools.calculateSignedAngleBetweenTwoVectors(p12[:2], np.array([1, 0]))

    # Rotate P for angle phi aroud z axis to align it with global origin.
    rot = np.array([
        [math.cos(phi), -math.sin(phi), 0],
        [math.sin(phi), math.cos(phi), 0],
        [0, 0, 1]
    ])
    Pglobal = np.dot(np.linalg.inv(rot), P)
    Pglobal = np.c_[Pglobal, np.zeros(3)]
    Pglobal = np.r_[Pglobal, [[0, 0, 0, 1]]]

    positions = np.zeros([len(legsLocalPoses), 3])
    for idx, leg in enumerate(legsLocalPoses):
        positions[idx] = np.dot(Pglobal[:3,:3], leg[:,3][:3]) + np.dot(Pglobal[:3,:3], -legsGlobalPositions[idx])
    Pglobal[:,3][:3] = np.mean(positions, axis = 0)

    pose = np.linalg.inv(Pglobal)

    yaw = math.atan2(Pglobal[1, 0], Pglobal[0, 0])
    # Note that roll and pitch are swapped because of spider's axis definition.
    roll = math.atan2(-Pglobal[2, 0], math.sqrt(math.pow(Pglobal[2, 1], 2) + math.pow(Pglobal[2, 2], 2)))
    pitch = math.atan2(Pglobal[2, 1], Pglobal[2, 2])

    x, y, z = pose[:,3][:3]
    xyzrpy = [x, y, z, roll, pitch, yaw]
    
    return xyzrpy

def legJacobi(jointValues):
    """Calculate Jacobian matrix for given leg.

    Args:
        legId (int): Leg id.
        jointValues (list): Joints values in radians.

    Returns:
        numpy.ndarray: 3x3 Jacobian matrix.
    """
    q1, q2, q3 = jointValues
    L1 = spider.LEGS_DIMENSIONS[0]
    L2 = spider.LEGS_DIMENSIONS[1]
    L3 = spider.LEGS_DIMENSIONS[2]

    return np.array([
        [-(L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.sin(q1), -math.cos(q1) * (L2 * math.sin(q2) + L3 * math.sin(q2 + q3)), -L3 * math.cos(q1) * math.sin(q2 + q3)],
        [math.cos(q1) * (L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)), -math.sin(q1) * (L2 * math.sin(q2) + L3 * math.sin(q2 + q3)), -L3 * math.sin(q1) * math.sin(q2 + q3)],
        [0, L2 * math.cos(q2) + L3 * math.cos(q2 + q3), L3 * math.cos(q2 + q3)]
        ], dtype = np.float32)

@numba.njit
def spiderBaseToLegTipForwardKinematics(legId, jointsValues, angleBetweenLegs = spider.ANGLE_BETWEEN_LEGS, radius = spider.BODY_RADIUS, legsDimensions = spider.LEGS_DIMENSIONS):
    """Calculate forward kinematics from spider base to leg-tip.

    Args:
        legId (int): Leg id.
        jointsValues (list): Joints values in radians.

    Returns:
        numpy.ndarray: 4x4 transformation matrix from spider base to leg-tip.
    """
    qb = legId * angleBetweenLegs + math.pi / 2
    q1, q2, q3 = jointsValues
    r = radius
    L1 = legsDimensions[0]
    L2 = legsDimensions[1]
    L3 = legsDimensions[2]

    return np.array([
        [math.cos(q2 + q3) * math.cos(q1 + qb), -math.cos(q1 + qb) * math.sin(q2 + q3), math.sin(q1 + qb), r * math.cos(qb) + (L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.cos(q1 + qb)],
        [math.cos(q2 + q3) * math.sin(q1 + qb), -math.sin(q2 + q3) * math.sin(q1 + qb), -math.cos(q1 + qb), r * math.sin(qb) + (L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.sin(q1 + qb)],
        [math.sin(q2 + q3), math.cos(q2 + q3), 0, L2 * math.sin(q2) + L3 * math.sin(q2 + q3)],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype = np.float32)

@numba.njit
def spiderBaseToLegTipForwardKinematicsMultipleLegs(jointsValues, legs = spider.LEGS_IDS):
    """Calculate legs' positions in spider's origin, for all five legs.

    Args:
        jointsValues (list): 5x3 array of joints values in radians.

    Returns:
        numpy.ndarray: 5x3 array of legs' positions in spider's origin.
    """
    xA = np.zeros((len(legs), 3), dtype = np.float32)
    for idx, leg in enumerate(legs):
        xA[idx] = spiderBaseToLegTipForwardKinematics(leg, jointsValues[idx])[:,3][:3]
    return xA

@numba.njit
def spiderBaseToLegTipJacobi(legId, jointValues, angle = spider.ANGLE_BETWEEN_LEGS, legsDimensions = spider.LEGS_DIMENSIONS):
    """Calculate Jacobian matrix for spider's origin - leg-tip relation.

    Args:
        legId (int): Leg id.
        jointValues (list): Joints values in radians.

    Returns:
        numpy.ndarray: 3x3 Jacobian matrix.
    """
    qb = legId * angle + math.pi / 2
    q1, q2, q3 = jointValues
    L1 = legsDimensions[0]
    L2 = legsDimensions[1]
    L3 = legsDimensions[2]

    return np.array([
        [-(L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.sin(q1 + qb), -math.cos(q1 + qb) * (L2 * math.sin(q2) + L3 * math.sin(q2 + q3)), -L3 * math.cos(q1 + qb) * math.sin(q2 + q3)],
        [(L1 + L2 * math.cos(q2) + L3 * math.cos(q2 + q3)) * math.cos(q1 + qb), -(L2 * math.sin(q2) + L3 * math.sin(q2 + q3)) * math.sin(q1 + qb), -L3 * math.sin(q2 + q3) * math.sin(q1 + qb)],
        [0, L2 * math.cos(q2) + L3 * math.cos(q2 + q3), L3 * math.cos(q2 + q3)]
    ], dtype = np.float32)

def getLegsApproachPositionsInGlobal(legsIds, spiderPose, globalPinsPositions, offset = 0.03):
    """Calculate approach point in global origin, so that gripper would fit on pin.

    Args:
        legsIds (list): Ids of used legs.
        spiderPose (list): Global spider's pose. Could be given as 1x4 array, representing xyzy values or 1x6 array, representing xyzrpy values.
        globalPinsPositions (list): nx3 array of used pins positions in global origin, where n should be same as number of used legs.
        offset (float, optional): Distance from pin to the approach point. Defaults to 0.03.

    Raises:
        ValueError: If lengths of legsIds and globalPinsPositions parameters are not the same.

    Returns:
        numpy.ndarray: nx3 array of approach positions in global origin, where n is number of used legs.
    """
    spiderPose = np.array(spiderPose, dtype = np.float32)

    if len(legsIds) != len(globalPinsPositions):
        raise ValueError("Invalid values of legsIds or pinsPositions parameters.")
    
    approachPointsInGlobal = np.empty([len(legsIds), 3])
    for idx, leg in enumerate(legsIds):
        goalPosition = tf.getLegInLocal(leg, globalPinsPositions[idx], spiderPose)
        goalPosition = np.array(goalPosition, dtype = np.float32)
        legsDimensions = np.copy(spider.LEGS_DIMENSIONS)
        legsDimensions[2] += offset
        jointsValues = legInverseKinematics(goalPosition, legsDimensions)
        T_GA = np.dot(tf.xyzRpyToMatrix(spiderPose), spider.T_ANCHORS[leg])
        approachPointsInLocal = legForwardKinematics(jointsValues)[:,3][:3]
        approachPointsInGlobal[idx] = np.dot(T_GA, np.append(approachPointsInLocal, 1))[:3]

    return approachPointsInGlobal

def getSpiderPose(legsIds, legsGlobalPositions, qA):
    """Calculate spider's pose in global origin. If more than three legs are given, it calculates spider's pose from each
    combination of these three legs. Finally pose is determined as mean value of all calculations.

    Args:
        legsIds (list): Ids of legs to use for calculating spider's pose. Should not use less than three legs.
        legsGlobalPositions (list): nx3 array of x, y, z positions of used legs in global origin, where n should be the same as length of legsIds.

    Returns:
        list: 1x6 array of xyzrpy pose.
    """
    legsGlobalPositions = np.array(legsGlobalPositions)
    poses = []
    for legsSubset in itt.combinations(legsIds, 3):
        legsSubset = np.array(legsSubset)
        subsetIdxs = [legsIds.index(leg) for leg in legsSubset]
        # Skip calculations if all three selected legs are on the same line.
        if not (np.diff(legsGlobalPositions[subsetIdxs][:, 0]).any() and np.diff(legsGlobalPositions[subsetIdxs][:, 1]).any()):
            continue
        jointsValues = qA[legsSubset]
        legsPoses = np.zeros([3, 4, 4])
        for idx, leg in enumerate(legsSubset):
            legsPoses[idx] = spiderBaseToLegTipForwardKinematics(leg, jointsValues[idx])
        poses.append(platformForwardKinematics(legsSubset, legsGlobalPositions[(subsetIdxs)], legsPoses))
    pose = np.mean(np.array(poses), axis = 0)

    return pose