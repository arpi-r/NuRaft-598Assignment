import subprocess
import psutil
import time

print("starting follower 1 ...")
command1 = ["taskset", "-ac", "0", "./raft_bench", "2", "10.10.10.2:12345", "3600"]
process1 = subprocess.Popen(command1, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

time.sleep(30)

print("starting follower 2 ...")
command2 = ["taskset", "-ac", "1", "./raft_bench", "3", "10.10.10.3:12346", "3600"]
process2 = subprocess.Popen(command2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

time.sleep(30)

print()
print("Running benchmark")

avg_lat = []
thru = []

for i in range(2, 22, 2):
    print("Starting leader with ", str(i), "client threads ...")
    command = ["taskset", "-ac", "2-3", "./raft_bench", "1", "10.10.10.1:12347",  "20", "55000", str(i), "2048", "10.10.10.2:12345", "10.10.10.3:12346"]
    process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = process.communicate()

    if err:
        print("ERR: ")
        print(err.decode())
        exit(1)
    
    out_str = out.decode()
    out_lines = out_str.split('\n')

    for line in out_lines:
        if 'avg latency' in line:
            avg_lat.append(line.split()[2])
        if 'final throughput' in line:
            thru.append(line.split()[2][:-1])
    
    print("Run with thread count", i, "done!")

    if not i == 20:
        print("restarting follower 2 ...")
        command2 = ["taskset", "-ac", "1", "./raft_bench", "3", "10.10.10.3:12346", "3600"]
        process2 = subprocess.Popen(command2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        time.sleep(30)
    
print("Experiments done!")
print()

print("Killing all benchmark process...")

for proc in psutil.process_iter():
    try:
        processName = proc.name()
        if processName == "raft_bench":
            processID = proc.pid
            print(processName , ' ::: ', processID, "killed")
            command_kill = ["kill", "-9", str(processID)]
            process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print()
print()

print("Throughput (Kops/s)")
for th in thru:
    print(th)

print()

print("Average Latency (us)")
for lat in avg_lat:
    print(lat)
print()