#!/bin/bash

# This script will run on the sever and will prepare for the laptop to take over duties before shutting down

# Array with containers to move
# EXCLUDES the fileserver to restart pi network share as quickly as possible
containers=(105 114)
vms=()

timestamp=$(date +%s)

# Rollback the laptop to previous snapshot
mostRecentSnapShot=$(zfs list -t snapshot -o name -s creation -r rpool/Storage/derek/Essential | tail -1)

mostRecentSnapShotServer=$(echo $mostRecentSnapShot | cut -c 7-)

ssh 192.168.2.22 zfs rollback $mostRecentSnapShotServer

zfs snapshot rpool/Storage/derek/Essential@$timestamp

zfs send -i $mostRecentSnapShot rpool/Storage/derek/Essential@$timestamp | ssh 192.168.2.22 zfs recv Storage/derek/Essential


pct migrate 102 server --restart
# Dont need to reboot can just remount network share
ssh pi@192.168.2.105 'sudo mount -a'

for container in ${containers[@]}; do
    pct migrate $container server --restart
done

for vm in ${vms[@]}; do
    qm migrate $vm server --online --with-local-disks
done

sleep 10