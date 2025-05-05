#!/bin/sh
#https://unix.stackexchange.com/a/230050
#for a in $(make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | grep txt)
#    do make "$a"
#done
make --jobs --ignore-errors --always-make $(make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | grep txt)
