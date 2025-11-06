# vio_zed_camera.launch.py
# เรียก zed_camera.launch.py + remap odom & imu + depth_to_scan

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    robot_name = "recon_bot"
    package_description = f"{robot_name}_description"

    zed_launch_path = os.path.join(
        get_package_share_directory('zed_wrapper'),
        'launch',
        'zed_camera.launch.py'
    )

    ekf_config_path = os.path.join(
        get_package_share_directory(package_description), 
        'config', 
        'rviz',
        'recon_rviz_config.rviz'
    )

    # URDF ของคุณ
    # urdf_path = os.path.join(
    #     get_package_share_directory('zed_wrapper'),
    #     'urdf',
    #     'zed_camera.urdf.xacro'
    # )

    # Override params
    vio_params_path = os.path.join(
        get_package_share_directory('zed_wrapper'),
        'config',
        'zed_vio_params.yaml'
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        output={"stdout": "screen", "stderr": "log"}
    )

    return LaunchDescription([
        # === ZED Camera (เรียกไฟล์ต้นฉบับ) ===
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(zed_launch_path),
            launch_arguments={
                'camera_model': 'zed2',
                'camera_name': 'zed',
                'node_name': 'zed_node',

                # URDF
                # 'publish_urdf': 'false',  # ปิด เพราะ URDF มี
                # 'xacro_path': urdf_path,

                # TF
                # 'publish_tf': 'false',  # ปิด เพราะ URDF มี
                # 'publish_imu_tf': 'false',  # ปิด เพราะ URDF มี

                # Override
                'ros_params_override_path': vio_params_path,
            }.items()
        ),

        # # === REMAP odom และ imu (สำคัญมาก!) ===
        # # วิธีนี้: ใช้ Node เปล่า + remappings
        # Node(
        #     package='topic_tools',
        #     executable='relay',
        #     name='odom_relay',
        #     output='screen',
        #     arguments=['/zed/zed_node/odom', '/camera_odom']  # input output
        # ),

        # Node(
        #     package='topic_tools',
        #     executable='relay',
        #     name='imu_relay',
        #     output='screen',
        #     arguments=['/zed/zed_node/imu/data', '/imu/data']
        # ),

        # === Depth to LaserScan ===
        Node(
            package='depthimage_to_laserscan',
            executable='depthimage_to_laserscan_node',
            name='depth_to_scan',
            parameters=[{
                'scan_time': 0.0333,
                'range_min': 0.3,
                'range_max': 20.0,
                'output_frame_id': 'zed_camera_link'
            }],
            remappings=[
                ('image', '/zed/zed_node/depth/depth_registered'),
                ('camera_info', '/zed/zed_node/depth/camera_info'),
                ('scan', '/scan')
            ]
        ),
    ])