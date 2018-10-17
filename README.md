# splosh
Ssh Pam LOgin SHell cgroup environment 
--------------------------------------

use cpu, cpuset, and memcg cgroups to protect cluster login nodes from users doing silly things and also protects users from each other. cpu usage is fairshared and memory and cores can be limited.

setup is pretty simple.

firstly, copy `pam_user_cgroup` to eg. `/opt/root/` and `chmod +x` it. then edit the script to choose which resources you want users to be able to access and which to keep for the system.

secondly, pick how you want cpus to be allocated to users. if you are being nice to them you would spread their cpus over all available sockets. examples are provided for a hash based deterministic spreading of cores across dual socket nodes with even/odd (eg. skylake) and sequential cpu enumeration (eg. sandy bridgy).eg.

    cp hashUserToRange.evenOdd.py /opt/root/hashUserToRange.py
    chmod +x /opt/root/hashUserToRange.py

thirdly, add something like

    #session    required     pam_exec.so log=/tmp/pam.txt /opt/root/pam_user_cgroup
    session    required     pam_exec.so /opt/root/pam_user_cgroup

to the end of `/etc/pam.d/sshd`.
set `debug=1` in the `pam_user_cgroup` script and use the pam debugging line above until you are confident it's working.

finally, enjoy no more login node crashes or ooms. set and forget.

quirks
* this version is for RHEL7 era and similar systemd machines, and plays nicely with the `/sys/fs/cgroup` hierarchy there.
let me know if you want a RHEL6 "shared cgroup" version instead.
* selinux (eg. on fedora) may disallow pam (and hence this tool) from automatically creating the top level dir. give it a go and see. you may need to make the top level "corral" cgroup for users separately at boot.

Robin Humble.  insert this github username @ gmail.com
