# self-service-vm-restore

Self service VM restore will be available in a future release of AOS. Until then you can use these scripts.
HOWTO.txt describes the process required to configure a Deployment VM. Run scripts from this Deployment VM.
Please be sure to update variables in clusterconfig.py also.

The use case here is to:

a. Take a snapshot (or more than one snapshot) of a VM from Prism Element.

b. Restore the VM to a prior snapshot using merge_vm.py.

merge_vm.py restores a VM to a previous snapshot. With a "--snapshots" option it outputs all snapshots in the cluster. You can use this output to figure out which snapshot to restore your VM to.


