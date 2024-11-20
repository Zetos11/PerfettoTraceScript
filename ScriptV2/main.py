import os
import sys

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

    print("gpu0 + gpu1= ", gpu0_freq, gpu1_freq, gpu_mem_avg)


    ad_power_rails_metrics = tp.metric(['android_powrails'])
    print(ad_power_rails_metrics)
    open('./out/tmp', 'w').close()
    with open('./out/tmp', 'w') as f:
        print(ad_power_rails_metrics, file=f)
    with open('./out/tmp', 'r') as f:
        lines = f.readlines()


    #return power_rails, cpu_little_freq, cpu_medium_freq, cpu_big_freq, gpu0_freq, gpu1_freq, gpu_mem_avg

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
