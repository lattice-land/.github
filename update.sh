#!/bin/bash

projects=("cuda-battery" "lala-core" "lala-parsing" "lala-power" "lala-pc" "turbo" "lattice-land.github.io" ".github")

for project in ${projects[@]}; do
  cd ../${project}
  git pull
done
