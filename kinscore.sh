#!/bin/bash

python kinscore.py $1
# if [ ! -e synbreed ]; then
#     R CMD INSTALL --library="." --clean lib/synbreed_0.11-29.tar.gz &> /dev/null
# fi
R CMD INSTALL --library="." --clean lib/synbreed_0.11-29.tar.gz &> /dev/null
R CMD BATCH --slave --no-timing kinscore.R
rm -f kinscore.Rout
