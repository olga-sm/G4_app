import time
from G4Track import *

file_directory = os.path.dirname(os.path.abspath(__file__))
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
            for i, sensor in enumerate(frame_data.G4_sensor_per_hub):
                if i <= 2:
                    print(f"Sensor {i}:")
                    print(f"  Position: (x: {sensor.pos[0]}, y: {sensor.pos[1]}, z: {sensor.pos[2]})")
                    print(f"  Orientation: (qx: {sensor.ori[0]}, qy: {sensor.ori[1]}, "f"qz: {sensor.ori[2]})")


close_sensor()
