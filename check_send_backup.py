#!/usr/bin/python3
import os
import pysftp
import datetime
import derek_functions as df

LOCAL_BACKUP_FOLDER = '/var/lib/vz/dump'
#LOCAL_BACKUP_FOLDER = 'Z:\\Proxmox_backups\\dump'
REMOTE_BACKUP_FOLDER = '/Storage/derek/Proxmox_backups/dump/'


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
ip = '192.168.2.22'
username = df.file_server_username
password = df.file_server_password
port = 22
MAX_BACKUPS = 7



# Returns the number of backups with container id 
def getNumBackups(conatinerID):
    connection = pysftp.Connection(host=ip,username=username,password=password,port=port,cnopts=cnopts)
    backups = connection.listdir(REMOTE_BACKUP_FOLDER)
    conatinerCount = 0
    for item in backups:
        parsed = item.split('-')
        if parsed[-1][-3:] == 'log':
            continue
        #print(parsed)
        if parsed[2] == str(conatinerID):
            conatinerCount += 1
    return conatinerCount

def getOldestBackUp(containerID):
    connection = pysftp.Connection(host=ip,username=username,password=password,port=port,cnopts=cnopts)
    backups = connection.listdir(REMOTE_BACKUP_FOLDER)
    releventBackups = []
    for item in backups:
        parsed = item.split('-')
        if parsed[-1][-3:] == 'log':
            continue
        if parsed[2] == str(containerID):
            releventBackups.append(item)
    
    dates = []
    for item in releventBackups:
        parsed = item.split('-')
        dateString = parsed[3]
        dateObject = datetime.datetime.strptime(dateString,"%Y_%m_%d")
        d = {}
        d['Name'] = item
        d['DateObejct'] = dateObject
        dates.append(d)
        
    dates = sorted(dates, key = lambda i:i['DateObejct'])
    return dates[0]['Name']
        
def removeOldestBackup(containerID):
    backupToRemove = getOldestBackUp(containerID)
    backupPath = os.path.join(REMOTE_BACKUP_FOLDER,backupToRemove)
    os.system(f"ssh root@{ip} rm {backupPath} ")

def main():
    backups = os.listdir(LOCAL_BACKUP_FOLDER)
    for each in backups:
        if '.dat' in each:
            continue
        parsed = each.split('-')
        containerId, containerDate = parsed[2], parsed[3]
        fullPath = os.path.join(LOCAL_BACKUP_FOLDER,each)
        if os.path.isfile(fullPath) is False:
            continue
        print(f'Sending {each}')
        if getNumBackups(containerId) >= MAX_BACKUPS:
            print("Going to remove an old backup")
            removeOldestBackup(containerId)
        remoteFolder = os.path.join(REMOTE_BACKUP_FOLDER,each)
        connection = pysftp.Connection(host=ip,username=username,password=password,port=port,cnopts=cnopts)
        x = connection.put(fullPath,remoteFolder)
        connection.close()
        print(x)
        os.system(f'rm {fullPath}')


def test():
    connection = pysftp.Connection(host=ip,username=username,password=password,port=port,cnopts=cnopts)
    x = connection.listdir(REMOTE_BACKUP_FOLDER)
    connection.close()
    print(x)

if __name__ == '__main__':
    main()