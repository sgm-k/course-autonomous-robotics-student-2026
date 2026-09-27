#!/usr/bin/env bash
set -euo pipefail

course_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "${course_repo_dir}/scripts/env.sh"

if ! ros2 pkg prefix course_robot >/dev/null 2>&1; then
  echo "ERROR: 教材パッケージが見つかりません。./scripts/build.sh を実行してください。" >&2
  exit 1
fi

exec ros2 launch course_robot course.launch.py "$@"

