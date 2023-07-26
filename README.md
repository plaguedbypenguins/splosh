# splosh
Ssh Pam LOgin SHell cgroup environment 
--------------------------------------

Use cpu, cpuset, and memcg cgroups to protect cluster login nodes from users doing silly things, and also (partially) protect users from each other. Cpu usage is fairshared and memory and cores can be limited. No one user can hog all the cpus or ram, and no combination of users can crash a login node.

Setup is 4 simple steps.

Firstly, copy `pam_user_cgroup` to eg. `/opt/root/` and `chmod +x` it. Then edit the script to choose which resources you want users to be able to access and which to keep for the system. The basic idea is to put all users into one cgroup that essentially protects the node from the users, and then put each user into a sub-cgroup that gives them a deterministic set of cores and typically a generous (overcommitted) amount of ram.

Secondly, pick how you want cores to be allocated to users. If you are being nice to them you would spread their accessible cores over all available sockets. This is so that all numa zones are accessible, and peripheral devices can be accessed more directly. Examples are provided for a hash based deterministic spreading of cores across dual socket nodes with even/odd core enumeration (eg. skylake), dual or single socket sequential core enumeration (eg. sandy bridge, or VMs), and lots of numa nodes like AMD Milan. eg.

    cp hashUserToRange.evenOdd.py /opt/root/hashUserToRange.py
    chmod +x /opt/root/hashUserToRange.py

Thirdly, add something like

    #session    required     pam_exec.so log=/tmp/pam.txt /opt/root/pam_user_cgroup
    session    required     pam_exec.so /opt/root/pam_user_cgroup

to the end of `/etc/pam.d/sshd`. Set `debug=1` in the `pam_user_cgroup` script and use the pam debugging line above until you are confident it's working.

Fourthly, systemd needs to be told to leave tasks in our cgroups alone, otherwise it'll eventually shift them into systemd cgroups. Add the below to the Service block in `/etc/systemd/system/sshd.service`

    # tell systemd to ignore tasks in login node cgroups
    Delegate=yes

Finally, enjoy no more login node crashes. Set and forget.

Quirks
* This is for RHEL7/8 and similar systemd machines, and plays nicely with the `/sys/fs/cgroup` hierarchy there. Let me know if you want a RHEL6 "shared cgroup" version instead.
* In RHEL9 you must tell systemd to use cgroups v1. ie. boot with `systemd.unified_cgroup_hierarchy=0 systemd.legacy_systemd_cgroup_controller`
* selinux (eg. on Fedora) may disallow pam (and hence this tool) from automatically creating the top level dir. Give it a go and see. You may need to make the top level "corral" cgroup for users separately at boot.


Robin Humble.  insert this github username @ gmail.com
