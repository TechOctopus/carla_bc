#!/bin/bash
set -e

# Download and unpack ns-3

curl -O https://www.nsnam.org/releases/ns-allinone-3.44.tar.bz2
tar xjf ns-allinone-3.44.tar.bz2
rm ns-allinone-3.44.tar.bz2

echo "[INFO] ns-3 downloaded and unpacked"

# Build ns-3

cd ns-allinone-3.44
./build.py --enable-examples --enable-tests

echo "[INFO] ns-3 installation completed"

# Copy our bridge code to ns-3

cd ..
cp -r ./ns3/* ./ns-allinone-3.44/ns-3.44/scratch/

echo "[INFO] Setup completed successfully!"
