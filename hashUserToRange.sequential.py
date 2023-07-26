#!/usr/bin/python3

import sys, hashlib

# rjh; Fri Jun 29 00:44:34 AEST 2018
# Licensed under the GPLv3 or later
#
# hash a string to generate a deterministic list of X numbers in a given range.
# used for cpuset allocations on login nodes.
# also make sure there's a similar amount on both sockets.
#
# use this sequential version if lscpu says:
#  NUMA node0 CPU(s):     0-5
#  NUMA node1 CPU(s):     6-11

# NOTE - this version will only work as-is for 12 core nodes.
# edit the below for your node type.

# should construct this from `lscpu -p` but for now...
# HACK HACK HACK
# assume dual 6 core sandybridge
physcpus=[range(0,6), range(6,12)]

# or for single socket VMs like eg.
#  NUMA node0 CPU(s):   0-7
#
#physcpus=[range(0,8)]

if len(sys.argv) != 5:
   print('usage:', sys.argv[0], 'string X min max')
   print('   eg. username 4 1 30  ->  7,22,29,30')
   sys.exit(1)

u = sys.argv[1]   # eg. rjh
c = int(sys.argv[2])  # 4
m = int(sys.argv[3])  # 1
M = int(sys.argv[4])  # 30
r = M-m+1   # 30

if c > M-m+1:
   print('range not big enough')
   sys.exit(1)

sockets=len(physcpus)

# allowed cpus
cpus = []
for s in range(sockets):
   cc = []
   for i in physcpus[s]:
      if i >= m and i <= M:
         cc.append(i)
   cpus.append(cc)
#print('allowed cpus', cpus)

# want approx equal on each socket
cnt = {}
cntmax = {}
s = 0
for s in range(sockets):
   cnt[s] = 0
   cntmax[s] = 0
s = 0
for i in range(c):
   found=0
   while not found:
      if cntmax[s] < len(cpus[s]):
         cntmax[s] += 1
         found=1
      s += 1
      s %= sockets
#print('cntmax', cntmax)

h = hashlib.sha1(u.encode('ascii')).hexdigest()

# start from least signif bytes
val = []
l = len(h)
x = 1
i = 0
s = 0

while len(val) != c:
   if len(cpus[s]) == 0:   # skip sockets with no cpus on them
      s += 1
   b = h[l-i-2:l-i]   # pull off 2 bytes at a time == 00 to ff
   rn = int(b, 16)    # 0 to 255
   rn *= len(cpus[s])
   rn //= 256   # 0 to numberOfCpusOnSocket-1
   rn = cpus[s][rn]
   i += 2
   if i > l-2:
      # ran out of hashes. hash more...
      h = hashlib.sha1((u*x).encode('ascii')).hexdigest()
      x += 1
      i = 0
      continue
   if rn in val:
      continue
   val.append(rn)
   cnt[s] += 1
   if cnt[s] == cntmax[s]:
      s += 1

#print(val)
val.sort()
s = ''
for v in val:
   s += '%d,' % v
s = s[:-1]

print(s)
sys.exit(0)
