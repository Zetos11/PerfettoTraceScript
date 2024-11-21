import os
import sys
from typing import re

from perfetto.trace_processor import TraceProcessor
from google.protobuf.json_format import MessageToDict


def load_input_filename():
    filenames = []
    for root, _, files in os.walk('./in'):
        for filename in files:
            if filename.endswith('.perfetto-trace'):
                file_path = os.path.join(root, filename)
                filenames.append(file_path)
                print(file_path)
    return filenames

def create_rail_entry(name, energy_list):
    return {
        "rail": name,
        "total_energy": 0,
        "energy_list": energy_list,
        "delta_list": []
    }

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

def parse_file(filename):
    freq_tab = {
        "Little" : [],
        "Medium" : [],
        "Big" : []
    }

    cpu_little_freq = 0
    cpu_medium_freq = 0
    cpu_big_freq = 0
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

    return rails_data, int(cpu_little_freq), int(cpu_medium_freq), int(cpu_big_freq), gpu0_freq, gpu1_freq, gpu_mem_avg #Rounded for comprehsion

def result_to_csv(data):
    with open('./out/out.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(data)

def process_result(trace_name, data, power_rails_slice):
    line_elements = trace_name + ";"
    for elt in data[0]:
        size = len(elt["delta_list"])
        percent = int(size / (100 / value))
        print(percent)
        if percent > 0:
            line_elements = line_elements + str(sum(elt["delta_list"][0:percent])) + ";"
        else:
            line_elements = line_elements + str(sum(elt["delta_list"][size - percent:])) + ";"

    for elt in data:
        line_elements = line_elements + elt + ";"

def slice_validation(value):
    res = False
    pattern = r"^\[(\d+):(\d+)\]$" # [0:100]
    match = re.match(pattern, value)
    if match:
        res =  True
    x, y = map(int, match.groups())
    if not (0 < x < 100 and 0 < y < 100 and x < y):
            res =  False
            print('slice format : [x:y] with 0 < x < 100 and 0 < y < 100 and x < y')
    return res


def main(args):
    if not slice_validation(args[0]):
        print("Usage: python3 main.py slice (format : [0-100]")
        sys.exit(0)

    filenames = load_input_filename()

    if len(filenames) == 0:
        print("No trace file found")
        sys.exit(0)

    data = []

    for elt in filenames:
        formatted_data = process_result(elt.split('/'[2]), parse_file(elt), args[0])
        data.append(formatted_data)

    result_to_csv(data)

if __name__ == '__main__':
    main(sys.argv[1:])
