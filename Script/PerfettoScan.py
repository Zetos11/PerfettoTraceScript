import subprocess
import Const as c


def power_rails_verification():
    print("Checking power rails availability...\n")
    adb_add_config = subprocess.run(["adb", "push", "cfg/verification.cfg", "/data/misc/perfetto-configs/verification.cfg"], text=True, capture_output=True)
    add_cfg = adb_add_config.stdout
    if add_cfg.find('error') != -1:
        print(add_cfg)
        return -2
    print("Configuration file pushed successfully")
    adb_start_perfetto = subprocess.run(["adb", "shell", "perfetto", "-o", "-", "--txt", "--config", "/data/misc/perfetto-configs/verification.cfg"], capture_output=True)
    perfetto_out = adb_start_perfetto.stdout
    f = open('verification/out.proto', 'wb')
    f.write(perfetto_out)
    f.close()
    print("Perfetto output written to file verification/out.proto")
    traceconv = subprocess.run(["../traceconv", "text", "verification/out.proto", "verification/out.txt"], text=True, capture_output=True)
    traceconv_out = traceconv.stderr
    if traceconv_out.find('main') != -1:
        return -3
    print("Scan complete")
    f1 = open("verification/out.txt", 'r')
    f1_read = f1.read()
    if f1_read.find("rail_descriptor") == -1:
        return -4
    else:
        return 0


def perfetto_scan(cfg_path):
    print("Pushing configuration file to device...\n")
    adb_add_config = subprocess.run(["adb", "push", cfg_path, "/data/misc/perfetto-configs/config.cfg"], text=True, capture_output=True)
    add_cfg = adb_add_config.stdout
    if add_cfg.find('error') != -1:
        print(add_cfg)
        return -2
    print("Configuration file pushed successfully" + c.jump_line)
    print("Starting Perfetto tracing...\n")
    adb_start_perfetto = subprocess.run(["adb", "shell", "perfetto", "-o", "-", "--txt", "--config", "/data/misc/perfetto-configs/config.cfg"], capture_output=True)
    perfetto_out = adb_start_perfetto.stdout
    print("Writing Perfetto output to file out.proto...")
    f = open('out/out.proto', 'wb')
    f.write(perfetto_out)
    f.close()
    print("Perfetto output written to file out.proto" + c.jump_line)
    print("out.proto conversion for analysis...")
    traceconv = subprocess.run(["../traceconv", "text", "out/out.proto", "out/out.txt"], text=True, capture_output=True)
    traceconv_out = traceconv.stderr
    if traceconv_out.find('main') != -1:
        return -3
    print("Conversion complete" + c.jump_line)



