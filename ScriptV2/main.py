import os
import sys

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
        "CPU0" : [],
        "CPU1" : [],
        "CPU2" : [],
        "CPU3" : [],
        "CPU4" : [],
        "CPU5" : [],
        "CPU6" : [],
        "CPU7" : [],
    }
    core_runtime_total = [0, 0, 0, 0, 0, 0, 0, 0]
    core_avg_freq_total = [0, 0, 0, 0, 0, 0, 0, 0]
    gpu0_freq = 0
    gpu1_freq = 0
    gpu_mem_avg = 0

    tp = TraceProcessor(trace=filename)

    ad_cpu_metrics = tp.metric(['android_cpu'])

    open('./out/tmp', 'w').close()
    with open('./out/tmp', 'w') as f:
        print(ad_cpu_metrics, file=f)
    with open('./out/tmp', 'r') as f:
        lines = f.readlines()

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


    ad_power_rails_metrics = tp.metric(['android_powrails'])
    rails_data = []
    test = MessageToDict(ad_power_rails_metrics)
    for elt in test['androidPowrails']['powerRails']:
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


    #return rails_data, cpu_little_freq, cpu_medium_freq, cpu_big_freq, gpu0_freq, gpu1_freq, gpu_mem_avg

def main(args):
    filenames = load_input_filename()

    try :
        value = int(args[0])
    except ValueError:
        print("Usage: python3 main.py slice (format : [0-100]")
        sys.exit(0)

    if len(filenames) == 0:
        print("No trace file found")
        sys.exit(0)

    for elt in filenames:
        data = parse_file(elt)

if __name__ == '__main__':
    main(sys.argv[1:])
