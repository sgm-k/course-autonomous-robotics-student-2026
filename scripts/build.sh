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

echo
echo "ビルドが完了しました。新しい端末では次を実行してください。"
echo "  cd ${course_repo_dir}"
echo "  source scripts/env.sh"
