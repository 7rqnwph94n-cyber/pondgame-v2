#!/bin/zsh
set -eu
project_dir="$(cd "$(dirname "$0")/../.." && pwd -P)"
destination="$HOME/Desktop/Play Pondlife.app"
if [[ -e "$destination" || -L "$destination" ]]; then
  if [[ -L "$destination" && "$(readlink "$destination")" == "$project_dir/Play Pondlife.app" ]]; then
    print "Desktop launcher already installed."
    exit 0
  fi
  print "An unrelated launcher already exists at $destination; preserving it."
  exit 1
fi
ln -s "$project_dir/Play Pondlife.app" "$destination"
print "Installed $destination"
