import ast
import csv
import os
import subprocess
import sys
import re
from perfetto.trace_processor import TraceProcessor


def load_input_filename():
    filenames = []
    for root, _, files in os.walk('./in'):
        for filename in files:
            if filename.endswith('.perfetto-trace'):
                file_path = os.path.join(root, filename)
                filenames.append(file_path)
                print(file_path)
    return filenames

def trace_conversion(filename):
    open('filename', 'w').close()
    traceconv = subprocess.run(["./traceconv", "text", filename, "out/out.txt"],
                               text=True, capture_output=True)
    traceconv_out = traceconv.stderr
    if traceconv_out.find('main') != -1:
        print("conversion error")
        sys.exit(0)
    print("conversion success")


def process_result(trace_name, power_rails, other_data, value):
    line_elements = trace_name + ";"
    for elt in power_rails:
        size = len(elt["delta_list"])
        percent = int(size / (100 / value))
        print(percent)
        if percent > 0:
            line_elements = line_elements + str(sum(elt["delta_list"][0:percent])) + ";"
        else:
            line_elements = line_elements + str(sum(elt["delta_list"][size-percent:])) + ";"

    for elt in other_data:
        line_elements = line_elements + elt + ";"


def result_to_csv(data):
    with open('./out/out.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(data)

def parsing_freq(trace):
    freq_tab = {
        "CPU0" : [],
        "CPU1" : [],
        "CPU2" : [],
        "CPU3" : [],
        "CPU4" : [],
        "CPU5" : [],
        "CPU6" : [],
        "CPU7" : [],
        "GPU0" : [],
        "GPU1" : [],
    }
    core_runtime_total = [0, 0, 0, 0, 0, 0, 0, 0]
    core_avg_freq_total = [0, 0, 0, 0, 0, 0, 0, 0]
    tp = TraceProcessor(trace=trace)
    ad_cpu_metrics = tp.metric(['android_cpu'])
    ad_gpu_metrics = tp.metric(['android_gpu'])
    ad_powrails_metrics = tp.metric(['android_powrails'])

    print(ad_powrails_metrics)
    with open("./out/cpu_metric.txt", 'w') as f:
        print(ad_cpu_metrics, file=f)
    with open("./out/cpu_metric.txt", 'r') as f:
        lines = f.readlines()

    return 0

def parse_power_rails():
    rails_data = []
    gpu = 0
    gpu0 = []
    gpu1 = []
    with open("out/out.txt", 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if "rail_descriptor" in lines[i]:
                index = int(find_string_pattern("index", lines[i + 1]))
                rail_name = re.sub('[\W_]+', '', find_string_pattern("subsys_name", lines[i + 3]))
                if rail_name == "MultimediaSubsystem" or rail_name == "Multimedia" or rail_name == "multimedia":  # Fix the Camera Rail name to be more intuitive
                    rail_name = "Camera"
                if rail_name == "GPU":
                    if gpu == 1:
                        rail_name = "GPU3D"
                    else:
                        gpu = 1
                rails_data.append(create_rail_entry(rail_name, index))
                print(rail_name)
            if "energy_data" in lines[i]:
                index = int(find_string_pattern("index", lines[i + 1]))
                energy = int(find_string_pattern("energy", lines[i + 3]))
                rails_data[index]["energy_list"].append(energy)
            if "gpu_frequency" in lines[i]:
                index = int(find_string_pattern("gpu_id", lines[i + 1]))
                frequency = int(find_string_pattern("state", lines[i + 2]))
                if index == 0:
                    gpu0.append(frequency)
                else:
                    gpu1.append(frequency)


        rails_data_valid = []
        for i in rails_data:
            if i["energy_list"]:
                rails_data_valid.append(i)

        for i in rails_data_valid:
            res = energy_delta(i["energy_list"])
            i["total_energy"] = res[0]
            i["delta_list"] = res[1]
            i["delta_list"].pop(0)

    return rails_data_valid

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


def find_string_pattern(pattern, line):
    idx = line.index(pattern)
    return (line[idx + len(pattern) + 2:len(line)]).translate(str.maketrans({'"': None}))


def create_rail_entry(name, index):
    return {
        "rail": name,
        "index": index,
        "total_energy": 0,
        "energy_list": [],
        "delta_list": []
    }

def print_usage():
    print("Usage: python3 main.py optionnal:integer")


def main(argv):
    filenames = load_input_filename()

    try :
        value = int(argv[0])
    except ValueError:
        print_usage()
        sys.exit(0)

    if len(filenames) == 0:
        print("No trace file found")
        sys.exit(0)

    for elt in filenames:
        #trace_conversion(elt)
        res = parse_power_rails()
        other_data = parsing_freq(elt)
        data = process_result(elt, res, other_data, value=100)
        result_to_csv(data)





if __name__ == '__main__':
    main(sys.argv[1:])
