#!/bin/sh

echo "start"

sudo sh -c "sudo mkdir /sys/fs/cgroup/cpu/db"
sudo sh -c "sudo echo ${1} > /sys/fs/cgroup/cpu/db/cpu.cfs_quota_us"
sudo sh -c "sudo echo ${2} > /sys/fs/cgroup/cpu/db/cpu.cfs_period_us"

echo "end"