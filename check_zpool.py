import subprocess
import derek_functions as df
from collections import defaultdict

class ZpoolStatus:

    def __init__(self) -> None:
        self.name = open('/etc/hostname').read().replace('\n','')
        self.sent_notfication = defaultdict(lambda: False)

        
    def get_pool_status(self):
        status, result = subprocess.getstatusoutput('zpool list -o name,health')

        pools = result.split('\n')[1:]

        for pool in pools:
            if 'ONLINE' not in pool:
                pool_array = pool.split('  ')
                pool_name = pool_array[0]
                pool_status = pool_array[-1]
                message = f'{pool_name} status is {pool_status} on server {self.name}'
                if self.sent_notfication[pool_name] == False:
                    print(message)
                    df.sendText('+17153471797',message)
                    self.sent_notfication[pool_name] = True

            else:
                pool_array = pool.split('  ')
                pool_name = pool_array[0]
                pool_status = pool_array[-1] 
                self.sent_notfication[pool_name] = False

def main():
    x = ZpoolStatus()
    x.get_pool_status()

if __name__ == '__main__':
    main()