"""File for storing global variables.
"""
CONTROLLER_FREQUENCY = 70.0
FORCE_DAMPING = 0.01
K_P_FORCE = 0.03
K_P = 25.0
K_D = 1.8
K_ACC = 0.18

SPIDER_ORIGIN = 'spider'
LEG_ORIGIN = 'local'
GLOBAL_ORIGIN = 'global'

BEZIER_TRAJECTORY = 'bezier'
MINJERK_TRAJECTORY = 'minJerk'

FORCE_DISTRIBUTION_DURATION = 1.0

FORCE_MODE = 'forceMode'
IMPEDANCE_MODE = 'impedanceMode'

WORKING_STATE = 'working'
RESTING_STATE = 'resting'
TRANSITION_STATE = 'transition'

WORKING_THREAD_NAME = 'working_thread'
TRANSITION_THREAD_NAME = 'transition_thread'
RESTING_THREAD_NAME = 'resting_thread'
SAFETY_THREAD_NAME = 'safety_thread'
CONTROL_THREAD_NAME = 'control_thread'
UPDATE_DICT_THREAD_NAME = 'update_dict_thread'
UPDATE_DATA_THREAD_NAME = 'update_data_thread'
STATE_DICT_POSE_KEY = 'pose'
STATE_DICT_PINS_KEY = 'pins'

SERVER_IP = '192.168.1.20'
ARDUIONO_IP_LIST = ['192.168.1.11','192.168.1.12','192.168.1.13','192.168.1.14','192.168.1.15','192.168.1.16']

global visualisationValues
global dataJson
global poseData
global arduinoValues
global arduinoTimes
global minValues

SENSOR_IDS = [54, 55, 56, 57, 58, 59]
GET_SENSOR_POSITION_ADDR = 'http://192.168.1.20:5000/zalij'
POST_SPIDER_POSITION = 'http://192.168.1.20:5000/spiderPos'
NUMBER_OF_WATERING_BEFORE_REFILL = 15
WATERING_TIME = 12.0
REFILL_TIME = 67.0
