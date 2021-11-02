#!/bin/bash

# This script will run on the sever and will prepare for the laptop to take over duties before shutting down

# Array with containers to move
# EXCLUDES the fileserver to restart pi network share as quickly as possible
containers=(105 114 119)
vms=()

blkLaptopContainers=(101 103 108 115 120)
blkLaptopvms=(112 113 118)

timestamp=$(date +%s)

# Rollback the laptop to previous snapshot
mostRecentSnapShot=$(zfs list -t snapshot -o name -s creation -r Storage/derek/Essential | tail -1)

ssh 192.168.2.70 zfs rollback rpool/$mostRecentSnapShot

zfs snapshot Storage/derek/Essential@$timestamp

zfs send -i $mostRecentSnapShot Storage/derek/Essential@$timestamp | ssh 192.168.2.70 zfs recv rpool/Storage/derek/Essential


pct migrate 102 laptop --restart


# All the rest of the containers 
for container in ${containers[@]}; do
    pct migrate $container laptop --restart
done

for vm in ${vms[@]}; do
    qm migrate $vm laptop --online --with-local-disks
done

for container in ${blkLaptopContainers[@]}; do
    pct migrate $container blkLaptop --restart
done

for vm in ${blkLaptopvms[@]}; do
    qm migrate $vm blkLaptop --online --with-local-disks
done

# Remount network share on pi so that programs continue to run correctly
ssh pi@192.168.2.105 'sudo mount -a'

sleep 10

#shutdown now
