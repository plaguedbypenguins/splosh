#!/usr/bin/python3

import sys, hashlib

# rjh; Wed 26 Jul 2023 17:26:20 AEST
# Licensed under the GPLv3 or later
#
# milan nodes have 8 numa nodes, each with 8 cores
# pick X random cores inside X different numa nodes
#
# use this if lscpu looks like eg.
#  NUMA:
#      NUMA node(s):          8
#      NUMA node0 CPU(s):     0-7
#      NUMA node1 CPU(s):     8-15
#      NUMA node2 CPU(s):     16-23
#      NUMA node3 CPU(s):     24-31
#      NUMA node4 CPU(s):     32-39
#      NUMA node5 CPU(s):     40-47
#      NUMA node6 CPU(s):     48-55
#      NUMA node7 CPU(s):     56-63

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

h = hashlib.sha1(u.encode('ascii')).hexdigest()

# start from least signif bytes
val = []
l = len(h)
i = 0

# pick a starting numa node
b = h[l-i-2:l-i]   # pull off 2 bytes at a time == 00 to ff
numa = (8*int(b, 16))//256    # 0 to 7

for k in range(c):
   i += 2
   b = h[l-i-2:l-i]   # pull off 2 bytes at a time == 00 to ff
   core = (8*int(b, 16))//256    # 0 to 7
   #print('numa', numa, 'core', core)
   j = 8*numa+core
   if j < m or j > M:
       numa += 1
       numa %= 8
       continue
   val.append(j)
   # go to next numa node along
   numa += 1
   numa %= 8

   if i > l-2:
       # ran out of hashes. hash more...
       h = hashlib.sha1((u*x).encode('ascii')).hexdigest()
       i = -2

#print val
val.sort()
s = ''
for v in val:
   s += '%d,' % v
s = s[:-1]

print(s)
sys.exit(0)
