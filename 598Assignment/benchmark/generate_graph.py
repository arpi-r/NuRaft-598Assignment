import matplotlib.pyplot as plt

throughput = []
latency = []

with open("bench_out2.txt", "r") as f:
    out_lines = f.readlines()

start_throughput = False
start_latency = False
for line in out_lines:
    if "Throughput (Kops/s)" in line:
        start_throughput = True
        continue
    elif "Average Latency (us)" in line:
        start_latency = True
        continue
    elif line == "\n":
        start_throughput = False
        continue

    if start_throughput:
        throughput.append(float(line[:-1]))
    if start_latency:
        latency.append(int(line[:-1]))

print(throughput)
print(latency)

plt.clf()
plt.plot(throughput, latency, 'bo-')

num_thread = 2
for x,y in zip(throughput, latency):
    label = num_thread
    num_thread += 2
    plt.annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='right', va='center')

plt.title('Baseline Benchmark Performance', fontsize=20)
plt.xlabel('Throughput (Kops/s)', fontsize=12)
plt.ylabel('Average Latency (us)', fontsize=12)

plt.axis([6, 21, 250, 1200])
plt.grid()

plt.show()

plt.savefig("bench.png")
