#!/bin/bash

# Akiba Robot - Tam Sistem Başlatma Scripti
# Tüm sensörler + Odometry + EKF + SLAM

echo "🤖 Akiba Robot Sistemi Başlatılıyor..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ROS Domain ID
export ROS_DOMAIN_ID=10

# Workspace source
source ~/faal_ws/install/setup.bash

echo ""
echo "1️⃣  micro-ROS Agent başlatılıyor (STM32)..."
gnome-terminal --title="micro-ROS Agent" --geometry=80x20+0+0 -- bash -c "
    export ROS_DOMAIN_ID=10;
    echo '🔌 STM32 bağlantısı kuruluyor...';
    ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyACM1;
    exec bash"

sleep 2

echo "2️⃣  BNO055 IMU başlatılıyor..."
gnome-terminal --title="BNO055 IMU" --geometry=80x20+0+400 -- bash -c "
    export ROS_DOMAIN_ID=10;
    echo '🧭 IMU sensörü başlatılıyor...';
    ros2 run bno055 bno055 --ros-args \
      -p uart_port:=/dev/ttyUSB0 \
      -p uart_baudrate:=115200 \
      -p frame_id:=imu_link \
      --remap /bno055/imu:=/imu/data;
    exec bash"

sleep 2

echo "2️⃣  RPLIDAR S2 M1 başlatılıyor..."
gnome-terminal --title="RPLIDAR S2 M1" --geometry=80x20+0+300 -- bash -c "
    export ROS_DOMAIN_ID=10;
    sudo chmod 666 /dev/ttyUSB0;
    echo '📡 LIDAR S2 M1 taraması başlatılıyor...';
    ros2 run rplidar_ros rplidar_node --ros-args \
      -p serial_port:=/dev/ttyUSB0\
      -p serial_baudrate:=1000000 \
      -p frame_id:=laser_link \
      -p scan_mode:=Standard \
      -p angle_compensate:=true;
    exec bash"

sleep 2

echo "4️⃣  Odometry + EKF + TF sistemi başlatılıyor..."
gnome-terminal --title="Akiba Core System" --geometry=100x25+900+400 -- bash -c "
    export ROS_DOMAIN_ID=10;
    source ~/faal_ws/install/setup.bash;
    echo '⚙️  Core sistem başlatılıyor...';
    ros2 launch akiba_odometry akiba_full.launch.py;
    exec bash"

sleep 3

echo "5️⃣  SLAM Toolbox başlatılıyor..."
gnome-terminal --title="SLAM Toolbox" --geometry=100x25+450+250 -- bash -c "
    export ROS_DOMAIN_ID=10;
    source ~/faal_ws/install/setup.bash;
    echo '🗺️  SLAM haritalama başlatılıyor...';
    ros2 launch akiba_odometry slam.launch.py;
    exec bash"

sleep 3

echo "6️⃣  RViz2 görselleştirme açılıyor..."
gnome-terminal --title="RViz2" --geometry=80x30+1800+0 -- bash -c "
    export ROS_DOMAIN_ID=10;
    sleep 2;
    echo '🎨 RViz2 başlatılıyor...';
    rviz2;
    exec bash"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tüm sistem başlatıldı!"
echo ""
echo "📊 Sistem Durumu:"
echo "   ├─ micro-ROS Agent  : /dev/ttyACM1"
echo "   ├─ BNO055 IMU       : /dev/ttyUSB0"
echo "   ├─ RPLIDAR A1       : /dev/ttyUSB1"
echo "   ├─ Odometry + EKF   : ✓"
echo "   ├─ SLAM Toolbox     : ✓"
echo "   └─ RViz2            : ✓"
echo ""
echo "🎮 Kontrol için:"
echo "   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/akiba_1/cmd_vel"
echo ""
echo "🗺️  RViz2 Ayarları:"
echo "   1. Fixed Frame → 'map'"
echo "   2. Add → /map → Map"
echo "   3. Add → /scan → LaserScan"
echo "   4. Add → TF"
echo ""
