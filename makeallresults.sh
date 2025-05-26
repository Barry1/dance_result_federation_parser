#!/bin/sh
#https://unix.stackexchange.com/a/230050
#for a in $(make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | grep txt)
#    do make "$a"
#done

targets=$(make -qp |
	awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' |
	grep txt |
	grep -v GOC_ |
	sort)
goctargets="\nGOC_2020.txt\nGOC_2021.txt\nGOC_2022.txt\nGOC_2023.txt\nGOC_2024.txt\nGOC_2025.txt"
alltargets="${targets} ${goctargets}"
mdtargets=$(echo "${alltargets}" | shuf | sed -e 's/.txt/.md/g')
# shuffled to be not so reproducible
echo "Targets: ${mdtargets}"
# for make understanding multiple targets
# shellcheck disable=SC2086
make --jobs 1 -f Makefile.githubworkflow --ignore-errors --always-make ${mdtargets}
