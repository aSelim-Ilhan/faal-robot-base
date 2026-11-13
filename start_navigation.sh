#!/bin/bash

echo "=========================================="
echo " AKIBA ROBOT - NAVIGATION SİSTEMİ"
echo "=========================================="
echo ""

export ROS_DOMAIN_ID=10

# Port izinleri
sudo chmod 666 /dev/ttyUSB1 2>/dev/null

echo "1  micro-ROS Agent başlatılıyor..."
gnome-terminal --title="micro-ROS Agent" --geometry=80x20+0+0 -- bash -c "
    export ROS_DOMAIN_ID=10;
    echo ' micro-ROS Agent başlatılıyor...';
    ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyACM1;
    exec bash"

sleep 2

echo "2️⃣  RPLIDAR S2 M1 başlatılıyor..."
gnome-terminal --title="RPLIDAR S2 M1" --geometry=80x20+0+300 -- bash -c "
    export ROS_DOMAIN_ID=10;
    sudo chmod 666 /dev/ttyUSB0;
    echo '📡 LIDAR S2 M1 taraması başlatılıyor...';
    ros2 run rplidar_ros rplidar_node --ros-args \
      -p serial_port:=/dev/ttyUSB0 \
      -p serial_baudrate:=1000000 \
      -p frame_id:=laser_link \
      -p scan_mode:=Standard \
      -p angle_compensate:=true;
    exec bash"

sleep 2

echo "3  Odometry + EKF + TF başlatılıyor..."
gnome-terminal --title="Core System" --geometry=80x20+0+600 -- bash -c "
    export ROS_DOMAIN_ID=10;
    source ~/faal_ws/install/setup.bash;
    echo '  Core sistem başlatılıyor...';
    ros2 launch akiba_odometry akiba_full.launch.py;
    exec bash"

sleep 5

echo "4  Navigation Stack başlatılıyor..."
gnome-terminal --title="Navigation Stack" --geometry=80x30+800+0 -- bash -c "
    export ROS_DOMAIN_ID=10;
    source ~/faal_ws/install/setup.bash;
    echo '  Navigation (AMCL + Nav2) başlatılıyor...';
    echo '';
    echo ' Lifecycle manager bekleniyor...';
    ros2 launch akiba_odometry navigation.launch.py;
    exec bash"

sleep 8

echo "5  RViz2 Navigation başlatılıyor..."
gnome-terminal --title="RViz2 Navigation" --geometry=80x20+800+400 -- bash -c "
    export ROS_DOMAIN_ID=10;
    echo ' RViz2 başlatılıyor...';
    sleep 3;
    rviz2;
    exec bash"

sleep 5



echo "6  Initial Pose gönderiliyor..."
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: 'map'
pose:
  pose:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
  covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891909122467]
" > /dev/null 2>&1

sleep 2

echo ""
echo "=========================================="
echo " NAVIGATION SİSTEMİ BAŞLATILDI!"
echo "=========================================="
echo ""
echo " ÇALIŞAN SİSTEMLER:"
echo "   1  micro-ROS Agent (STM32)"
echo "   2  RPLIDAR A1"
echo "   3  Odometry + EKF + TF"
echo "   4  Navigation Stack (AMCL + Nav2)"
echo "   5  RViz2"
echo "   6  Initial Pose (Otomatik gönderildi!)"
echo ""
echo ""
echo " Sistem hazır: ~20 saniye"
echo ""
echo " KULLANIM:"
echo "   1. RViz2'de Fixed Frame: 'map' yap"
echo "   2. Add → Map → Topic: /map"
echo "   3. Add → LaserScan → Topic: /scan"
echo "   4. AMCL localize oldu! (yeşil oklar görünüyor)"
echo "   5. Toolbar'dan '2D Goal Pose' seç"
echo "   6. Hedef gönder!"
echo ""
echo " DURDURMA: ~/stop_navigation.sh"
echo ""
