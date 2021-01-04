#!/bin/bash

#Ensure we are in right directory.
cd /home/USER/gistemp/src/gistemp4.0/tmp/input/

#Remove old files.
rm *.dat *.inv

#Get new files.
wget https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz
tar -xzf ghcnm.tavg.latest.qcf.tar.gz
rm ghcnm.tavg.latest.qcf.tar.gz
mv ghcnm*/* .
rmdir ghcnm.v4.0.1*

rm SBBX.ERSSTv5.gz
wget https://data.giss.nasa.gov/pub/gistemp/SBBX.ERSSTv5.gz
tar -xzf SBBX.ERSSTv5.gz

rm Ts.strange.v4.list.IN_full
wget https://data.giss.nasa.gov/pub/gistemp/Ts.strange.v4.list.IN_full

mv ghcnm*.dat ghcnm.tavg.qcf.dat
mv ghcnm*.inv v4.inv

cd /home/USER/gistemp/src/gistemp4.0/
/home/USER/anaconda3/bin/python tool/run.py