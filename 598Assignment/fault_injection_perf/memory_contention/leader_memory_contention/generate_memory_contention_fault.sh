#!/bin/sh

echo "start"

sudo sh -c "sudo mkdir /sys/fs/cgroup/memory/db"
sudo sh -c "sudo echo $(($1 * 1024 * 1024)) > /sys/fs/cgroup/memory/db/memory.limit_in_bytes"

echo "end"