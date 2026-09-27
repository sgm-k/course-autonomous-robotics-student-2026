#!/usr/bin/env bash
set -euo pipefail

course_ros_distro="jazzy"
course_ubuntu_codename="noble"
course_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -r /etc/os-release ]]; then
  echo "ERROR: Ubuntuを確認できません。" >&2
  exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
if [[ "${VERSION_CODENAME:-}" != "${course_ubuntu_codename}" ]]; then
  echo "ERROR: Ubuntu 24.04 (noble) が必要です。現在: ${PRETTY_NAME:-unknown}" >&2
  exit 1
fi

sudo apt update
sudo apt upgrade -y
sudo apt install -y curl git software-properties-common
sudo add-apt-repository -y universe

if [[ ! -f /etc/apt/sources.list.d/ros2.sources ]] && \
   [[ ! -f /etc/apt/sources.list.d/ros2-latest.list ]]; then
  ros_apt_version="$({
    curl -fsSL https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
      | sed -n 's/.*"tag_name": "\([^"]*\)".*/\1/p'
  } | head -n 1)"
  if [[ -z "${ros_apt_version}" ]]; then
    echo "ERROR: ROS apt sourceのバージョンを取得できません。" >&2
    exit 1
  fi
  ros_apt_deb="/tmp/ros2-apt-source-${ros_apt_version}.deb"
  curl -fsSL -o "${ros_apt_deb}" \
    "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ros_apt_version}/ros2-apt-source_${ros_apt_version}.${course_ubuntu_codename}_all.deb"
  sudo dpkg -i "${ros_apt_deb}"
fi

sudo apt update
sudo apt install -y \
  "ros-${course_ros_distro}-desktop" \
  "ros-${course_ros_distro}-mvsim" \
  "ros-${course_ros_distro}-navigation2" \
  "ros-${course_ros_distro}-nav2-bringup" \
  "ros-${course_ros_distro}-slam-toolbox" \
  "ros-${course_ros_distro}-teleop-twist-keyboard" \
  python3-colcon-common-extensions \
  python3-matplotlib \
  python3-rosdep \
  mesa-utils

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi
rosdep update

set +u
# shellcheck disable=SC1091
source "/opt/ros/${course_ros_distro}/setup.bash"
set -u
rosdep install \
  --from-paths "${course_repo_dir}/ros2_ws/src" \
  --ignore-src -r -y \
  --rosdistro "${course_ros_distro}"

"${course_repo_dir}/scripts/build.sh"
"${course_repo_dir}/scripts/doctor.sh"
