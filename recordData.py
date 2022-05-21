import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import serial
from serial.serialutil import SerialException

port = '/dev/cu.usbserial-A50285BI'  # check first with arduino software
baudrate = 1000000  # needs to fit setting in arduino code
timeout = 0.1  # in seconds
debug = True

measurements_to_record = 2 * 40 * 50 + 10 # 5 minutes = 30k lines + 10 lines just in case...

WAITING_FOR_SETTINGS = 0
RECEIVING_SETTINGS = 1
RECEIVING_DATA = 2
RECORDING_DATA = 3
RECORDING_ENDED = 4


a = 5 # Pitch 1
b = 5 # Yaw 1
c = 5 # Pitch 2
d = 5 # Yaw 2


def main():
    while True:
        print(f'Trying to  connect to Serial port ({port}, {baudrate}, {timeout}) ...', end='')
        ser = None
        error = False
        state = WAITING_FOR_SETTINGS
        out_file = None
        line_count = 0
        sensor_number = 0
        while not ser:
            try:
                ser = open_serial()
                print(' Done.')
            except SerialException as ex:
                if debug:
                    print(ex)
                ser = None
                sleep(1)
        try:
            while ser.isOpen() and state != RECORDING_ENDED:
                if ser.in_waiting == 0:
                    sleep(0.0005)
                    continue
                try:
                    line = ser.readline().decode('ascii').strip()
                    # print(f'LINE: {line}')
                except UnicodeDecodeError:  # catch error and ignore it
                    raise Exception('ERROR: There seems to be an Baud rate mismatch.')
                if state == WAITING_FOR_SETTINGS:
                    if line.startswith('#'):
                        state = RECEIVING_SETTINGS
                        print('Receiving settings...')
                        now = datetime.now()
                        os.makedirs(f'./Fire_200m/{now.strftime("%Y-%m-%d")}', exist_ok=True)
                        out_file = open(f'./Fire_200m/{now.strftime("%Y-%m-%d")}/{now.strftime("%Y-%m-%d-%H-%M-%S_")}{a}-{b}-{c}-{d}.csv','w')
                    else:
                        # skip lines until a comment line indicates start of settings
                        continue
                if state == RECEIVING_SETTINGS:
                    if line.startswith('#'):
                        # receiving a settings line
                        out_file.write(line)
                        out_file.write('\n')
                    else:
                        state = RECEIVING_DATA
                        print('Settings part ended. Received first data line.')
                if state == RECEIVING_DATA:
                    if line.startswith('#'):
                        # receiving a settings line
                        raise Exception('got commented line while receiving data.')
                    else:
                        try:
                            sensor_number = analyze_data_line(line, sensor_number)
                            state = RECORDING_DATA
                            out_file.write(f'#s {datetime.now().isoformat()}\n')
                            print(f'Started Recording after {line_count} error lines.')
                            line_count = 0
                        except Exception as e:
                            if debug:
                                print(f'WARNING: {e}')
                            line_count += 1

                if state == RECORDING_DATA:
                    if line.startswith('#'):
                        # receiving a settings line
                        raise Exception('got commented line while receiving data.')
                    sensor_number = analyze_data_line(line, sensor_number)
                    out_file.write(line)
                    out_file.write('\n')
                    line_count += 1
                    if line_count >= measurements_to_record:
                        state = RECORDING_ENDED
                        print(f'Done recording {measurements_to_record} lines.')
                        out_file.write(f'#e {datetime.now().isoformat()}\n')
                if state == RECORDING_ENDED:
                    print('############################################')
                    print('# Data Acquisition Done                    #')
                    print('############################################')
                    break
        except Exception as e:
            print(f'ERROR: An error occured after recording {line_count} / {measurements_to_record} lines.')
            print(f'ERROR: {e}')
            print('############################################')
            print('# Restarting Measurement - old data keept  #')
            print('############################################')
            error = True
        # out_file.close()
        if not error:
            print('Waiting ...')
            last_line_timestamp = datetime.now()
            while datetime.now() - last_line_timestamp <= timedelta(milliseconds=100):
                if ser.in_waiting == 0:
                    sleep(0.0005)
                    continue
                else:
                    line = ser.readline()
                    last_line_timestamp = datetime.now()
            print('############################################')
            print('# Starting new Measurement                 #')
            print('############################################')
        ser.close()
        sleep(1)

def open_serial():
    ser = serial.Serial(port, baudrate)
    # ser.baudrate = baudrate
    # ser.port = port
    ser.timeout = timeout
    ser.rtscts = True
    ser.close()
    ser.open()
    return ser


def analyze_data_line(line: str, num_sens_prev: int) -> (int):
    values = line.split('\t')
    if len(values) < 3:
        raise Exception(f'Dataline malformation: Less then three values. {line}')
    if len(values)%2 != 1:
        raise Exception(f'Dataline malformation: Even number of values. {line}')
    num_sens = int((len(values)-1)/2)
    if num_sens != num_sens_prev and num_sens_prev != 0:
        raise Exception(f'Sensor number changed. {line}')
    for value in values:
        if str(int(value)) != value:
            raise Exception(f'Transmitted value {value} not an integer. {line}')
    for i in range(num_sens):
        if int(values[1+num_sens+i]) != 0:
            raise Exception(f'Arduino transmitted Error {values[1+num_sens+i]}. {line}')
    return num_sens


if __name__ == '__main__':
    main()
