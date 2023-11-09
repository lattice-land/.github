import argparse
import os
import subprocess
from semantic_version import *
from git import *
import shutil

def call(cmd):
  print("  " + cmd)
  res = subprocess.call(cmd, shell=True)
  if(res != 0):
    print("Command `" + cmd + "` terminated with an error code!")
    exit(1)

def get_version_tag(repo_path):
  repo = Repo(repo_path)
  tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
  for t in reversed(tags):
    if t.name[0] == "v":
      return str(t.name)
  return "v0.0.0"

def check_if_latest(deps_name, deps_version):
  repo_path = "../" + deps_name
  if os.path.exists(repo_path):
    tag = get_version_tag(repo_path)
    if tag != deps_version:
      print("Dependency `" + deps_name + "` is set to an older version (`" + deps_version + "`), the newest dependency is`" + tag + "`")
      exit(1)
    else:
      print("  Dependency `" + deps_name + "` version `" + deps_version + "`")
  else:
    if deps_name != "googletest":
      print("Dependency `" + deps_name + "` unchecked because the repository does not exist locally.")

# pre: must be in the directory of the repository.
def check_dependencies():
  with open("CMakeLists.txt") as f:
    cmake = f.read()
    state = 0
    deps_name = ""
    deps_version = ""
    for line in cmake.split("\n"):
      line = line.strip()
      if state == 0:
        if "FetchContent_Declare(" == line:
          state = 1
      elif state == 1:
        deps_name = line.replace("_", "-")
        state = 2
      elif state == 2:
        state = 3
      elif state == 3:
        deps_version = line.split(" ")[-1].strip()
        check_if_latest(deps_name, deps_version)
        state = 0

def main():
  parser = argparse.ArgumentParser(
              prog = 'release',
              description = 'Script to release new version of git projects.')
  parser.add_argument('repository')
  parser.add_argument('--kind', required=True, choices=['patch', 'minor', 'major'])
  parser.add_argument('--skiptests', action='store_true')
  parser.add_argument('--skipcheckdeps', action='store_true')
  parser.add_argument('--skiptag', action='store_true')
  parser.add_argument('--skipdoc', action='store_true')
  args = parser.parse_args()
  print("Updating " + args.repository + "...")
  os.chdir(os.getcwd() + "/../" + args.repository)
  if not args.skiptests:
    call("cmake --workflow --preset gpu-release --fresh")
    call("cmake --workflow --preset cpu-release --fresh")

  if not args.skipcheckdeps:
    check_dependencies()

  latest_tag = get_version_tag(".")
  tag_name = latest_tag
  semver = Version.coerce(tag_name[1:])
  if not args.skiptag:
    repo = Repo(".")
    if repo.is_dirty():
      print("Git repository has uncommitted changes.")
      exit(1)

    if len(list(repo.iter_commits('main@{u}..main'))) != 0:
      print("Git repository has unpushed changes.")
      exit(1)

    if(args.kind == "patch"):
      semver = semver.next_patch()
    elif(args.kind == "minor"):
      semver = semver.next_minor()
    else:
      semver = semver.next_major()

    tag_name = "v"+str(semver)
    new_tag = repo.create_tag(tag_name, message='Version "{0}"'.format(str(semver)))
    repo.remotes.origin.push(new_tag)

  if not args.skipdoc:
    # Update the documentation
    if os.path.exists("build/doc"):
      shutil.rmtree("build/doc")
    os.mkdir("build/doc")
    call("cmake -DCMAKE_BUILD_TYPE=Release -DGPU=ON -D{0}_BUILD_TESTS=OFF -DREDUCE_PTX_SIZE=ON -Bbuild/doc".format(args.repository.upper().replace("-", "_")))
    call("cmake --build build/doc")
    call("mkdir -p ../lattice-land.github.io/{0}".format(args.repository))
    call("cp -r build/doc/html/* ../lattice-land.github.io/{0}/".format(args.repository))

    doc_repo = Repo("../lattice-land.github.io/")
    doc_repo.git.add(all=True)
    doc_repo.index.commit("Update documentation of {0}-{1}.".format(args.repository, tag_name))
    doc_repo.remotes.origin.push()

if __name__ == "__main__":
  main()
