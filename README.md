# Lattice Land

This is a meta-repository about the [lattice land project](https://github.com/lattice-land) to explain how to get started contributing to this project and the [turbo](https://github.com/ptal/turbo/) constraint solver.

## Getting Started

Turbo is relying on several libraries from the Lattice Land project, which are used to implement different components of the solver (e.g., propagation, search, interval arithmetic).
When developing Turbo it is easier to have these repositories grouped in one common directory and use these _local repositories_ as the dependencies.
Hence, when you change something in `lala-core`, you don't need to commit and push that directory to have the changes accessible in Turbo.

```
mkdir lattice-land
cd lattice-land
git clone https://github.com/NVIDIA/cccl.git
git clone https://github.com/xcsp3team/XCSP3-CPP-Parser.git
git clone git@github.com:yhirose/cpp-peglib.git
git clone git@github.com:lattice-land/cuda-battery.git
git clone git@github.com:lattice-land/lala-core.git
git clone git@github.com:lattice-land/lattice-land.github.io.git
git clone git@github.com:lattice-land/lala-pc.git
git clone git@github.com:lattice-land/lala-power.git
git clone git@github.com:lattice-land/lala-parsing.git
git clone git@github.com:lattice-land/.github.git
git clone git@github.com:ptal/turbo.git
```

All projects have the same set of presets, therefore they are configured and compiled in the same way.
To avoid downloading the dependencies when compiling Turbo (or other projects), you can use the preset `cmake --workflow --preset gpu-release-local --fresh` and similarly for the others (appending `-local` to the preset).
For convenience, you can set up a bunch of aliases in your `.bashrc`:

```
alias gpudebug="time cmake --workflow --preset gpu-debug-local --fresh"
alias gpurelease="time cmake --workflow --preset gpu-release-local --fresh"
alias cpudebug="time cmake --workflow --preset cpu-debug-local --fresh"
alias cpurelease="time cmake --workflow --preset cpu-release-local --fresh"

alias gpurelease2="time cmake --workflow --preset gpu-release --fresh"
alias gpudebug2="time cmake --workflow --preset gpu-debug --fresh"
alias cpurelease2="time cmake --workflow --preset cpu-release --fresh"
alias cpudebug2="time cmake --workflow --preset cpu-debug --fresh"
```

Alternatively, you can use these commands without presets and workflow (it is useful compilation scenario falling outside what is provided by the presets):

```
cmake -DCMAKE_BUILD_TYPE=Release -DGPU=ON -DREDUCE_PTX_SIZE=ON -DCMAKE_VERBOSE_MAKEFILE=ON -Bbuild/gpu-release
cmake --build build/gpu-release
```

# Development Workflow

We always work on `main`, and use tags (e.g., `v1.1.0`) to point to compilable, tested and hopefully working versions.
The script `release.py` is useful to release a new project as well as its documentation automatically.
For instance, to release a new minor version of cuda-battery:

```
python3 release.py --kind minor cuda-battery
```

There are other options to this script, type `python3 release.py -h` to get them all.
