import ctypes
import os
'''import time'''
from enum import Enum

file_directory = os.path.dirname(os.path.abspath(__file__))
G4Track = ctypes.CDLL(os.path.join(file_directory, "G4Track.dll"))


# Structure to receive position & orientation from each sensor with fields:
#   id:     zero-based sensor number
#   pos:    position [x, y, z] in inch or cm, according to g4_set_query
#   ori:    orientation in Euler (asimuth, elevation, roll) or in quaternions according to configuration
class G4SensorFrameData(ctypes.Structure):
    _fields_ = [("id", ctypes.c_uint32),
                ("pos", ctypes.c_float * 3),
                ("ori", ctypes.c_float * 4)]


# Structure used by 'g4_get_frame_data' to retrieve most recent frame's tracker data with fields:
#   hub:                hub id as reported by system
#   frame:              frame number which position & orientation corresponds
#   stationMap:         bit-map to indicate which sensor is active, 1 if its active
#   dig_io:             8-bit map that corresponds to the digital I/O-ports
#   G4_sensor_per_hub:  array of G4SensorFrameData that holds info of each sensor
class G4FrameData(ctypes.Structure):
    _fields_ = [("hub", ctypes.c_uint32),
                ("frame", ctypes.c_uint32),
                ("stationMap", ctypes.c_uint32),
                ("dig_io", ctypes.c_uint32),
                ("G4_sensor_per_hub", G4SensorFrameData * 3)]


# Structure used to retrieve position & orientation of each source with fields:
#   id:     zero-based if of the source (between 0 and 7)
#   freq:   zero-based frequency value (between 0 and 7: 0->A, 1->B, ...)
#   pos:    position [x,y,z] of the source, in inch or cm according to the configuration
#   att:    orientation Euler [azimuth, elevation, pitch) or in quaternions (4 elements)
class G4SRCMAP(ctypes.Structure):
    _fields_ = [("id", ctypes.c_uint),
                ("freq", ctypes.c_uint),
                ("pos", ctypes.c_float * 3),
                ("att", ctypes.c_float * 4)]


class ERROR(Enum):
    G4_ERROR_NONE = 0
    G4_ERROR_NO_FRAME_DATA_AVAIL = -100
    G4_ERROR_UNSUPPORTED_ACTION = -99
    G4_ERROR_UNSUPPORTED_TYPE = -98
    G4_ERROR_UNSUPPORTED_COMMAND = -97
    G4_ERROR_INVALID_STATION = -96
    G4_ERROR_NO_CONNECTION = -95
    G4_ERROR_NO_HUBS = -94
    G4_ERROR_FRAMERATE_SET = -93
    G4_ERROR_MEMORY_ALLOCATION = -92
    G4_ERROR_INVALID_SYSTEM_ID = -91
    G4_ERROR_SRC_CFG_FILE_OPEN = -90
    G4_ERROR_INVALID_SRC_CFG_FILE = -89
    G4_ERROR_UNABLE_TO_START_TIMER = -88
    G4_ERROR_HUB_NOT_ACTIVE = -87
    G4_ERROR_SYS_RESET_FAIL = -86
    G4_ERROR_DONGLE_CONNECTION = -85
    G4_ERROR_DONGLE_USB_CONFIGURATION = -84
    G4_ERROR_DONGLE_USB_INTERFACE_0 = -83
    G4_ERROR_DUPLICATE_SYS_IDS = -82
    G4_ERROR_INVALID_WILDCARD_USE = -81
    G4_ERROR_TOTAL = -80


# uint32_t g4_init_sys(int* pDongleId,const char* src_cfg_file,void* reserved)
G4Track.g4_init_sys.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_void_p]
G4Track.g4_init_sys.restype = ctypes.c_uint32

# void g4_close_tracker(void)
G4Track.g4_close_tracker.argtypes = ()
G4Track.g4_close_tracker.restype = None

# uint32_t g4_get_frame_data(G4_FRAMEDATA* fd_array, int sysId, const int* hub_id_list, int num_hubs)
G4Track.g4_get_frame_data.argtypes = [ctypes.POINTER(G4FrameData), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.c_int]
G4Track.g4_get_frame_data.restype = ctypes.c_uint32


# Initialize the G4Track Libray. It must be called before any interaction using this library.
# Input:
#       scr_cfg_file:   source configuration file (.g4c)
# Output:
#       status:         returns True if the connection is active
#       dongle_id:      system ID
def initialize_system(src_cfg_file):
    G4Track = ctypes.CDLL(os.path.join(file_directory, "G4Track.dll"))

    dongle_id_C = ctypes.c_int()
    status = G4Track.g4_init_sys(ctypes.byref(dongle_id_C), src_cfg_file.encode('utf-8'), ctypes.c_void_p(None))

    # numbers are still unsigned --> convert to signed by substracting 2^32 or 0x100000000
    if status > 0x7FFFFFFF:
        status = status - 0x100000000

    if status == ERROR.G4_ERROR_NONE.value:
        return True, dongle_id_C
    elif status == ERROR.G4_ERROR_NO_CONNECTION.value:
        print(f"Error: No connection possible (status code: {status}).")
        return False, None
    else:
        print(f"Error: Unexpected status code {status}.")
        return False, None


def close_sensor():
    G4Track = ctypes.CDLL(os.path.join(file_directory, "G4Track.dll"))
    G4Track.g4_close_tracker()
    del G4Track


# Eanbles the program to retrieve position & orientation from the hub
# Input:
#       system_id:      source configuration file (.g4c)
#       hub_id_list:    array of hub ids the user is requesting data from
#       num_hubs:       number of hubs
# Output:
#       fd:             return structure G4FrameData with the data of the hub
#       res:            32-bit value where the upper 16-bit word contains the total number of
#                       active hubs on the system, and the lower 16-bit word contains the number of hubs worth
#                       of data returned in fd_array
def get_frame_data(system_id, hub_id_list):
    G4Track = ctypes.CDLL(os.path.join(file_directory, "G4Track.dll"))

    hubs = 1
    fd = G4FrameData()
    hub_id_c = (ctypes.c_int * len(hub_id_list))(*hub_id_list)
    res = G4Track.g4_get_frame_data(ctypes.byref(fd), system_id, hub_id_c, 1)
    return fd, res


def extract_hub_info(value):
    # Ensure value is treated as a 32-bit integer
    value = value & 0xFFFFFFFF  # Mask to 32 bits

    # Extract upper 16 bits (total number of active hubs)
    total_active_hubs = (value >> 16) & 0xFFFF  # Shift right by 16 bits and mask

    # Extract lower 16 bits (number of hubs worth of data)
    hubs_data_count = value & 0xFFFF  # Mask to get lower 16 bits

    return total_active_hubs, hubs_data_count


'''
src_cfg_file = os.path.join(file_directory, "first_calibration.g4c")
connected, dongle_id = initialize_system(src_cfg_file)


start_time = time.time()
elapsed_time = time.time() - start_time
if connected:
    print(f'Status of connection with id {dongle_id.value}: {connected}')

    while elapsed_time < 20:
        frame_data, res = get_frame_data(dongle_id, [0])
        elapsed_time = time.time() - start_time

        if res != 0 and extract_hub_info(res) == (1,1):
            print(f"Station Map: {frame_data.stationMap:#010b}")

            for i, sensor in enumerate(frame_data.G4_sensor_per_hub):
                print(f"Sensor {i}:")
                #print(f"  ID: {sensor.id}")
                print(f"  Position: (x: {sensor.pos[0]}, y: {sensor.pos[1]}, z: {sensor.pos[2]})")
                #print(
                #    f"  Orientation: (qx: {sensor.ori[0]}, qy: {sensor.ori[1]}, qz: {sensor.ori[2]}, qw: {sensor.ori[3]})")


close_sensor()
del G4Track
'''
