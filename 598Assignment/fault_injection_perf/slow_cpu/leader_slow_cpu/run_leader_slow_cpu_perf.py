import subprocess
import psutil
import time
from threading import Thread

print("Fault injection: leader slow cpu")

avg_lat = []
thru = []
threads = []

def reader(f, outbuffer):
	while True:
		line = f.readline()
		# print(line)
		if line:
			outbuffer.append(line)
		else:
			break

quota = 50000
period = 1000000

command_inject_slow = ["bash", "generate_slow_fault.sh", str(quota), str(period)]
process_inject_slow = subprocess.Popen(command_inject_slow, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
out, err = process_inject_slow.communicate()
if err:
    print("ERR: ", err)

print("Running performance experiments")

for i in range(2, 22, 2):
    outlines = b''
    outbuffer = []

    print("starting follower 1 ...")
    command1 = ["taskset", "-ac", "0", "./raft_bench", "2", "localhost:12345", "3600"]
    process1 = subprocess.Popen(command1, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process1_pid = process1.pid
    time.sleep(10)

    print("starting follower 2 ...")
    command2 = ["taskset", "-ac", "1", "./raft_bench", "3", "localhost:12346",  "20", "40000", str(i), "2048"]
    process2 = subprocess.Popen(command2, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process2_pid = process2.pid
    t = Thread(target=reader, args=(process2.stdout, outbuffer))
    t.daemon = True
    t.start()
    time.sleep(10)
    
    print("Starting leader with ", str(i), "client threads ...")
    command = ["taskset", "-ac", "2", "./raft_bench", "1", "localhost:12347",  "20", "40000", str(i), "2048", "localhost:12345", "localhost:12346"]
    process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    process_pid = process.pid
    time.sleep(5)

    print("slowing down leader ... ")
    command_slow_leader = ["bash", "slow_leader_cpu.sh", str(process_pid)]
    process_slow_leader = subprocess.Popen(command_slow_leader, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = process_slow_leader.communicate()
    if err:
        print("ERR: ", err)
    
    t.join()

    while psutil.pid_exists(process2_pid):
        if outbuffer:
            line = outbuffer.pop(0)
            # print(line)
            outlines += line
            if b"tests passed out of" in line:
                break
        else:
            time.sleep(1)

    print(outlines)

    out_str = outlines.decode()
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
    out_lines = []

    print("killing all nodes...")
    print("Follower 1" , ' ::: ', process1_pid, "killed")
    command_kill = ["kill", "-9", str(process1_pid)]
    process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print("Follower 2" , ' ::: ', process2_pid, "killed")
    command_kill = ["kill", "-9", str(process2_pid)]
    process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print("Leader" , ' ::: ', process_pid, "killed")
    command_kill = ["kill", "-9", str(process_pid)]
    process_kill = subprocess.Popen(command_kill, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    time.sleep(15)
    
    print("Run with thread count", i, "done!")
    print()
    
print("Experiments done!")
print()

print("Killing all raft_bench processes ...")

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