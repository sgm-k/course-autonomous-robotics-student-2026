#!/usr/bin/env bash
set -euo pipefail

course_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo "ERROR: /opt/ros/jazzy/setup.bash がありません。先に install.sh を実行してください。" >&2
  exit 1
fi

set +u
# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
set -u
cd "${course_repo_dir}/ros2_ws"
colcon build --symlink-install

# 新しいターミナルを開いたときに、教材の設定が自動で読み込まれるようにする（1回だけ書き足す）。
# これで、ターミナルを開くたびに source scripts/env.sh を打たなくてよくなる。
bashrc_marker="# autonomous-robotics-student: ROS 2 と教材の設定を読み込む"
if [[ -f "${HOME}/.bashrc" ]] && ! grep -qF "${bashrc_marker}" "${HOME}/.bashrc"; then
  {
    echo ""
    echo "${bashrc_marker}"
    echo "[ -f \"${course_repo_dir}/scripts/env.sh\" ] && source \"${course_repo_dir}/scripts/env.sh\" >/dev/null 2>&1"
  } >> "${HOME}/.bashrc"
  echo "新しいターミナルでも ROS 2 のコマンドがすぐ使えるように設定しました。"
fi

echo
echo "ビルドが完了しました。"
