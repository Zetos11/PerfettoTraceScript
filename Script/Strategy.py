import PerfettoScan
import Const as c
import ConversionParsing as cp
import Graph as g
import sys
import main
import ADB
import utils

def strategy_device():
    status = 0
    error_message = ""
    print("Starting device energy consumption analysis...\n")
    perfetto_scan = PerfettoScan.perfetto_scan("./cfg/config.cfg")
    if perfetto_scan == -2:
        status = 2
        error_message = "Error while pushing config file, check if the config file name is 'config.cfg'" + c.jump_line
    elif perfetto_scan == -3:
        status = 3
        error_message = "Error while converting out.proto to out.txt, check if the input and output files names are correct" + c.jump_line
    main.status_check(status, error_message)
    print("Analysis complete" + c.jump_line)

    print("Parsing power rails data...\n")
    parsingPR = cp.parse_power_rails()
    main.status_check(status, error_message)
    print("Parsing complete" + c.jump_line)

    for elt in parsingPR:
        print(elt["rail"] + " : " + str(elt["total_energy"]) + " uWs" + c.jump_line)

    res_CPU = 0

    for elt in parsingPR:
        if elt["rail"] == "CPUBIG":
            res_CPU += elt["total_energy"]
        if elt["rail"] == "CPUMID":
            res_CPU += elt["total_energy"]
        if elt["rail"] == "CPULITTLE":
            res_CPU += elt["total_energy"]

    res_mAh_CPU = res_CPU / 3600 / 1000 / 4.4

    res_screen = 0

    for elt in parsingPR:
        if elt["rail"] == "Display":
            res_screen += elt["total_energy"]

    res_mAh_screen = res_screen / 3600 / 1000 / 4.4

    res_GPS = 0

    for elt in parsingPR:
        if elt["rail"] == "GPS":
            res_GPS += elt["total_energy"]

    res_mAh_GPS = res_GPS / 3600 / 1000 / 4.4

    res_WIFI = 0

    for elt in parsingPR:
        if elt["rail"] == "WLANBT":
            res_WIFI += elt["total_energy"]

    res_mAh_WIFI = res_WIFI / 3600 / 1000 / 4.4


    print("Result CPU with mAh : " + str(res_mAh_CPU) + c.jump_line)

    print("Result screen with mAh : " + str(res_mAh_screen) + c.jump_line)

    print("Result GPS with mAh : " + str(res_mAh_GPS) + c.jump_line)

    print("Result WIFI with mAh : " + str(res_mAh_WIFI) + c.jump_line)

    print("Generating graph...\n")
    # csv.import_to_csv(parsing[0], "out/out.csv")
    g.display_graph(parsingPR)
    print("Graph generated successfully" + c.jump_line)
    print("Exiting...")
    sys.exit(0)


def strategy_app(app_name):
    status = 0
    error_message = ""

    no_uid = app_name.split(" ")

    print("Retrieving power_profile.xml...\n")
    dumpsys = ADB.adb_dumpsys_power_profile()
    power_profile_cpu = cp.parsing_power_profile(dumpsys)
    print("Power profile retrieved successfully" + c.jump_line)

    ADB.adb_start_app(app_name)

    perfetto_scan = PerfettoScan.perfetto_scan("cfg/config.cfg")
    if perfetto_scan == -2:
        status = 2
        error_message = "Error while pushing config file, check if the config file name is 'config.cfg'" + c.jump_line
    elif perfetto_scan == -3:
        status = 3
        error_message = "Error while converting out.proto to out.txt, check if the input and output files names are correct" + c.jump_line
    main.status_check(status, error_message)

    print("Parsing power rails data...\n")
    parsingPR = cp.parse_power_rails()
    main.status_check(status, error_message)
    print("Parsing complete" + c.jump_line)
    parsing = cp.parsing_perfetto_version(no_uid[0])
    main.status_check(status, error_message)

    res_mAh = utils.cpu_power_estimation(power_profile_cpu, parsing)

    ADB.adb_stop_app(app_name)

    for elt in parsingPR:
        print(elt["rail"] + " : " + str(elt["total_energy"]) + " uWs" + c.jump_line)

    res_screen = 0

    for elt in parsingPR:
        if elt["rail"] == "Display":
            res_screen += elt["total_energy"]

    res_mAh_screen = res_screen / 3600 / 1000 / 4.4

    res_GPS = 0

    for elt in parsingPR:
        if elt["rail"] == "GPS":
            res_GPS += elt["total_energy"]

    res_mAh_GPS = res_GPS / 3600 / 1000 / 4.4

    res_WIFI = 0

    for elt in parsingPR:
        if elt["rail"] == "WLANBT":
            res_WIFI += elt["total_energy"]

    res_mAh_WIFI = res_WIFI / 3600 / 1000 / 4.4


    print("Result with mAh : " + str(res_mAh) + c.jump_line)

    print("Result screen with mAh : " + str(res_mAh_screen) + c.jump_line)

    print("Result GPS with mAh : " + str(res_mAh_GPS) + c.jump_line)

    print("Result WIFI with mAh : " + str(res_mAh_WIFI) + c.jump_line)

    sys.exit(0)


def strategy_tpl(choice):
    status = 0
    error_message = ""

    print("Retrieving power_profile.xml...\n")
    dumpsys = ADB.adb_dumpsys_power_profile()
    power_profile_cpu = cp.parsing_power_profile(dumpsys)
    print("Power profile retrieved successfully" + c.jump_line)

    if choice == "ads":
        ads_strategy(power_profile_cpu)

    elif choice == "crashreporting":
        crashreporting_strategy(power_profile_cpu)

    elif choice == "monitoring":
        monitoring_strategy(power_profile_cpu)

    sys.exit(0)


def ads_strategy(power_profile_cpu):
    ads_max = "tpl.ads.banner.max"
    ads_chartboost = "tpl.ads.banner.chartboost"
    ads_admob = "tpl.ads.banner.admob"
    ads_template = "tpl.ads.banner.template"

    status = 0
    error_message = ""

    ADB.adb_start_app(ads_template)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(ads_template)
    template = cp.parsing_perfetto_version(ads_template)
    print("Parsing power rails data...\n")
    parsingPR1 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR1)

    ADB.adb_start_app(ads_chartboost)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(ads_chartboost)
    ads1 = cp.parsing_perfetto_version(ads_chartboost)
    print("Parsing power rails data...\n")
    parsingPR2 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR2)

    ADB.adb_start_app(ads_admob)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(ads_admob)
    ads2 = cp.parsing_perfetto_version(ads_admob)
    print("Parsing power rails data...\n")
    parsingPR3 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR3)

    ADB.adb_start_app(ads_max)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(ads_max)
    ads3 = cp.parsing_perfetto_version(ads_max)
    print("Parsing power rails data...\n")
    parsingPR4 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR4)


    res_template = utils.cpu_power_estimation(power_profile_cpu, template)
    res1 = utils.cpu_power_estimation(power_profile_cpu, ads1)
    res2 = utils.cpu_power_estimation(power_profile_cpu, ads2)
    res3 = utils.cpu_power_estimation(power_profile_cpu, ads3)

    list_res = [res_template, res1, res2, res3]
    list_res.sort()

    print("Result : ")
    print("Template : " + str(res_template))
    print("Chartboost : " + str(res1))
    print("Admob : " + str(res2))
    print("Max : " + str(res3))
    print("Ranking : " + str(list_res))
    sys.exit(0)


def print_energy_data(parsingPR):
    res_GPS = 0

    for elt in parsingPR:
        if elt["rail"] == "GPS":
            res_GPS += elt["total_energy"]

    res_mAh_GPS = res_GPS / 3600 / 1000 / 4.4

    res_WIFI = 0

    for elt in parsingPR:
        if elt["rail"] == "WLANBT":
            res_WIFI += elt["total_energy"]

    res_mAh_WIFI = res_WIFI / 3600 / 1000 / 4.4

    print("Result GPS with mAh : " + str(res_mAh_GPS) + c.jump_line)

    print("Result WIFI with mAh : " + str(res_mAh_WIFI) + c.jump_line)


def crashreporting_strategy(power_profile_cpu):
    cr_acra = "tpl.crashreporting.acra"
    cr_crashlytics = "tpl.crashreporting.crashlytics"
    cr_newrelic = "tpl.crashreporting.newrelic"
    cr_template = "tpl.crashreporting.template"

    ADB.adb_start_app(cr_template)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(cr_template)
    template = cp.parsing_perfetto_version(cr_template)
    print("Parsing power rails data...\n")
    parsingPR1 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR1)


    ADB.adb_start_app(cr_acra)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(cr_acra)
    cr1 = cp.parsing_perfetto_version(cr_acra)
    print("Parsing power rails data...\n")
    parsingPR2 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR2)

    ADB.adb_start_app(cr_crashlytics)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(cr_crashlytics)
    cr2 = cp.parsing_perfetto_version(cr_crashlytics)
    print("Parsing power rails data...\n")
    parsingPR3 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR3)

    ADB.adb_start_app(cr_newrelic)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(cr_newrelic)
    cr3 = cp.parsing_perfetto_version(cr_newrelic)
    print("Parsing power rails data...\n")
    parsingPR4 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR4)

    res_template = utils.cpu_power_estimation(power_profile_cpu, template)
    res1 = utils.cpu_power_estimation(power_profile_cpu, cr1)
    res2 = utils.cpu_power_estimation(power_profile_cpu, cr2)
    res3 = utils.cpu_power_estimation(power_profile_cpu, cr3)

    list_res = [res_template, res1, res2, res3]
    list_res.sort()

    print("Result : ")
    print("Template : " + str(res_template))
    print("Acra : " + str(res1))
    print("Crashlytics : " + str(res2))
    print("NewRelic : " + str(res3))
    print("Ranking : " + str(list_res))
    sys.exit(0)


def monitoring_strategy(power_profile_cpu):
    moni_newrelic = "tpl.monitoring.newrelic"
    moni_amplitude = "tpl.monitoring.amplitude"
    moni_firebase = "tpl.monitoring.firebase"
    moni_template = "tpl.monitoring.template"

    ADB.adb_start_app(moni_template)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(moni_template)
    template = cp.parsing_perfetto_version(moni_template)
    print("Parsing power rails data...\n")
    parsingPR1 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR1)


    ADB.adb_start_app(moni_firebase)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(moni_firebase)
    moni1 = cp.parsing_perfetto_version(moni_firebase)
    print("Parsing power rails data...\n")
    parsingPR2 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR2)

    ADB.adb_start_app(moni_amplitude)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(moni_amplitude)
    moni2 = cp.parsing_perfetto_version(moni_amplitude)
    print("Parsing power rails data...\n")
    parsingPR3 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR3)

    ADB.adb_start_app(moni_newrelic)
    PerfettoScan.perfetto_scan("cfg/tpl_cfg.cfg")
    ADB.adb_stop_app(moni_newrelic)
    moni3 = cp.parsing_perfetto_version(moni_newrelic)
    print("Parsing power rails data...\n")
    parsingPR4 = cp.parse_power_rails()
    print("Parsing complete" + c.jump_line)
    print_energy_data(parsingPR4)

    res_template = utils.cpu_power_estimation(power_profile_cpu, template)
    res1 = utils.cpu_power_estimation(power_profile_cpu, moni1)
    res2 = utils.cpu_power_estimation(power_profile_cpu, moni2)
    res3 = utils.cpu_power_estimation(power_profile_cpu, moni3)

    list_res = [res_template, res1, res2, res3]
    list_res.sort()

    print("Result : ")
    print("Template : " + str(res_template))
    print("Firebase : " + str(res1))
    print("Amplitude : " + str(res2))
    print("NewRelic : " + str(res3))
    print("Ranking : " + str(list_res))
    sys.exit(0)
