#!/usr/bin/env bash

course_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo "ERROR: ROS 2 Jazzyが見つかりません。先に ./scripts/install.sh を実行してください。" >&2
  return 1 2>/dev/null || exit 1
fi

# ROSのsetup.bashは未定義変数を参照することがあるため、呼出側が
# `set -u` を使っていてもsourceできるように一時的に解除する。
course_restore_nounset=0
if [[ $- == *u* ]]; then
  course_restore_nounset=1
  set +u
fi
# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
if (( course_restore_nounset )); then
  set -u
fi

if [[ -f "${course_repo_dir}/ros2_ws/install/setup.bash" ]]; then
  # shellcheck disable=SC1091
  if [[ $- == *u* ]]; then
    set +u
    # shellcheck disable=SC1091
    source "${course_repo_dir}/ros2_ws/install/setup.bash"
    set -u
  else
    # shellcheck disable=SC1091
    source "${course_repo_dir}/ros2_ws/install/setup.bash"
  fi
else
  echo "WARNING: ワークスペースが未ビルドです。./scripts/build.sh を実行してください。" >&2
fi

export COURSE_REPO_DIR="${course_repo_dir}"
