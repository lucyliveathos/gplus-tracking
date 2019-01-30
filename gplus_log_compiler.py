'''
gplus_log_compiler does the following:
1. Looks in "Core-Hub Shipment Logs" on Box Sync from G+ cores.
    a) Does so by searching in the dates folders (ex 2019-1-4-17-47) and looking
    for folders named "minihub-<hub's MAC address>
2. Checks if these core underwent Hub-Hardening by searching through the Hub-Hardening
folder found in Core-Hub Shipment Logs.
4. Checks if the cores were updated to the latest BLE firmware (as of 2019-01-16 it's 
v1.0.5)
3. Combines all of these cores into a single gplus_updated.csv file, with cores that
didn't undergo hub hardening into gplus_no_dump.csv and cores that weren't updated in
gplus_no_bleupdate.csv.
4. gplus_updated can then be inputted into the following Google Sheet 
https://docs.google.com/spreadsheets/d/1-rhGOnfU0wzsMTdaXG5j4hARozovJVEfkStKSAaZ-Js/edit#gid=934065228
If you don't have access to "G+ Core Status" Google Sheet, ask Guido access
'''

import os
import time
import csv

class Core:
    def __init__(self, sn, mac, datetime, ble, dsp, dspbl):
        self.sn = sn
        self.mac = mac
        self.datetime = datetime
        self.ble = ble
        self.dsp = dsp
        self.dspbl = dspbl
    
    def printf(self):
        date = time.localtime(self.datetime)
        print('sn: %s, mac: %s, datetime: %s/%s/%s, ble: %s, dsp: %s, dspbl: %s'
            %(self.sn, self.mac, str(date[2]), str(date[1]), str(date[0]), self.ble, self.dsp, self.dspbl))

#Given a path to a hub's update-log.txt and a list of cores, will parse through the log
#and add the cores found in the log to the list. If the core already exist in the list,
#will choose which log was more recent.
def add_cores(hub_log_path, core_list):
    epoch_time = os.path.getmtime(hub_log_path)
    with open(hub_log_path, 'r') as log:
        for line in log:
            added = 0
            core_info = line.split(', ')
            core_info.append(epoch_time)
            if len(core_info) < 6:
                print('\n \n ERROR: Not enough information. Check ' + hub_log_path + ' for more info.')
            for core in core_list:
                #If core already in list, keep most recent log in list
                if (core.mac == core_info[1]) and (core.datetime < core_info[5]):
                    core.datetime = core_info[5]
                    #BLE can have 2 values: Apparel_Debug or v1.0.5
                    if core_info[2].split(' ')[1] != 'Apparel_Debug':
                        core.ble = core_info[2].split(' v')[1]
                    else:
                        core.ble = core_info[2].split(' ')[1]
                    core.dsp = core_info[3].split(' v')[1]
                    core.dspbl = core_info[4].split(' v')[1]
                    added = 1
                    break
                elif core.mac != core_info[1]:
                    continue
                else:
                    added = 1
                    break
            if added == 0:
                #BLE can have 2 values: Apparel_Debug or v1.0.5
                if core_info[2].split(' ')[1] != 'Apparel_Debug':
                    core_ble = core_info[2].split(' v')[1]
                else:
                    core_ble = core_info[2].split(' ')[1]
                
                #If core was not found in list, add to list
                new_core = Core(core_info[0], core_info[1], epoch_time, \
                        core_ble, \
                        core_info[3].split(' v')[1], \
                        core_info[4].split(' v')[1])
                core_list.append(new_core)

def search_ship():
    core_list = []
    ship_path = os.path.expanduser('~/Box Sync/Core-Hub Shipment Logs/')
    ship_folder = [f for f in os.listdir(ship_path) if f.startswith('2019-')]
    hardening_path = ship_path + 'Hub-Hardening/'
    hardening_folder = [f for f in os.listdir(hardening_path) if f.startswith('2019-')]
    for folder in ship_folder:
        for f in os.listdir(ship_path + folder): 
            if f.startswith('minihub-'):
                hub_log = (ship_path + folder + '/' + f + '/' + 'update-log.txt')
                add_cores(hub_log, core_list)
                #datetime = time.localtime(os.path.getmtime(hub_log))
    for harden in hardening_folder:
        for h in os.listdir(hardening_path + harden):
            if h.startswith('minihub-'):
                harden_log = (hardening_path + harden + '/' + h + '/' + 'update-log.txt')
                add_cores(harden_log, core_list)

    # filepath = path.abspath(path.join(ship_path, '2019-1-4-17-47', "minihub-b827ebccfedb", "update-log.txt"))

    # log = open(filepath, 'r')
    # print log.read()
    #print(ship_folder)
    return core_list

if __name__ == '__main__':
    core_list = search_ship()
    output = os.path.expanduser('~/Documents/')
    with open(output + 'Gplus_Tracking' + '.csv', 'w+') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['sn', 'mac', '', '', '', '', 'dsp', 'dspbl', 'ble', 'date'])
        for core in core_list:
            date = time.localtime(core.datetime)
            writer.writerow([core.sn, core.mac, '', '', '', '' , core.dsp, core.dspbl, core.ble, \
                            str(date[2]) + '/' + str(date[1]) + '/' + str(date[0])])
            core.printf()