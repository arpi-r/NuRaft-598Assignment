import subprocess
import psutil
import time

print("Fault injection: follower crash")
print("Running performance experiments")

avg_lat = []
thru = []
threads = []

for i in range(2, 22, 2):
    print("starting follower 1 ...")
    command1 = ["taskset", "-ac", "0", "./raft_bench", "2", "localhost:12345", "3600"]
    # command1 = ["./raft_bench", "2", "localhost:12345", "3600"]
    process1 = subprocess.Popen(command1, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process1_pid = process1.pid
    time.sleep(10)

    print("starting follower 2 ...")
    command2 = ["taskset", "-ac", "1", "./raft_bench", "3", "localhost:12346", "3600"]
    # command2 = ["./raft_bench", "3", "localhost:12346", "3600"]
    process2 = subprocess.Popen(command2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process2_pid = process2.pid
    time.sleep(10)
    
    print("Starting leader with ", str(i), "client threads ...")
    command = ["taskset", "-ac", "2", "./raft_bench", "1", "localhost:12347",  "20", "40000", str(i), "2048", "localhost:12345", "localhost:12346"]
    # command = ["./raft_bench", "1", "localhost:12347",  "20", "40000", str(i), "2048", "localhost:12345", "localhost:12346"]
    process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process_pid = process.pid
    out, err = process.communicate()

    print(out)

    if err:
        print("ERR: ")
        print(err.decode())
        exit(1)
    
    out_str = out.decode()
    out_lines = out_str.split('\n')

    for line in out_lines:
        if 'avg latency' in line:
            threads.append(i)
            avg_lat.append(line.split()[2])
        if 'final throughput' in line:
            if 'K' in line:
                thru.append(line.split()[2][:-1])
            else:
                thru.append(line.split()[2])
                
    print("killing followers...")
    print("Follower 1" , ' ::: ', process1_pid, "killed")
    command_kill = ["kill", "-9", str(process1_pid)]
    process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print("Follower 2" , ' ::: ', process2_pid, "killed")
    command_kill = ["kill", "-9", str(process2_pid)]
    process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    time.sleep(15)
    
    print("Run with thread count", i, "done!")
    print()
    
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

print(threads)
print()

print("Throughput (Kops/s)")
for th in thru:
    print(th)

print()

print("Average Latency (us)")
for lat in avg_lat:
    print(lat)

print()