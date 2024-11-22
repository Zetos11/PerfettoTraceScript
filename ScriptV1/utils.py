def cpu_power_estimation(cpu_data, parsing_data):
    core_runtime = parsing_data[0]
    core_avg_freq = parsing_data[1]

    a = {}
    k = 0
    while k < 8:
        key = k
        cpu_data[k]['speed'].append(core_avg_freq[k])
        cpu_data[k]['speed'].sort()
        idx = cpu_data[k]['speed'].index(core_avg_freq[k])
        try:
            power = (cpu_data[k]['power'][idx] + cpu_data[k]['power'][idx + 1]) / 2
        except:
            power = cpu_data[k]['power'][-1]
        value = core_runtime[k] * power  # ns * mA
        a[key] = value
        cpu_data[k]['speed'].pop(idx)
        k += 1

    cons = 0

    for k in range(8):
        cons += a[k] / 1000000000 / 3600   # To get mAh

    return cons  # 4.4V average voltage for the battery

