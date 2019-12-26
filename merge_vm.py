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

        # Spew out all undeleted snapshots in the cluster.
        status,resp = mycluster.get_snapshots()
        all_snapshots_list = resp["entities"]
        # We could also include the VM, and the creation time of the snapshot.
        if (sys.argv[1] == "--snapshots"):
            print ("Here are the available snapshots that may be merged:")
            for snapshot in all_snapshots_list:
                if (snapshot["deleted"] == False):
                    print (snapshot["snapshot_name"])
            sys.exit(0)

        # We're here to restore a VM to a prior snapshot.
        snapshot_name = sys.argv[1]
        vm_name = sys.argv[2]
        found = False
        # Get the UUID of the VM.
        # Get information about all VMs in the cluster.
        status,all_vms = mycluster.get_all_vm_info()
        all_vms_list = all_vms["entities"]
        # pprint(all_vms_list)
        for vm_dict in all_vms_list:
            # If you were looking for a VM with a particular UUID, you would be matching for it here.
            if (vm_name == vm_dict["name"]):
                vm_uuid = vm_dict["uuid"]
                break
        try:
            print ("UUID of your VM is:",vm_uuid)
        except NameError:
            print (">>> Cannot proceed because we cannot find",vm_name)
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
 
        print ("Successfully merged: ",vm_name, " with ", snapshot_name)
        taskid = resp["task_uuid"]
        mycluster.poll_task(taskid)
        mycluster.power_on_vm(vm_uuid)

    except Exception as ex:
        print(ex)
        sys.exit(1)
