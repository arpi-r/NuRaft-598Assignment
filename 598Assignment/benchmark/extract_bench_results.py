avg_lat = []
thru = []

with open('598_bench_out', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'avg latency' in line:
            avg_lat.append(line.split()[2])
        if 'final throughput' in line:
            thru.append(line.split()[2][:-1])

for th in thru:
    print(th)

print()

for lat in avg_lat:
    print(lat)