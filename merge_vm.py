#!/usr/local/bin/python3.8
#
# DISCLAIMER: This script is not supported by Nutanix. Please contact
# Sandeep Cariapa (first.last@nutanix.com) if you have any questions.
# Last updated: 12/26/2019
# This script uses Python 3.8.
# NOTE: 
# 1. You need a Python library called "requests" which is available from
# the url: http://docs.python-requests.org/en/latest/user/install/#install
# For reference look at:
# http://developer.nutanix.com

import sys
import requests
import clusterconfig as C
from pprint import pprint
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Print usage messages.
def PrintUsage():

    print ("<Usage>: <{}> --snapshots".format(sys.argv[0]))
    print ("Will list the available snapshots in the cluster.\n")
    print ("<{}> <Snapshot name> <VM Name>".format(sys.argv[0]))
    print ("Will restore <Snapshot name> to <VM Name>.")
    return

if __name__ == "__main__":
    try:
        if ((len(sys.argv) != 2) and (len(sys.argv) != 3)):
            PrintUsage()
            sys.exit(1)

        if (len(sys.argv) == 2) and (sys.argv[1] != "--snapshots"):
            PrintUsage()
            sys.exit(1)

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        mycluster = C.my_api(C.src_cluster_ip,C.src_cluster_admin,C.src_cluster_pwd)
        status, cluster = mycluster.get_cluster_information()
        if (status != 200):
            print("Cannot connect to ",cluster)
            print("Did you remember to update the config file?")
            sys.exit(1)

        # Get information about all VMs in the cluster.
        status,all_vms = mycluster.get_all_vm_info()
        all_vms_list = all_vms["entities"]
        vm_by_name = {}
        vm_by_uuid = {}
        for vm_dict in all_vms_list:
            t_vm_uuid = vm_dict["uuid"]
            t_vm_name = vm_dict["name"]
            vm_by_name[t_vm_name] = t_vm_uuid
            vm_by_uuid[t_vm_uuid] = t_vm_name
        #pprint(all_vms_list)

        # Spew out all undeleted snapshots in the cluster.
        status,resp = mycluster.get_snapshots()
        all_snapshots_list = resp["entities"]
        if (sys.argv[1] == "--snapshots"):
            #pprint(all_snapshots_list)
            print ("Here are the available snapshots that may be restored:")
            for snapshot in all_snapshots_list:
                if (snapshot["deleted"] == False):
                    parent_vm_uuid = snapshot["vm_uuid"]
                    parent_vm_name = vm_by_uuid[parent_vm_uuid]
                    ss_time_str = datetime.fromtimestamp(snapshot["created_time"]/1000000).strftime('%Y-%m-%d %H:%M:%S')
                    print (">>> Snapshot Name:",snapshot["snapshot_name"],"VM Name:",parent_vm_name,"TimeStamp:",ss_time_str)
            sys.exit(0)

        # We're here to restore a VM to a prior snapshot.
        snapshot_name = sys.argv[1]
        vm_name = sys.argv[2]

        # If the specified VM is not an allowed VM, exit right now.
        if vm_name not in C.allowed_vm_list:
            print (">>> Cannot proceed because you are not allowed to restore:",vm_name)
            sys.exit(1)

        found = False
        vm_uuid = vm_by_name[vm_name]

        try:
            print ("UUID of your VM is:",vm_uuid)
        except NameError:
            print (">>> Cannot proceed because we cannot find:",vm_name)
            sys.exit(1)

        # pprint(all_snapshots_list)
        for snapshot in all_snapshots_list:
            if ((snapshot["snapshot_name"] == snapshot_name) and (snapshot["deleted"] == False)):
                ss_uuid = snapshot["uuid"]
                found = True
                break

        if (found == False):
            print (">>> Could not find", snapshot_name, "in the cluster.")
            print (">>> Please run", sys.argv[0], "--snapshots to get a list of all snapshots.")
            sys.exit(1)

        if (snapshot["vm_uuid"] != vm_uuid):
            print (">>> Snapshot does not match the VM.")
            print (">>> Please check your args.")
            sys.exit(1)

        status,resp = mycluster.merge_vm(vm_uuid,ss_uuid)
        print("Status: ",status)
 
        print ("Successfully restored:",vm_name, "to", snapshot_name)
        taskid = resp["task_uuid"]
        mycluster.poll_task(taskid)
        mycluster.power_on_vm(vm_uuid,vm_name)

    except Exception as ex:
        print(ex)
        sys.exit(1)
