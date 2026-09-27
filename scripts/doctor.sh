#!/usr/bin/env bash
set -u

course_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
warnings=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }
warn() { printf '[WARN] %s\n' "$1"; warnings=$((warnings + 1)); }

printf '環境診断\n\n'

if grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
  pass "WSL環境"
else
  warn "WSLではありません（通常のUbuntuなら問題ありません）"
fi

if grep -qi WSL2 /proc/sys/kernel/osrelease 2>/dev/null; then
  pass "WSL2"
elif grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
  fail "WSL2ではありません"
fi

if [[ -r /etc/os-release ]] && grep -q 'VERSION_ID="24.04"' /etc/os-release; then
  pass "Ubuntu 24.04"
else
  warn "基準環境のUbuntu 24.04ではありません"
fi

if [[ -n "${WAYLAND_DISPLAY:-}" || -n "${DISPLAY:-}" ]]; then
  pass "GUI表示変数"
else
  fail "WAYLAND_DISPLAYとDISPLAYが空です"
fi

if [[ -d /mnt/wslg ]] || [[ -n "${DISPLAY:-}" ]]; then
  pass "GUI表示基盤"
else
  fail "WSLgまたはX11表示を確認できません"
fi

if [[ -e /dev/dxg ]] || [[ -d /dev/dri ]]; then
  pass "GPU描画デバイス"
else
  warn "GPU描画デバイスを確認できません"
fi

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  pass "ROS 2 Jazzy"
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
  set -u
else
  fail "ROS 2 Jazzy"
fi

for course_pkg in mvsim rviz2 teleop_twist_keyboard nav2_bringup slam_toolbox; do
  if command -v ros2 >/dev/null 2>&1 && ros2 pkg prefix "${course_pkg}" >/dev/null 2>&1; then
    pass "ROSパッケージ: ${course_pkg}"
  else
    fail "ROSパッケージ: ${course_pkg}"
  fi
done

if [[ -f /opt/ros/jazzy/lib/libnav2_msgs__rosidl_typesupport_fastrtps_cpp.so ]]; then
  if python3 - <<'PY' >/dev/null 2>&1
import ctypes
ctypes.CDLL(
    '/opt/ros/jazzy/lib/libnav2_msgs__rosidl_typesupport_fastrtps_cpp.so')
PY
  then
    pass "Nav2共有ライブラリの整合性"
  else
    fail "Nav2共有ライブラリが不整合です（sudo apt update && sudo apt upgrade -y を実行）"
  fi
fi

if [[ -f "${course_repo_dir}/ros2_ws/install/setup.bash" ]]; then
  set +u
  # shellcheck disable=SC1091
  source "${course_repo_dir}/ros2_ws/install/setup.bash"
  set -u
  if ros2 pkg prefix course_robot >/dev/null 2>&1; then
    pass "学生用ワークスペース"
  else
    fail "学生用パッケージを検出できません"
  fi
else
  warn "ワークスペースは未ビルドです"
fi

printf '\n結果: FAIL=%d, WARN=%d\n' "${failures}" "${warnings}"
if (( failures > 0 )); then
  exit 1
fi
