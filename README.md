# FAAL Akiba — Otonom Mobil Robot Platformu

**Sanayide Dijital 2026 Yarışması**  
**Takım:** FAAL | **Geliştirici:** Ahmet Selim İlhan  
**Platform:** ROS2 Humble · Ubuntu 22.04 · STM32F407

> Bu repo, [AGV-GOREVLER](https://github.com/aSelim-Ilhan/AGV-GOREVLER) projesinin tamamlanmış ve temizlenmiş taban sürümüdür.  
> AGV-GOREVLER'deki görev yürütme katmanının altında çalışan navigasyon, odometri ve lokalizasyon altyapısını içerir.

---

## İçindekiler

- [Sistem Mimarisi](#sistem-mimarisi)
- [TF Ağacı](#tf-ağacı)
- [ROS2 Topic Haritası](#ros2-topic-haritası)
- [Donanım](#donanım)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Konfigürasyon](#konfigürasyon)
- [Sorun Giderme](#sorun-giderme)

---

## Sistem Mimarisi

```
┌──────────────────────────────────────────────────────────────────┐
│                        ROS2 HUMBLE STACK                         │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐  │
│  │ SLAM Toolbox│   │ Navigation2  │   │  robot_localization  │  │
│  │ (async map) │   │ AMCL + Nav2  │   │  EKF (odom + IMU)    │  │
│  └──────┬──────┘   └──────┬───────┘   └──────────┬───────────┘  │
│         │                 │                       │              │
│  ┌──────┴─────────────────┴───────────────────────┴───────────┐  │
│  │               akiba_odometry  paketi                       │  │
│  │   odometry_node · static_tf_publisher · waypoint_navigator │  │
│  └──────┬──────────────────────────────────────┬──────────────┘  │
└─────────┼──────────────────────────────────────┼────────────────┘
          │  Micro-ROS (Serial 115200)            │  USB
   ┌──────┴──────┐                        ┌──────┴──────┐
   │  STM32F407  │                        │ RPLIDAR S2  │
   │  PID Motor  │                        │  M1 (30 m)  │
   └──────┬──────┘                        └─────────────┘
          │
   ┌──────┴──────────────┐
   │  Sol Motor  │  Sağ  │   Differential Drive
   │  Enkoder    │ Motor │   139,941 tick/rev
   └─────────────┴───────┘
```

---

## TF Ağacı

Robotun koordinat çerçeveleri ve aralarındaki dönüşümler:

```
map
 └── odom                          (EKF → robot_localization)
      └── base_footprint           (odometry_node)
           └── base_link           (static_tf_publisher — sabit)
                └── laser_link     (static_tf_publisher — LIDAR ofseti)
                     x: +0.40 m (ileri)
                     y: +0.10 m (sol)
                     z: +0.40 m (yukarı)
```

| Transform | Yayıncı | Tip |
|-----------|---------|-----|
| `map → odom` | AMCL / SLAM Toolbox | Dinamik |
| `odom → base_footprint` | EKF (robot_localization) | Dinamik |
| `base_footprint → base_link` | odometry_node | Dinamik |
| `base_link → laser_link` | static_tf_publisher | Statik |

> TF ağacını canlı görmek için: `ros2 run tf2_tools view_frames`

---

## ROS2 Topic Haritası

```
STM32 (Micro-ROS)
  └─► /akiba_1/mps_info  ──► odometry_node ──► /odom
                                             └─► /tf  (base_footprint → base_link)

static_tf_publisher ──────────────────────────► /tf_static (base_link → laser_link)

RPLIDAR S2 M1 ────────────────────────────────► /scan

EKF (robot_localization)
  ├─ ◄── /odom
  └─────────────────────────────────────────► /odometry/filtered
                                             └─► /tf  (odom → base_footprint)

Navigation2 (AMCL + Planner + Controller)
  ├─ ◄── /scan
  ├─ ◄── /map
  ├─ ◄── /odometry/filtered
  └─────────────────────────────────────────► /akiba_1/cmd_vel
                                             └─► /plan, /local_plan

SLAM Toolbox
  ├─ ◄── /scan
  ├─ ◄── /tf
  └─────────────────────────────────────────► /map
                                             └─► /tf  (map → odom)

Teleop / Harici ──────────────────────────────► /akiba_1/cmd_vel
```

---

## Donanım

### Kontrolör
| Parametre | Değer |
|-----------|-------|
| MCU | STM32F407VGT6 |
| İşlemci | ARM Cortex-M4 @ 168 MHz |
| Micro-ROS | Serial `/dev/ttyACM1` @ 115200 baud |
| Motor PID | Kp=25.8, Ki=10.0, Kd=0.0, Ts=0.01 |

### Sensörler
| Sensör | Model | Bağlantı | Özellik |
|--------|-------|----------|---------|
| LIDAR | RPLIDAR S2 M1 | `/dev/ttyUSB0` @ 1 Mbaud | 30 m, 40k sample/s, 10 Hz |

### Mekanik
| Parametre | Değer |
|-----------|-------|
| Boyut | 86 × 46 × 55 cm |
| Tahrik | Diferansiyel sürüş |
| Tekerlek çapı | 11.1 cm (`wheel_diameter: 0.111`) |
| Dingil açıklığı | 30.5 cm (`wheel_base: 0.305`) |
| Encoder çözünürlüğü | 139,941 tick/rev |
| Ayak izi (footprint) | `[[0.43, 0.23], [0.43, -0.23], [-0.43, -0.23], [-0.43, 0.23]]` |

---

## Kurulum

### Bağımlılıklar

```bash
sudo apt install \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-localization \
  ros-humble-rplidar-ros \
  ros-humble-micro-ros-agent \
  ros-humble-teleop-twist-keyboard
```

### Build

```bash
cd ~/faal_ws
colcon build
source install/setup.bash
```

### Kalıcı Ortam Değişkeni

```bash
echo "export ROS_DOMAIN_ID=10" >> ~/.bashrc
echo "source ~/faal_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Port İzinleri

```bash
sudo usermod -a -G dialout $USER
# Sonra logout/login yapın
```

---

## Kullanım

### Senaryo 1 — Harita Çıkarma (SLAM)

```bash
~/start_akiba.sh
```

Açılan terminal pencerelerini bekle (~25 sn), ardından:

```bash
# Görselleştirme
rviz2
# Fixed Frame: map | Add: Map (/map), LaserScan (/scan)

# Manuel sürüş
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/akiba_1/cmd_vel

# Haritayı kaydet
ros2 run nav2_map_server map_saver_cli \
  -f ~/faal_ws/src/akiba_odometry/map/akiba_map
```

> **İpucu:** Yavaş git, kapalı döngü yap (başlangıç noktasına dön), köşelere yaklaş.

---

### Senaryo 2 — Otonom Navigasyon

```bash
~/start_navigation.sh
```

Ardından RViz'de:
1. **"2D Pose Estimate"** → robotun bulunduğu yere tıkla, yönünü çiz
2. **"Nav2 Goal"** → hedef noktaya tıkla, yönünü çiz

Robot otomatik yol planlar ve gider.

```bash
# Hedefi komut satırından göndermek için:
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5}, orientation: {w: 1.0}}}"
```

---

### Temel Komutlar

```bash
# STM32 Micro-ROS
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyACM1

# RPLIDAR
ros2 run rplidar_ros rplidar_node --ros-args \
  -p serial_port:=/dev/ttyUSB0 \
  -p serial_baudrate:=1000000 \
  -p frame_id:=laser_link \
  -p scan_mode:=Standard

# TF ağacı görüntüle
ros2 run tf2_tools view_frames

# Odometri izle
ros2 topic echo /odom

# EKF çıkışı izle
ros2 topic echo /odometry/filtered
```

---

## Konfigürasyon

### Temel Parametre Dosyaları

| Dosya | İçerik |
|-------|--------|
| `config/odometry_params.yaml` | Tekerlek çapı, dingil açıklığı, frame isimleri |
| `config/ekf_config.yaml` | EKF sensör ağırlıkları, kovaryanslar |
| `config/nav2_params.yaml` | AMCL, DWB, planner, controller parametreleri |
| `config/slam_toolbox_params.yaml` | SLAM async modu parametreleri |

### Navigasyon Performans Parametreleri

```yaml
# nav2_params.yaml — önemli değerler
max_vel_x: 0.3          # m/s (ileri maksimum hız)
max_vel_theta: 1.0      # rad/s (dönüş maksimum hız)
min_vel_x: -0.1         # geri gitme
inflation_radius: 0.70  # engel genişletme mesafesi (m)
min_particles: 500      # AMCL parçacık sayısı (min)
max_particles: 2000     # AMCL parçacık sayısı (max)
```

### LIDAR TF Ofseti Değiştirme

`akiba_odometry/static_tf_publisher.py` dosyasında:

```python
laser_tf.transform.translation.x = 0.40  # ileri/geri (m)
laser_tf.transform.translation.y = 0.10  # sol/sağ (m)
laser_tf.transform.translation.z = 0.40  # yukarı/aşağı (m)
```

---

## Sorun Giderme

### LIDAR başlamıyor
```bash
ls -l /dev/ttyUSB*
sudo chmod 666 /dev/ttyUSB0
```

### STM32 "Waiting for agent..." kalıyor
```bash
ls -l /dev/ttyACM*
sudo chmod 666 /dev/ttyACM1
```

### TF hatası — "frame 'laser_link' does not exist"
```bash
ros2 node list | grep static_tf        # publisher çalışıyor mu?
ros2 run akiba_odometry static_tf_publisher   # elle başlat
```

### SLAM harita oluşmuyor
```bash
ros2 run tf2_ros tf2_echo base_link laser_link  # TF geliyor mu?
ros2 topic hz /scan                              # LIDAR yayın yapıyor mu?
```

### AMCL lokalize olmuyor
1. RViz'de **"2D Pose Estimate"** ile ilk pozisyonu ver
2. Robotu biraz hareket ettir (parçacık filtresi yakınsasın)
3. `ros2 topic echo /amcl_pose` ile kovaryansın düştüğünü doğrula

---

## Proje Yapısı

```
faal_ws/
├── src/
│   └── akiba_odometry/
│       ├── akiba_odometry/
│       │   ├── odometry_node.py          # Enkoder → /odom
│       │   ├── static_tf_publisher.py    # base_link → laser_link TF
│       │   └── waypoint_navigator.py     # Nav2 action client, 4 waypoint
│       ├── config/
│       │   ├── nav2_params.yaml          # AMCL, DWB, planner
│       │   ├── ekf_config.yaml           # EKF sensör füzyonu
│       │   ├── odometry_params.yaml      # Tekerlek kalibrasyon
│       │   └── slam_toolbox_params.yaml  # SLAM async modu
│       ├── launch/
│       │   ├── akiba_full.launch.py      # Odometry + EKF + TF
│       │   ├── akiba_odometry.launch.py  # Sadece odometri
│       │   ├── navigation.launch.py      # Nav2 tam stack
│       │   ├── slam.launch.py            # SLAM Toolbox
│       │   └── ekf.launch.py             # Sadece EKF
│       └── map/
│           ├── my_map.pgm / .yaml        # Kayıtlı haritalar
│           └── my1_map.pgm / .yaml
├── start_akiba.sh                        # SLAM modu başlatıcı
├── start_navigation.sh                   # Navigasyon modu başlatıcı
└── README.md
```

---

## Bağlantılar

- **AGV-GOREVLER** (görev yürütme katmanı): [github.com/aSelim-Ilhan/AGV-GOREVLER](https://github.com/aSelim-Ilhan/AGV-GOREVLER)
- ROS2 Humble: https://docs.ros.org/en/humble/
- Navigation2: https://navigation.ros.org/
- SLAM Toolbox: https://github.com/SteveMacenski/slam_toolbox
- Micro-ROS: https://micro.ros.org/

---

**Geliştirici:** Ahmet Selim İlhan — **Takım:** FAAL — **Yarışma:** Sanayide Dijital 2026
