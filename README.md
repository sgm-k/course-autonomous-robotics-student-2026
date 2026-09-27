# 学生用教材

授業の演習で使う教材です。ROS 2 Jazzyと移動ロボットシミュレータMVSimを使います。
基準環境はWindows 11、WSL2、Ubuntu 24.04です。

## 取得とセットアップ

Ubuntu端末で実行します。詳しい手順は、授業で配る手順書（準備編）にあります。

```bash
cd ~
git clone https://github.com/sgm-k/course-autonomous-robotics-student-2026.git autonomous-robotics-student
cd autonomous-robotics-student
./scripts/install.sh
./scripts/doctor.sh
./scripts/build.sh
```

`install.sh`はROS 2、MVSim、RViz2、SLAM Toolbox、Nav2を導入します。初回は時間が
かかるため、電源とネットワークを確保してください。

## フォルダの中身

| フォルダ | 中身 |
|---|---|
| `scripts/` | インストール、診断、ビルド、起動のコマンド |
| `ros2_ws/` | 授業用のROS 2パッケージ（ワールド、起動ファイル、設定） |
| `src/` | 自分のコードを置く場所 |

配布されたファイルは書き換えず、自分のコードは`src/`に置いてください。

## シミュレーションの起動

```bash
./scripts/run_demo.sh
```

別端末でロボットを操作します。

```bash
source scripts/env.sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

MVSimのLiDAR生データは`/laser1`、SLAM・AMCL・Nav2用に時刻をそろえたデータは
`/scan`です。通常のLaunchで`scan_relay`が自動起動します。

## 軽量モード

MVSimのGUIを表示せず、RViz2だけを使用します。

```bash
source scripts/env.sh
ros2 launch course_robot course.launch.py headless:=true
```

GUIをすべて無効にする場合は次のようにします。

```bash
ros2 launch course_robot course.launch.py \
  headless:=true use_rviz:=false
```

## SLAM・自己位置推定・Nav2

第6回以降は次の起動ファイルを使用します。`maps/week06.yaml`は、自分で作成して`maps/`に保存した地図です。

```bash
# 地図作成
ros2 launch course_robot slam.launch.py headless:=true

# AMCL
ros2 launch course_robot localization.launch.py \
  map:=$PWD/maps/week06.yaml headless:=true

# Nav2
ros2 launch course_robot navigation.launch.py \
  map:=$PWD/maps/week06.yaml headless:=true
```

MVSimは`/clock`をpublishしないため、本教材の設定では`use_sim_time: false`です。

## 更新

教材を更新したときは授業で案内します。案内があったら次を実行してください。

```bash
cd ~/autonomous-robotics-student
git pull
./scripts/build.sh
```

配布されたファイルを書き換えていると、`git pull`が失敗することがあります。

## ライセンス

BSD 3-Clause License（[LICENSE](LICENSE)）です。
Nav2から取り込んだ設定ファイルについては[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)を参照してください。
