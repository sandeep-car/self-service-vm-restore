# self-service-vm-restore

Self service VM restore will be available in a future release of Prism Central. Until then you can use these scripts.
HOWTO.txt describes the process required to configure a Deployment VM. Run scripts from this Deployment VM.
Please be sure to update variables in clusterconfig.py also.

The use case here is to:

a. Take a snapshot (or more than one snapshot) of a User VM from Prism Element.

b. Log into the deployment VM, then restore the User VM to a prior snapshot using merge_vm.py.

merge_vm.py restores a VM to a previous snapshot. With a "--snapshots" option it outputs all snapshots in the cluster. You can use this output to figure out which snapshot to restore your VM to.

Security concerns:

As written, the program allows anyone to restore a snapshot to any user VM (as long as that snapshot belongs to the VM). This means user A can mistakenly restore a VM belonging to user B, which is not good. A way around this is to specify the user VM(s) that the script can operate on, as a variable in clusterconfig.py. Then don't allow any snapshot restores of a VM unless it is part of the variable. Also means the Deployment VM must have a root user as well as an ordinary user who is not allowed to view/modify our Python code.


