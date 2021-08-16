#!/usr/bin/python

import sys, hashlib

# rjh; Fri Jun 29 00:44:34 AEST 2018
# Licensed under the GPLv3 or later
#
# hash a string to generate a deterministic list of X numbers in a given range.
# used for cpuset allocations on login nodes.
# also make sure there's a similar amount of odd and evens so that users have 
# cores on both sockets.
#
# use this even/odd version if lscpu says eg.
#  NUMA node0 CPU(s):     0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34
#  NUMA node1 CPU(s):     1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35


if len(sys.argv) != 5:
   print 'usage:', sys.argv[0], 'string X min max'
   print '   eg. username 4 1 30  ->  7,22,29,30'
   sys.exit(1)

u = sys.argv[1]   # eg. rjh
c = int(sys.argv[2])  # 4
m = int(sys.argv[3])  # 1
M = int(sys.argv[4])  # 30
r = M-m+1   # 30

if c > M-m+1:
   print 'range not big enough'
   sys.exit(1)

h = hashlib.sha1(u).hexdigest()

# start from least signif bytes
val = []
l = len(h)
x = 1
i = 0

# pick even or odd first
b = h[l-i-2:l-i]   # pull off 2 bytes at a time == 00 to ff
even = 2*int(b, 16)/256    # 0 to 1
i += 2

while len(val) != c:
   b = h[l-i-2:l-i]   # pull off 2 bytes at a time == 00 to ff
   rn = int(b, 16)    # 0 to 255
   rn *= r
   rn /= 256   # 0 to r-1
   odd = rn % 2
   if even == 1 and odd == 1:
      #print 'even', even, 'rn', rn,
      rn += 1
      rn %= r
      #print 'to', rn
   elif even == 0 and odd == 0:
      #print 'even', even, 'rn', rn,
      rn -= 1
      rn += r
      rn %= r
      #print 'to', rn
   even += 1
   even %= 2 
   i += 2
   if i > l-2:
      # ran out of hashes. hash more...
      h = hashlib.sha1(u*x).hexdigest()
      x += 1
      i = 0
      continue
   if rn in val:
      continue
   val.append(rn)

#print val
val.sort()
s = ''
for v in val:
   s += '%d,' % (m+v)
s = s[:-1]

print s
sys.exit(0)
