#!/usr/bin/env bash
sudo renice -20 $$
for (( i=1; i<6; i++ )) ; do time python -OO ./asyncResultParser.py >/dev/null; done
