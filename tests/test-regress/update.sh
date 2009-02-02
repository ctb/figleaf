#! /bin/bash
# specify version on cmd line, e.g. 'update.sh 2.5' for python2.5.
VER=$1
for i in tst*.py
do
   python$VER ../../bin/figleaf $i
   python$VER ../../bin/figleaf2cover
   mv $i.cover $i.cover.$VER
   rm .figleaf
done
