#!/bin/sh

echo "start"

sudo sh -c "sudo echo ${1} > /sys/fs/cgroup/memory/db/cgroup.procs"

echo "end"