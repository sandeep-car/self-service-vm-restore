# self-service-vm-restore

Self service VM restore will be available in a future release of Prism Central. Until then you can use these scripts.
HOWTO.txt describes the process required to configure a Deployment VM. Run scripts from this Deployment VM.
Please be sure to update variables in clusterconfig.py also. We assume you've created a restapiuser on your cluster 
which has cluster admin privileges but has a different password from the admin user. Please see below for security concerns.

The use case here is to:

a. Take a snapshot (or more than one snapshot) of a User VM from Prism Element.

b. Log into the deployment VM, then restore the User VM to a prior snapshot using merge_vm.py.

merge_vm.py restores a VM to a previous snapshot. With a "--snapshots" option it outputs all snapshots in the cluster.
You can use this output to figure out which snapshot to restore your VM to.

Security concerns:

The biggest security concern with restoring VMs is that user A can mistakenly restore a VM belonging to user B. Workaround 
here is the variable "allowed_vm_list" in clusterconfig.py.

Snapshot restores of a VM are not allowed unless the VM name is included in allowed_vm_list. This also means the 
Deployment VM must have a root user as well as an ordinary user who is not allowed to view/modify Python code. This
is recommended practice anyway because restapiuser passwords are stored in the clusterconfig.py file.

Possible enhancements:
"Allowed_vm_list" could be read from a CSV instead of from a variable.
