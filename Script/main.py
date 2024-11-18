import ast
import subprocess
import sys
import re


def parse_power_rails():
    rails_data = []
    gpu = 0
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
            if "energy_data" in lines[i]:
                index = int(find_string_pattern("index", lines[i + 1]))
                energy = int(find_string_pattern("energy", lines[i + 3]))
                rails_data[index]["energy_list"].append(energy)

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


def parsing_power_profile(power_profile):
    speed_list = [[None], [None], [None]]
    power_list = [[None], [None], [None]]
    power_profile_list = power_profile.split("\n")
    for elt in power_profile_list:
        if "cpu.clusters.cores" in elt:
            core_list = ast.literal_eval(elt.split("=")[1])
        if "cpu.core_speeds" in elt:
            temp_speed = elt.split("=")
            idx = int(temp_speed[0][-1])
            speed_list[idx] = ast.literal_eval(temp_speed[1])
        if "cpu.core_power" in elt:
            temp_power = elt.split("=")
            idx = int(temp_power[0][-1])
            power_list[idx] = ast.literal_eval(temp_power[1])
    power_profile_data = create_cpu_core_entry(speed_list, power_list, core_list)
    return power_profile_data


def create_cpu_core_entry(speed, power, type):
    power_data = []
    for idx, elt in enumerate(type):
        for i in range(int(elt)):
            power_data.append({
                "type": idx,
                "speed": speed[idx],
                "power": power[idx]
            })
    return power_data

def print_usage():
    print("Usage: python3 main.py trace_path")


def main(params):
    if len(params) == 0:
        print_usage()
    """
    else :
        traceconv = subprocess.run(["./traceconv", "text", params[0], "out/out.txt"],
                                   text=True, capture_output=True)
        traceconv_out = traceconv.stderr
        if traceconv_out.find('main') != -1:
            print(print_usage())
            sys.exit(0)
    """
    res = parse_power_rails()
    print(res)





if __name__ == '__main__':
    main(sys.argv[1:])
