# Noé Chachignot, INRIA, 2024
import csv
import os
import sys
import re

from perfetto.trace_processor import TraceProcessor
from google.protobuf.json_format import MessageToDict

"""
load_input_filename : Load all the trace files in the in directory

Returns:
    filenames : List of all the trace files
"""
def load_input_filename():
    filenames = []
    for root, _, files in os.walk('./in'):
        for filename in files:
            if filename.endswith('.perfetto-trace'):
                file_path = os.path.join(root, filename)
                filenames.append(file_path)
    return filenames

"""
create_rail_entry : Create a dictionary for a power rail

Parameters:
    name : Name of the power rail
    energy_list : List of energy values
    
Returns:
    Dictionary for the power rail
"""
def create_rail_entry(name, energy_list):
    return {
        "rail": name,
        "total_energy": 0,
        "energy_list": energy_list,
        "delta_list": []
    }

"""
cpu_freq_compilation : Calculate the average frequency for each CPU group

Parameters:
    freq_tab : Dictionary containing the frequency data for each CPU group
    
Returns:
    little : Average frequency for the little CPU group
    medium : Average frequency for the medium CPU group (big in the trace)
    big : Average frequency for the big CPU group (bigger in the trace)
"""
def cpu_freq_compilation(freq_tab):
    little = 0
    medium = 0
    big = 0
    for key in freq_tab:
        num = 0
        den = 0
        for elt in freq_tab[key]:
            num += int(elt[0])*int(elt[1])
            den += int(elt[1])
        if key == "Little":
            little = num / den
        if key == "Medium":
            medium = num / den
        if key == "Big":
            big = num / den
    return little, medium, big

"""
energy_delta : Calculate the energy delta for a power rail

Parameters:
    list_energy : List of energy values
    
Returns:
    end - start : Give total energy consumption
    list_delta : List of energy deltas
"""
def energy_delta(list_energy):
    list_delta = []
    timestamps = len(list_energy)
    start = list_energy[0]
    end = list_energy[timestamps - 1]
    j = start
    for i in list_energy:
        v = i - j
        list_delta.append(v)  # convert from uWs to mWs
        j = i
    return end - start, list_delta

"""
parse_file : Parse the trace file and extract the relevant data

Parameters:
    filename : Name of the trace file
    
Returns:
    rails_data : List of power rail data
    cpu_little_freq : Average frequency for the little CPU group
    cpu_medium_freq : Average frequency for the medium CPU group (big in the trace)
    cpu_big_freq : Average frequency for the big CPU group (bigger in the trace)
    gpu0_freq : Frequency of the first GPU
    gpu1_freq : Frequency of the second GPU
    gpu_mem_avg : Average GPU memory frequency
    battery_discharge : Battery discharge
"""
def parse_file(filename):
    freq_tab = {
        "Little" : [],
        "Medium" : [],
        "Big" : []
    }

    gpu0_freq = 0
    gpu1_freq = 0
    gpu_mem_avg = 0

    tp = TraceProcessor(trace=filename)

    # Parse GPU metrics
    ad_gpu_metrics = tp.metric(['android_gpu'])
    gpu_idx = 0
    open('./out/tmp', 'w').close()
    with open('./out/tmp', 'w') as f:
        print(ad_gpu_metrics, file=f)
    with open('./out/tmp', 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if "freq_metrics" in lines[i]:
                if "freq_avg" in lines[i+4]:
                    if gpu_idx == 0:
                        gpu0_freq = int(float(lines[i+4].split(":")[1][1:-2]))
                        gpu_mem_avg = int(lines[i-1].split(":")[1][1:-1])
                    else:
                        gpu1_freq = int(float(lines[i+4].split(":")[1][1:-2]))
                    gpu_idx += 1

    # Parse power rails
    ad_power_rails_metrics = tp.metric(['android_powrails'])
    rails_data = []
    gpu_dict = MessageToDict(ad_power_rails_metrics)
    for elt in gpu_dict['androidPowrails']['powerRails']:
        list_energy = []
        name = elt.get('name')
        for i in elt['energyData']:
            list_energy.append(i.get('energyUws'))
        rails_data.append(create_rail_entry(name, list_energy))
    for i in rails_data:
        res = energy_delta(i["energy_list"])
        i["total_energy"] = res[0]
        i["delta_list"] = res[1]
        i["delta_list"].pop(0)


    # Parse CPU metrics
    ad_cpu_metrics = tp.metric(['android_cpu'])
    cpu_dict = MessageToDict(ad_cpu_metrics)
    for elt in cpu_dict['androidCpu']['processInfo']:
        for ct in elt['coreType']:
            if ct['type'] == 'little':
                freq_tab["Little"].append([ct['metrics']['avgFreqKhz'], ct['metrics']['runtimeNs']])
            if ct['type'] == 'big':
                freq_tab["Medium"].append([ct['metrics']['avgFreqKhz'], ct['metrics']['runtimeNs']])
            if ct['type'] == 'bigger':
                freq_tab["Big"].append([ct['metrics']['avgFreqKhz'], ct['metrics']['runtimeNs']])

    # Calculate average cpu frequency
    res =  cpu_freq_compilation(freq_tab)
    cpu_little_freq = res[0]
    cpu_medium_freq = res[1]
    cpu_big_freq = res[2]

    # Parse Battery metrics
    ad_battery_metrics = tp.metric(['android_batt'])
    battery_dict = MessageToDict(ad_battery_metrics)
    battery_start = battery_dict['androidBatt']['batteryCounters'][0]['chargeCounterUah']
    battery_end = battery_dict['androidBatt']['batteryCounters'][-1]['chargeCounterUah']
    battery_discharge = battery_end - battery_start

    # Parse mem metrics
    ad_netperf_metrics = tp.metric(['android_netperf'])


    return rails_data, int(cpu_little_freq), int(cpu_medium_freq), int(cpu_big_freq), gpu0_freq, gpu1_freq, gpu_mem_avg, battery_discharge #Rounded for comprehension

"""
result_to_csv : Write the data to a CSV file

Parameters:
    data : List of data to write to the CSV file
"""
def result_to_csv(data):
    with open('./out/out.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow((
                                'Trace;'
                             'L21S_VDD2L_MEM_ENERGY;'
                             'UFS(Disk)_ENERGY;'
                             'S12S_VDD_AUR_ENERGY;'
                             'Camera_ENERGY;'
                             'GPU3D_ENERGY;'
                             'Sensor_ENERGY;'
                             'Memory_ENERGY;'
                             'Memory_ENERGY;'
                             'Display_ENERGY;'
                             'GPS_ENERGY;'
                             'GPU_ENERGY;'
                             'WLANBT_ENERGY;'
                             'L22M_DISP_ENERGY;'
                             'S6M_LLDO1_ENERGY;'
                             'S8M_LLDO2_ENERGY;'
                             'S9M_VDD_CPUCL0_M_ENERGY;'
                             'CPU_BIG_ENERGY;'
                             'CPU_LITTLE_ENERGY;'
                             'CPU_MID_ENERGY;'
                             'INFRASTRUCTURE_ENERGY;'
                             'CELLULAR_ENERGY;'
                             'CELLULAR_ENERGY;'
                             'INFRASTRUCTURE_ENERGY;'
                             'TPU_ENERGY;'
                             'CPU_LITTLE_FREQ;'
                             'CPU_MID_FREQ;'
                             'CPU_BIG_FREQ;'
                             'GPU0_FREQ;'
                             'GPU_1FREQ;'
                             'GPU_MEM_AVG;'
                             'BATTERY_DISCHARGE'
                             ).split(';'))
        for elt in data:
            print(elt)
            spamwriter.writerow(elt)

"""
process_result : Prepare the result to be written to the CSV file

Parameters:
    trace_name : Name of the trace
    data : List of data to write to the CSV file
    power_rails_slice : Slice of the power rails to consider given in the main   
    
Returns:
    line_elements : List of elements to write to the CSV file
"""
def process_result(trace_name, data, power_rails_slice):
    line_elements = [trace_name]
    pattern = r"^\[(\d+):(\d+)\]$"
    match = re.match(pattern, power_rails_slice)
    x, y = map(int, match.groups())
    for elt in data[0]:
        if x == 0 and y == 100:
            line_elements.append(str(elt["total_energy"]))
        else:
            size = len(elt["delta_list"])
            start = int((x/100) * size)
            end = int((y/100) * size)
            line_elements.append(str(sum(elt["delta_list"][start:end])))

    for elt in data[1:]:
        line_elements.append(str(elt))
    return line_elements

"""
slice_validation : Validate the slice format

Parameters:
    value : Slice to validate
    
Returns:
    res : True if the slice is valid, False otherwise
"""
def slice_validation(value):
    res = False
    pattern = r"^\[(\d+):(\d+)\]$" # [0:100]
    match = re.match(pattern, value)
    if match:
        res =  True
    x, y = map(int, match.groups())
    if not (0 <= x < 100 and 0 < y <= 100 and x < y):
            res =  False
            print('slice format : [x:y] with 0 < x < 100 and 0 < y < 100 and x < y')
    return res


def main(args):
    if not slice_validation(args[0]):
        print("Usage: python3 main.py power_rails_slice (format : [0:100])")
        sys.exit(0)

    filenames = load_input_filename()

    if len(filenames) == 0:
        print("No trace file found")
        sys.exit(0)

    open('./out/out.csv', 'w').close()
    data = []

    for elt in filenames:
        formatted_data = process_result(re.split(r' |/|\\',elt)[2][:-15], parse_file(elt), args[0])
        data.append(formatted_data)

    result_to_csv(data)

if __name__ == '__main__':
    main(sys.argv[1:])
