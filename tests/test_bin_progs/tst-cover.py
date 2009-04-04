"""
A simple little program for testing figleaf command stuff.
"""
import sys
print 'ARGV:', '::'.join(sys.argv[1:])

a = 1
b = 2
c = 3

if a:
    print 'hello, world!'
else:
    print 'goodbye'
