#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate bilingual (ZH/KO) exam review bank HTML."""
import json, html, textwrap

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_bank.html")

# Each SC: (week, zh_stem, ko_stem, options_zh, options_ko, answer, explain_zh, explain_ko)
# options: list of 4 strings without letter prefix

SC = [
(2,"ROS2 中查看所有运行中节点的命令是？","ROS2에서 실행 중인 모든 노드를 보는 명령은?",
 ["ros2 node list","ros2 topic list","ros2 pkg list","ros2 service list"],
 ["ros2 node list","ros2 topic list","ros2 pkg list","ros2 service list"],"A",
 "ros2 node list 列出节点。","ros2 node list가 노드 목록을 출력합니다."),
(2,"运行 turtlesim 节点的正确命令是？","turtlesim 노드를 실행하는 올바른 명령은?",
 ["ros2 run turtlesim turtlesim_node","ros2 launch turtlesim","ros2 node turtlesim","ros2 pkg turtlesim"],
 ["ros2 run turtlesim turtlesim_node","ros2 launch turtlesim","ros2 node turtlesim","ros2 pkg turtlesim"],"A",
 "标准格式 ros2 run <包> <节点>。","표준 형식은 ros2 run <패키지> <노드>입니다."),
(2,"发布/订阅模型中，数据通过什么传递？","Pub/Sub 모델에서 데이터는 무엇으로 전달되나요?",
 ["话题 Topic","服务 Service","参数 Parameter","动作 Action"],
 ["토픽 Topic","서비스 Service","파라미터 Parameter","액션 Action"],"A",
 "话题是异步连续数据流。","토픽은 비동기 연속 데이터 스트림입니다."),
(2,"查看某话题发布频率可用？","특정 토픽의 발행 주기를 확인하려면?",
 ["ros2 topic hz /topic","ros2 topic echo /topic","ros2 topic info /topic","ros2 bag play"],
 ["ros2 topic hz /topic","ros2 topic echo /topic","ros2 topic info /topic","ros2 bag play"],"A",
 "hz 显示频率。","hz로 주기를 확인합니다."),
(2,"colcon build 的作用主要是？","colcon build의 주된 역할은?",
 ["编译工作空间中的包","安装 Python","启动节点","录制 bag"],
 ["워크스페이스 패키지 빌드","Python 설치","노드 실행","bag 녹화"],"A",
 "ROS2 工作空间编译工具。","ROS2 워크스페이스 빌드 도구입니다."),
(2,"ros2 topic echo 的作用是？","ros2 topic echo의 역할은?",
 ["实时打印话题消息内容","列出所有话题","删除话题","修改话题类型"],
 ["토픽 메시지를 실시간 출력","모든 토픽 나열","토픽 삭제","토픽 타입 변경"],"A",
 "echo 用于调试查看消息。","디버깅용 메시지 출력입니다."),
(2,"节点 Node 在 ROS2 中代表？","ROS2에서 노드(Node)는?",
 ["一个独立执行计算的进程","一个话题名","一个镜像","一个 launch 文件"],
 ["독립적으로 계산을 수행하는 프로세스","토픽 이름","이미지","launch 파일"],"A",
 "节点是功能单元。","기능 단위 프로세스입니다."),
(2,"工作空间 src 目录通常放？","워크스페이스 src 폴더에는 보통?",
 ["源代码包","编译产物","日志","Docker 镜像"],
 ["소스 코드 패키지","빌드 산출물","로그","Docker 이미지"],"A",
 "src 放自定义包。","사용자 패키지를 둡니다."),
(3,"Python 中 f-string 的正确写法是？","Python f-string 올바른 예는?",
 ['f"速度:{v}"','"速度:{v}".format()','f(v)','format(f,v)'],
 ['f"속도:{v}"','"속도:{v}".format()','f(v)','format(f,v)'],"A",
 "f\"...{变量}...\" 。","f\"...{변수}...\" 형식입니다."),
(3,"ROS2 Python 节点中 spin() 的作用是？","ROS2 Python 노드에서 spin()의 역할은?",
 ["保持节点运行并处理回调","编译包","发布镜像","关闭话题"],
 ["노드를 유지하며 콜백 처리","패키지 빌드","이미지 발행","토픽 종료"],"A",
 "spin 进入事件循环。","이벤트 루프에 진입합니다."),
(3,"geometry_msgs/Twist 中 linear.x 通常表示？","geometry_msgs/Twist의 linear.x는 보통?",
 ["前进线速度","角速度","高度","横向力"],
 ["전진 선속도","각속도","높이","횡방향 힘"],"A",
 "x 方向线速度。","x축 선속도입니다."),
(3,"创建 Publisher 时需要指定？","Publisher 생성 시 지정해야 하는 것은?",
 ["话题名和消息类型","仅节点名","仅端口号","仅 IP"],
 ["토픽 이름과 메시지 타입","노드 이름만","포트만","IP만"],"A",
 "类型与话题名必须匹配。","타입과 토픽명이 일치해야 합니다."),
(3,"Python 列表 append 的作用是？","Python 리스트 append()는?",
 ["在末尾添加元素","删除元素","排序","反转"],
 ["끝에 요소 추가","요소 삭제","정렬","역순"],"A",
 "append 追加一项。","끝에 항목을 추가합니다."),
(3,"import rclpy 的目的是？","import rclpy의 목적은?",
 ["使用 ROS2 Python 客户端库","安装 Docker","打开相机","编译 C++"],
 ["ROS2 Python 클라이언트 사용","Docker 설치","카메라 열기","C++ 빌드"],"A",
 "rclpy 是 ROS2 Python API。","ROS2 Python API입니다."),
(3,"定时器 Timer 常用于？","타이머(Timer)는 주로?",
 ["周期发布控制命令","删除节点","挂载卷","SSH 登录"],
 ["주기적으로 제어 명령 발행","노드 삭제","볼륨 마운트","SSH 로그인"],"A",
 "周期回调发布 cmd_vel。","주기 콜백으로 cmd_vel 발행합니다."),
(3,"走正方形通常需要交替改变？","정사각형 주행은 보통 무엇을 번갈아 바꾸나요?",
 ["线速度与角速度","仅颜色","仅镜像名","仅域名"],
 ["선속도와 각속도","색상만","이미지 이름만","도메인만"],"A",
 "直行+转弯组合。","직진+회전 조합입니다."),
(4,"里程计 Odom 提供的信息主要是？","오도메트리(Odom)가 주로 주는 정보는?",
 ["机器人估计的位姿","激光点云","网页 HTML","镜像分层"],
 ["로봇 추정 자세","라이다 포인트클라우드","HTML","이미지 레이어"],"A",
 "位姿估计，会漂移。","자세 추정이며 드리프트가 있습니다."),
(4,"世界坐标系 World Frame 的特点是？","월드 좌표계(World Frame)의 특징은?",
 ["固定不变，作为全局参考","随机器人移动","只用于相机","只用于 Docker"],
 ["고정된 전역 기준","로봇과 함께 이동","카메라 전용","Docker 전용"],"A",
 "世界系固定。","월드 좌표계는 고정입니다."),
(4,"二维位姿通常用几个量表示？","2D 자세는 보통 몇 개로 표현하나요?",
 ["x, y, θ","x, y, z, roll, pitch, yaw","仅 r, g, b","仅 vx, vy"],
 ["x, y, θ","x, y, z, roll, pitch, yaw","r, g, b만","vx, vy만"],"A",
 "平面三自由度。","평면 3자유도입니다."),
(4,"机器人坐标系原点多放在？","로봇 좌표계 원점은 보통 어디에 두나요?",
 ["机器人底盘中心","世界原点","相机光心","显示器左上角"],
 ["로봇 베이스 중심","월드 원점","카메라 광심","화면 좌상단"],"A",
 "机体系描述自身运动。","기체 좌표계 기준입니다."),
(4,"turtlesim 中 /turtle1/pose 包含？","turtlesim /turtle1/pose에는?",
 ["位置和朝向","激光距离","镜像 ID","网页端口"],
 ["위치와 방향","라이다 거리","이미지 ID","웹 포트"],"A",
 "Pose 消息含 x,y,theta。","x,y,theta 포함합니다."),
(4,"积分速度得到位置的过程叫？","속도를 적분해 위치를 구하는 과정은?",
 ["里程计推算","卷积","标定","镜像提交"],
 ["오도메트리 적분","컨볼루션","캘리브레이션","docker commit"],"A",
 "速度积分得位姿。","속도 적분으로 자세 추정합니다."),
(4,"在平面运动中，角速度单位常用？","평면 운동에서 각속도 단위는 보통?",
 ["rad/s","像素","米","千克"],
 ["rad/s","픽셀","미터","킬로그램"],"A",
 "弧度每秒。","라디안/초입니다."),
(5,"激光雷达 LiDAR 主要测量？","라이다(LiDAR)는 주로 무엇을 측정하나요?",
 ["距离/深度","颜色","声音","网页流量"],
 ["거리/깊이","색상","소리","웹 트래픽"],"A",
 "ToF 或三角测距。","거리 측정 센서입니다."),
(5,"相机图像在 ROS2 中常见消息类型？","ROS2에서 카메라 이미지 메시지는 보통?",
 ["sensor_msgs/Image","geometry_msgs/Twist","std_msgs/String","nav_msgs/OccupancyGrid"],
 ["sensor_msgs/Image","geometry_msgs/Twist","std_msgs/String","nav_msgs/OccupancyGrid"],"A",
 "Image 消息存像素。","Image 메시지에 픽셀 저장합니다."),
(5,"RViz 的主要用途是？","RViz의 주 용도는?",
 ["三维可视化机器人数据","编译代码","写网页","SSH 隧道"],
 ["로봇 데이터 3D 시각화","코드 빌드","웹 작성","SSH 터널"],"A",
 "可视化工具。","시각화 도구입니다."),
(5,"激光雷达扫描数据常发布在？","라이다 스캔 데이터는 보통 어디에 발행되나요?",
 ["/scan 或 PointCloud 话题","/cmd_vel","/docker","/pages"],
 ["/scan 또는 PointCloud 토픽","/cmd_vel","/docker","/pages"],"A",
 "scan 为 2D，点云为 3D。","2D는 scan, 3D는 포인트클라우드입니다."),
(5,"IMU 可测量？","IMU는 무엇을 측정할 수 있나요?",
 ["加速度和角速度","仅距离","仅颜色","仅 HTML"],
 ["가속도와 각속도","거리만","색상만","HTML만"],"A",
 "惯性测量单元。","관성 측정 장치입니다."),
(5,"在 RViz 中添加 Image 显示需要？","RViz에 Image 표시를 추가하려면?",
 ["订阅图像话题","删除节点","停止 Docker","关闭 Pages"],
 ["이미지 토픽 구독","노드 삭제","Docker 중지","Pages 종료"],"A",
 "选择 Image 并设 Topic。","Image 디스플레이와 토픽 설정이 필요합니다."),
(5,"传感器融合指？","센서 퓨전이란?",
 ["组合多种传感器信息","只用一个传感器","删除激光","只写 README"],
 ["여러 센서 정보 결합","센서 하나만 사용","라이다 삭제","README만 작성"],"A",
 "多源互补。","다중 센서 상보입니다."),
(6,"开环控制的特点是？","개루프 제어의 특징은?",
 ["无反馈，输出不根据结果调整","有传感器反馈","一定最优","等于 PID"],
 ["피드백 없음","센서 피드백 있음","항상 최적","PID와 동일"],"A",
 "开环不修正误差。","결과에 따라 보정하지 않습니다."),
(6,"闭环控制需要？","폐루프 제어에는 무엇이 필요하나요?",
 ["传感器反馈","仅开环命令","仅镜像","仅 Markdown"],
 ["센서 피드백","개루프 명령만","이미지만","Markdown만"],"A",
 "反馈形成回路。","피드백 루프가 필요합니다."),
(6,"PID 中 P 项主要作用？","PID에서 P항의 주 역할은?",
 ["按当前误差比例调节","消除稳态误差","抑制超调","记录日志"],
 ["현재 오차에 비례 조절","정상상태 오차 제거","오버슈트 억제","로그 기록"],"A",
 "比例项响应快。","비례 제어로 빠른 응답입니다."),
(6,"简单避障：前方太近应？","단순 장애물 회피: 전방이 너무 가까우면?",
 ["减速并转向","加速直行","关闭节点","删除镜像"],
 ["감속 후 회전","가속 직진","노드 종료","이미지 삭제"],"A",
 "停/转避开障碍。","정지/회전으로 회피합니다."),
(6,"订阅 /scan 是为了？","/scan을 구독하는 이유는?",
 ["获取激光距离用于避障","发布速度","构建网页","拉取镜像"],
 ["라이다 거리로 회피","속도 발행","웹 구축","이미지 pull"],"A",
 "读取障碍物距离。","장애물 거리 획득입니다."),
(6,"PID 中 D 项有助于？","PID에서 D항은 무엇에 도움이 되나요?",
 ["抑制振荡/超调","增大稳态误差","替代传感器","生成 HTML"],
 ["진동/오버슈트 억제","정상상태 오차 증가","센서 대체","HTML 생성"],"A",
 "微分预测变化趋势。","미분으로 변화 추세 예측합니다."),
(6,"撞墙后仅原地转圈属于？","벽에 부딪힌 뒤 제자리만 도는 것은?",
 ["简单反应策略，可能陷入循环","最优 A*","已完成标定","Docker 分层"],
 ["단순 반응, 루프 가능","최적 A*","캘리브 완료","Docker 레이어"],"A",
 "需更智能策略。","더 나은 탐색 알고리즘이 필요합니다."),
(7,"Markdown 中一级标题语法是？","Markdown 1단계 제목 문법은?",
 ["# 标题","## 标题","**标题**","`标题`"],
 ["# 제목","## 제목","**제목**","`제목`"],"A",
 "# 后空格。","# 뒤 공백입니다."),
(7,"在 GitHub 显示图片的正确写法？","GitHub에서 이미지 표시는?",
 ["![说明](路径)","<img>","{图片}","#图片"],
 ["![설명](경로)","<img>","{이미지}","#이미지"],"A",
 "相对路径引用仓库内图片。","상대 경로로 저장소 이미지 참조합니다."),
(7,"GitHub Pages 默认从哪个分支发布？","GitHub Pages 기본 배포 브랜치는?",
 ["main 或 gh-pages（依设置）","仅 dev","仅 docker","无分支"],
 ["main 또는 gh-pages(설정에 따름)","dev만","docker만","브랜치 없음"],"A",
 "在 Settings→Pages 配置。","Settings→Pages에서 설정합니다."),
(7,"作业仓库 README 的作用是？","과제 README의 역할은?",
 ["介绍项目与导航","编译 ROS","替代 launch","删除容器"],
 ["프로젝트 소개와 내비게이션","ROS 빌드","launch 대체","컨테이너 삭제"],"A",
 "首页说明与目录。","홈 설명과 목차입니다."),
(7,"相对路径 ./week2/ 表示？","상대 경로 ./week2/는?",
 ["当前目录下的 week2 文件夹","上级目录","绝对路径 /","Docker 卷"],
 ["현재 폴더의 week2","상위 폴더","절대경로 /","Docker 볼륨"],"A",
 "./ 表示当前目录。","./는 현재 디렉터리입니다."),
(8,"Docker 镜像 Image 的特点是？","Docker 이미지(Image)의 특징은?",
 ["只读模板，分层存储","运行中的进程","等同容器可写层","等同 tailscale"],
 ["읽기 전용 템플릿, 레이어","실행 프로세스","컨테이너 쓰기층","tailscale"],"A",
 "镜像只读，容器可写。","이미지는 읽기 전용입니다."),
(8,"docker run 创建的是？","docker run이 만드는 것은?",
 ["容器 Container","新镜像（默认）","新分支","新话题"],
 ["컨테이너 Container","새 이미지(기본)","새 브랜치","새 토픽"],"A",
 "run 启动容器实例。","컨테이너 인스턴스를 시작합니다."),
(8,"查看运行中容器用？","실행 중 컨테이너 확인은?",
 ["docker ps","docker images","git status","ros2 node list"],
 ["docker ps","docker images","git status","ros2 node list"],"A",
 "ps 列运行中。","ps로 실행 중 목록을 봅니다."),
(8,"-p 6080:6080 表示？","-p 6080:6080의 의미는?",
 ["宿主机端口映射到容器端口","删除端口","关闭网络","挂载目录"],
 ["호스트↔컨테이너 포트 매핑","포트 삭제","네트워크 차단","디렉터리 마운트"],"A",
 "端口转发访问 noVNC 等。","noVNC 등 접속용 포트 포워딩입니다."),
(8,"-v 宿主机:容器 用于？","-v 호스트:컨테이너는?",
 ["目录挂载，共享文件","删除数据","仅显示日志","编译包"],
 ["디렉터리 마운트, 파일 공유","데이터 삭제","로그만 표시","패키지 빌드"],"A",
 "卷挂载持久化/共享代码。","볼륨 마운트로 코드 공유합니다."),
(8,"docker commit 的作用是？","docker commit의 역할은?",
 ["把容器当前状态保存为新镜像","删除容器","拉取镜像","启动 turtlesim"],
 ["컨테이너 상태를 새 이미지로 저장","컨테이너 삭제","이미지 pull","turtlesim 실행"],"A",
 "保存环境改动。","환경 변경을 이미지로 저장합니다."),
(8,"在 Docker 里运行 ROS2 桌面环境主要为了？","Docker에서 ROS2 데스크톱을 쓰는 주된 이유는?",
 ["统一环境、减少安装差异","替代 Git","替代 Markdown","关闭网络"],
 ["환경 통일, 설치 차이 감소","Git 대체","Markdown 대체","네트워크 차단"],"A",
 "一键复现课堂环境。","수업 환경을 일관되게 재현합니다."),
(10,"Docker 镜像类比面向对象中的？","Docker 이미지는 객체지향에서 무엇에 가깝나요?",
 ["类 Class","实例 Instance","函数","变量"],
 ["클래스 Class","인스턴스 Instance","함수","변수"],"A",
 "镜像是模板，容器是实例。","이미지=템플릿, 컨테이너=인스턴스입니다."),
(10,"OpenCV 读图函数是？","OpenCV에서 이미지 읽기 함수는?",
 ["cv2.imread","cv2.imshow","cv2.waitKey","cv2.destroyAllWindows"],
 ["cv2.imread","cv2.imshow","cv2.waitKey","cv2.destroyAllWindows"],"A",
 "imread 读入，imshow 显示。","imread로 읽고 imshow로 표시합니다."),
(10,"彩色图像在 OpenCV 默认通道顺序？","OpenCV 컬러 이미지 기본 채널 순서는?",
 ["BGR","RGB","HSV","灰度"],
 ["BGR","RGB","HSV","그레이"],"A",
 "与 matplotlib RGB 不同需注意。","matplotlib RGB와 다릅니다."),
(10,"cv2.cvtColor 用于？","cv2.cvtColor는?",
 ["颜色空间转换","矩阵乘法","路径规划","SSH"],
 ["색공간 변환","행렬 곱","경로 계획","SSH"],"A",
 "如 BGR→灰度/HSV。","BGR→그레이/HSV 등 변환입니다."),
(10,"docker pull 的作用是？","docker pull의 역할은?",
 ["从仓库下载镜像","删除镜像","进入容器 shell","发布网页"],
 ["레지스트리에서 이미지 다운","이미지 삭제","컨테이너 셸","웹 배포"],"A",
 "拉取远程镜像。","원격 이미지를 받습니다."),
(10,"容器文件系统可写层在？","컨테이너의 쓰기 가능한 층은?",
 ["容器层（运行于镜像之上）","镜像只读层","Git 分支","ROS bag"],
 ["컨테이너 쓰기층(이미지 위)","이미지 읽기층","Git 브랜치","ROS bag"],"A",
 "容器在镜像上加可写层。","이미지 위에 쓰기층이 있습니다."),
(10,"OpenCV 显示图像后常用？","OpenCV 이미지 표시 후 보통?",
 ["cv2.waitKey(0)","docker stop","git push","colcon build"],
 ["cv2.waitKey(0)","docker stop","git push","colcon build"],"A",
 "waitKey 等待按键。","키 입력 대기입니다."),
(10,"docker build 需要？","docker build에 필요한 것은?",
 ["Dockerfile","仅 README","仅 _config.yml","仅 bag"],
 ["Dockerfile","README만","_config.yml만","bag만"],"A",
 "Dockerfile 定义构建步骤。","Dockerfile로 빌드 단계를 정의합니다."),
(11,"获取容器 ID 可用？","컨테이너 ID 확인은?",
 ["docker ps","docker pull","git clone","ros2 run"],
 ["docker ps","docker pull","git clone","ros2 run"],"A",
 "ps 第一列 CONTAINER ID。","ps의 CONTAINER ID 열입니다."),
(11,"停止容器用？","컨테이너 중지는?",
 ["docker stop <ID>","docker run","docker build","docker push"],
 ["docker stop <ID>","docker run","docker build","docker push"],"A",
 "stop 优雅停止。","stop으로 정상 종료합니다."),
(11,"GitHub Pages 网站 URL 通常形如？","GitHub Pages URL 형식은 보통?",
 ["用户名.github.io/仓库名","localhost:8080","100.x.tailscale","仅 IP"],
 ["사용자명.github.io/저장소","localhost:8080","100.x.tailscale","IP만"],"A",
 "user.github.io/repo。","user.github.io/repo 형태입니다."),
(11,"Jekyll 网站配置常写在？","Jekyll 설정 파일은 보통?",
 ["_config.yml","Dockerfile","package.xml","CMakeLists.txt"],
 ["_config.yml","Dockerfile","package.xml","CMakeLists.txt"],"A",
 "Pages 主题与站点元数据。","Pages 테마와 사이트 메타데이터입니다."),
(11,"作业截图应使用？","과제 스크린샷은?",
 ["相对路径放入仓库并 Markdown 引用","外链仅依赖第三方","不写进仓库","只用纯文本"],
 ["저장소 상대경로+Markdown","외부 링크만","저장소에 없음","텍스트만"],"A",
 "保证长期可访问。","장기 접근 가능하게 합니다."),
(11,"docker exec -it 用于？","docker exec -it는?",
 ["进入运行中容器执行命令","删除镜像","编译 ROS","发布话题"],
 ["실행 중 컨테이너에서 명령","이미지 삭제","ROS 빌드","토픽 발행"],"A",
 "交互式进入容器 shell。","컨테이너 셸에 진입합니다."),
(11,"保存容器为新镜像可避免？","컨테이너를 이미지로 저장하면 피할 수 있는 것은?",
 ["重复手动安装依赖","所有编译错误","所有网络问题","所有数学推导"],
 ["의존성 재설치 반복","모든 빌드 오류","모든 네트워크 문제","모든 수식"],"A",
 "commit 固化环境。","commit으로 환경을 고정합니다."),
(11,"README 中返回上级目录链接可写？","README 상위 목록 링크 예는?",
 ["[返回](../README.md)","docker ps","ros2 run","#仅标题"],
 ["[돌아가기](../README.md)","docker ps","ros2 run","#제목만"],"A",
 "相对链接导航。","상대 링크 내비게이션입니다."),
(12,"Tailscale 给设备分配的典型地址段？","Tailscale이 주는 주소 대역은 보통?",
 ["100.x.x.x 虚拟局域网","127.0.0.1 仅本机","公网随机","仅 IPv6本地"],
 ["100.x.x.x 가상 LAN","127.0.0.1 로컬만","공인 IP 랜덤","IPv6 로컬만"],"A",
 "组建虚拟专网。","가상 사설망을 구성합니다."),
(12,"手机访问 WSL 服务困难常见原因？","휴대폰이 WSL 서비스 접속이 어려운 흔한 이유는?",
 ["AP 隔离与 NAT","缺少 Markdown","没有激光","没有镜像"],
 ["AP 격리와 NAT","Markdown 부족","라이다 없음","이미지 없음"],"A",
 "校园网隔离+WSL NAT。","캠퍼스 AP 격리+WSL NAT입니다."),
(12,"ArUco 码主要用于？","ArUco 마커는 주로?",
 ["机器人视觉定位与识别","音频处理","编译 C++","写网页主题"],
 ["로봇 비전 위치/식별","오디오 처리","C++ 빌드","웹 테마"],"A",
 "已知尺寸的方形标记。","알려진 크기의 사각 마커입니다."),
(12,"OpenCV detectMarkers 输出包含？","detectMarkers 출력에는?",
 ["角点与 ID","仅角速度","仅线速度","Docker ID"],
 ["코너와 ID","각속도만","선속도만","Docker ID"],"A",
 "检测到的标记编号与顶点。","마커 ID와 꼭짓점입니다."),
(12,"相机标定主要求解？","카메라 캘리브레이션은 주로?",
 ["内参和畸变参数","ROS 节点名","Git 分支","容器端口"],
 ["내부 파라미터와 왜곡","ROS 노드명","Git 브랜치","컨테이너 포트"],"A",
 "焦距、主点、畸变系数等。","초점, 주점, 왜곡 계수 등입니다."),
(12,"棋盘格标定需要？","체스보드 캘리브레이션에 필요한 것은?",
 ["多张不同姿态的棋盘格图片","仅一张 selfie","仅 Dockerfile","仅 bag"],
 ["여러 자세의 체스보드 사진","셀피 한 장","Dockerfile만","bag만"],"A",
 "多角度采集提高精度。","다양한 각도로 촬영합니다."),
(12,"距离测量若已知 ArUco 实际边长，可用？","ArUco 실제 변 길이를 알면 거리 측정에?",
 ["相似三角形/投影几何","仅 PID","仅 BFS","仅 docker pull"],
 ["유사삼각형/투영 기하","PID만","BFS만","docker pull만"],"A",
 "像素尺寸与真实尺寸比例。","픽셀-실제 크기 비율로 추정합니다."),
(12,"HTML5 getUserMedia 用于？","HTML5 getUserMedia는?",
 ["浏览器获取摄像头视频流","编译 ROS","拉取镜像","写 YAML"],
 ["브라우저 카메라 스트림","ROS 빌드","이미지 pull","YAML 작성"],"A",
 "手机浏览器采集视频。","모바일 브라우저 영상 획득입니다."),
(13,"PyBullet 常用于？","PyBullet은 주로?",
 ["物理仿真与机器人动力学","仅写网页","仅 Git Pages","仅 SSH"],
 ["물리 시뮬레이션/동역학","웹만","Git Pages만","SSH만"],"A",
 "四足/机械臂仿真。","사족/매니퓰레이터 시뮬입니다."),
(13,"四足机器人每条腿通常视为？","사족 로봇 각 다리는 보통?",
 ["一个串联关节链","一个激光","一个镜像","一个 HTML"],
 ["연결 관절 체인","라이다 하나","이미지 하나","HTML 하나"],"A",
 "多关节腿机构。","다관절 다리 기구입니다."),
(13,"强化学习训练四足时，奖励函数用于？","사족 RL에서 보상 함수는?",
 ["引导策略朝期望行为优化","删除模型","关闭 Docker","发布 /scan"],
 ["원하는 행동으로 정책 유도","모델 삭제","Docker 종료","/scan 발행"],"A",
 "奖励塑造学习目标。","학습 목표를 형성합니다."),
(13,"仿真中 reset 的作用是？","시뮬레이션 reset은?",
 ["将环境恢复到初始状态","永久删除机器人","提交镜像","发布网页"],
 ["환경을 초기 상태로","로봇 영구 삭제","이미지 commit","웹 배포"],"A",
 "每回合重新开始。","에피소드를 다시 시작합니다."),
(13,"相机在机器人视觉管线中提供？","로봇 비전에서 카메라는?",
 ["原始感知输入","仅控制命令","仅编译","仅域名"],
 ["원시 감지 입력","제어 명령만","빌드만","도메인만"],"A",
 "视觉传感器输入。","비전 센서 입력입니다."),
(13,"期末项目强调的工程原则是？","기말 프로젝트가 강조하는 원칙은?",
 ["一条链路一个常驻程序","每功能一个浏览器","每命令一个容器","每学生一个镜像"],
 ["한 링크=한 상주 프로그램","기능마다 브라우저","명령마다 컨테이너","학생마다 이미지"],"A",
 "桥接程序统一收发与控制。","브리지가 수신+제어를 담당합니다."),
(13,"WebSocket 相比普通 HTTP 更适合？","WebSocket이 일반 HTTP보다 적합한 것은?",
 ["实时双向通信","一次性静态页面","仅下载镜像","仅编译"],
 ["실시간 양방향 통신","정적 페이지 1회","이미지 다운로드만","빌드만"],"A",
 "遥控需要低延迟双向。","원격 조종에 양방향 저지연이 필요합니다."),
]

assert len(SC) == 80, len(SC)

MC = [
(2,["下列属于 ROS2 命令的有？","ROS2 명령에 해당하는 것은?"],
 ["ros2 topic list","ros2 node info","git commit","docker ps"],["A","B"],
 "节点与话题管理属 ROS2。","노드/토픽 관리는 ROS2입니다."),
(3,["编写 ROS2 Python 发布者需要？","ROS2 Python Publisher 작성에 필요한 것은?"],
 ["import rclpy","create_publisher","cv2.imread","docker run"],["A","B"],
 "rclpy 与 create_publisher。","rclpy와 create_publisher입니다."),
(4,["描述机器人位姿常用的量有？","로봇 자세를 나타내는 것은?"],
 ["x, y","θ (yaw)","像素 R,G,B","镜像 ID"],["A","B"],
 "平面位姿 x,y,θ。","평면 자세 x,y,θ입니다."),
(5,["常见机器人传感器包括？","흔한 로봇 센서는?"],
 ["激光雷达","相机","仅 Markdown","仅 HTML"],["A","B"],
 "感知传感器。","지각 센서입니다."),
(6,["闭环控制回路包含？","폐루프에 포함되는 것은?"],
 ["传感器测量","控制器计算","仅 docker pull","仅 git push"],["A","B"],
 "测量-计算-执行-反馈。","측정-계산-실행-피드백입니다."),
(6,["PID 三项包括？","PID 세 항은?"],
 ["比例 P","积分 I","仅 D 单独","仅镜像层"],["A","B"],
 "P/I/D 三项。","P/I/D입니다."),
(8,["Docker 核心概念包括？","Docker 핵심 개념은?"],
 ["Image 镜像","Container 容器","仅 Topic","仅 Node"],["A","B"],
 "镜像与容器。","이미지와 컨테이너입니다."),
(8,["docker run 常用参数有？","docker run 자주 쓰는 옵션은?"],
 ["-p 端口映射","-v 卷挂载","-spin","-colcon"],["A","B"],
 "端口与卷。","포트와 볼륨입니다."),
(10,["OpenCV 基础操作包括？","OpenCV 기본 작업은?"],
 ["imread 读图","imshow 显示","git clone","ros2 bag"],["A","B"],
 "读写显示。","읽기/표시입니다."),
(10,["容器与镜像关系正确的是？","컨테이너-이미지 관계로 맞는 것은?"],
 ["镜像是只读模板","容器是运行实例","容器等于只读模板","镜像等于运行进程"],["A","B"],
 "类-实例关系。","템플릿-인스턴스 관계입니다."),
(11,["GitHub Pages 部署需要？","GitHub Pages 배포에 필요한 것은?"],
 ["仓库开启 Pages","有 index/README 入口","仅 Dockerfile","仅激光"],["A","B"],
 "开启 Pages 并有入口页。","Pages 활성화와 진입 페이지입니다."),
(11,["Docker 环境固化可用？","Docker 환경 고정 방법은?"],
 ["docker commit","编写 Dockerfile 重建","仅 git amend","仅 echo"],["A","B"],
 "commit 或 Dockerfile。","commit 또는 Dockerfile입니다."),
(12,["ArUco 检测需要？","ArUco 검출에 필요한 것은?"],
 ["相机图像","已知字典/标记尺寸","仅 SSH 密码","仅 bag"],["A","B"],
 "图像与字典参数。","이미지와 딕셔너리 파라미터입니다."),
(12,["Tailscale 适用场景包括？","Tailscale 활용 사례는?"],
 ["手机访问 WSL 服务","跨 NAT 组网","替代 colcon","替代 Markdown"],["A","B"],
 "穿透隔离组网。","NAT/격리 환경 연결입니다."),
(13,["PyBullet 仿真可获取？","PyBullet 시뮬에서 얻을 수 있는 것은?"],
 ["关节角度","接触/碰撞信息","仅网页 CSS","仅域名"],["A","B"],
 "状态与接触。","상태와 접촉 정보입니다."),
(13,["期末项目链路包含？","기말 프로젝트 링크에 포함되는 것은?"],
 ["手机网页发命令","桥接程序驱动仿真","仅静态 PDF","仅镜像 pull"],["A","B"],
 "网页→网络→仿真。","웹→네트워크→시뮬입니다."),
(2,["话题相关操作有？","토픽 관련 작업은?"],
 ["ros2 topic echo","ros2 topic pub","docker stop","git pages"],["A","B"],
 "查看与发布。","확인과 발행입니다."),
(3,["Python 基础数据类型包括？","Python 기본 타입은?"],
 ["int","float","仅 Docker","仅 ArUco"],["A","B"],
 "数值类型。","수치 타입입니다."),
(5,["RViz 可显示？","RViz에서 표시 가능한 것은?"],
 ["LaserScan","Image","仅 git log","仅 tailscale"],["A","B"],
 "激光与图像。","라이다와 이미지입니다."),
(7,["良好作业 README 应包含？","좋은 과제 README에 있어야 할 것은?"],
 ["实验截图","运行命令记录","仅空标题","仅外链失效图"],["A","B"],
 "截图与命令。","스크린샷과 명령 기록입니다."),
]

assert len(MC) == 20, len(MC)

CALC = [
("C1","旋转矩阵","2D 点 (1,0) 绕原点逆时针旋转 90°，新坐标是？\n2D 점 (1,0)을 원점 기준 반시계 90° 회전하면?",
 "列向量约定 R=[0,-1;1,0]，[1;0]→[0;1]。",
 "答案 / 정답: (0, 1)"),
("C2","点积","向量 a=(3,4), b=(1,0)，|a|=?，a·b=?\n벡터 a=(3,4), b=(1,0)일 때 |a|=?, a·b=?",
 "|a|=5，a·b=3。","|a|=5, a·b=3"),
("C3","齐次变换","平面旋转 90° 再平移 (2,0)，点 (1,0) 最终坐标？\n평면 90° 회전 후 (2,0) 평행이동, 점 (1,0)의 최종 좌표는?",
 "先 (0,1) 再 + (2,0) → (2,1)。","(2, 1)"),
("C4","四元数模长","四元数 q=(1,0,0,0) 的模长 ||q||=?\n사원수 q=(1,0,0,0)의 크기 ||q||=?",
 "1（单位四元数）。","||q||=1"),
("C5","A* 启发式","网格中从 (0,0) 到 (3,4) 的曼哈顿距离 h=?\n격자에서 (0,0)에서 (3,4)까지 맨해튼 거리 h=?",
 "h=|3-0|+|4-0|=7。","h=7"),
]

PSEUDO = [
("P1","BFS 迷宫","写出用 BFS 在已知网格迷宫上从 start 到 goal 求最短路的伪代码框架（中韩要点即可）。",
 "队列+visited；出队扩展四邻；首次到 goal 回溯路径。",
 "QUEUE, VISITED, ENQUEUE start, while queue, dequeue, if goal, reconstruct"),
("P2","A* 搜索","写出 A* 的伪代码：开放列表、g 值、h 值、f=g+h。",
 "优先队列按 f 最小；更新更优 g 时记录 parent。",
 "OPEN priority by f=g+h, update g and parent"),
("P3","路径跟踪","已知规划器输出路径点序列 waypoints[]，写机器人沿路径前进的伪代码（读当前位姿、选最近路点、转向+前进）。",
 "循环：找最近未到达路点；计算目标朝向；角速度/线速度控制直到到达；切换下一路点。",
 "while not at goal: target=next waypoint; steer toward target; move forward"),
("P4","简单避障","根据激光前方距离 d：d<d_safe 则转向，否则前进。写伪代码。",
 "读 scan；取前方最小距离；if 太近 turn else forward。",
 "read scan min front; if d<safe turn else forward"),
("P5","卷积滑动","2D 卷积：核在输入上滑动，对应位置乘加。写双重循环伪代码框架。",
 "对每个输出像素，核覆盖区域元素乘加求和。",
 "for each output (i,j): sum input[i+di,j+dj]*kernel[di,dj]"),
]

def esc(s): return html.escape(str(s))

def render_options(opts, letters=True):
    L = "ABCD"
    return "\n".join(f'<li><strong>{L[i]}.</strong> {esc(opts[i])}</li>' for i in range(len(opts)))

def build():
    parts = []
    parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI机器人课程 · 期末复习题库 / 기말 복습 문제은행</title>
<style>
:root{--accent:#4f46e5;--bg:#f8fafc;--card:#fff;--muted:#64748b}
*{box-sizing:border-box}
body{font-family:"Noto Sans CJK JP","Noto Sans SC",system-ui,sans-serif;background:var(--bg);color:#1e293b;margin:0;line-height:1.55}
.wrap{max-width:920px;margin:0 auto;padding:24px 16px 60px}
header{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:28px 24px;border-radius:14px;margin-bottom:24px}
header h1{margin:0 0 8px;font-size:1.45em}
header p{margin:4px 0;opacity:.92;font-size:.92em}
.notice{background:#fffbeb;border:1px solid #fcd34d;border-radius:10px;padding:14px 18px;margin-bottom:22px;font-size:.9em}
.section{margin:28px 0 12px;padding-bottom:6px;border-bottom:2px solid #e2e8f0}
.section h2{margin:0;font-size:1.15em;color:var(--accent)}
.q{background:var(--card);border:1px solid #e2e8f0;border-radius:12px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.qid{font-weight:700;color:var(--accent);font-size:.85em}
.tag{display:inline-block;background:#eef2ff;color:#4338ca;font-size:.72em;padding:2px 8px;border-radius:6px;margin-left:6px}
.bilingual .zh{margin:8px 0 4px;font-weight:600}
.bilingual .ko{margin:0 0 10px;color:#475569;font-size:.92em}
ol.opts{margin:8px 0 8px 20px;padding:0}
ol.opts li{margin:4px 0}
.ans{margin-top:10px;padding:10px 12px;background:#f0fdf4;border-radius:8px;font-size:.88em;display:none}
.ans.show{display:block}
.btn{margin-top:8px;padding:6px 14px;border:1px solid #cbd5e1;background:#fff;border-radius:8px;cursor:pointer;font-size:.85em}
.btn:hover{background:#f1f5f9}
.calc,.pseudo{background:#fafafa}
footer{text-align:center;color:var(--muted);font-size:.85em;margin-top:40px}
@media print{.btn,.notice a{display:none}.ans{display:block!important}}
</style>
</head>
<body><div class="wrap">
<header>
<h1>🎓 AI机器人课程 · 期末复习题库</h1>
<p>AI 로봇 공학 · 기말 복습 문제은행 (중한 이중언어)</p>
<p>共 110 题：80 单选 + 20 双选 + 5 计算 + 5 伪代码 | 총 110문항</p>
</header>
<div class="notice">
<strong>📌 复习说明 / 안내</strong><br>
本库供复习准备。<strong>正式笔试抽取：</strong>16 道单选 + 4 道双选 + 1 道计算 + 1 道伪代码（共 22 题）。<br>
정식 필기 시험: <strong>객관식 16 + 복수선택 4 + 계산 1 + 의사코드 1</strong> (총 22문항).<br>
范围：第2–13周讲义（第9周仅计算/伪代码部分；第14周小组项目不考）。第9周数学概念题不单独计入 80+20，但计算/伪代码来自第9周。<br>
强调<strong>基础理解</strong>与<strong>基本操作</strong>（ROS2/Docker/GitHub/OpenCV/组网/仿真）。点击「显示答案」可自测。
</div>
""")

    # Single choice
    parts.append('<div class="section"><h2>一、单选题 80 道 / 객관식 80문항</h2></div>')
    for i, row in enumerate(SC, 1):
        w, zs, ks, oz, ok, ans, ez, ek = row
        parts.append(f'<div class="q" id="q{i}"><div class="qid">Q{i} <span class="tag">Week {w}</span> <span class="tag">单选</span></div>')
        parts.append(f'<div class="bilingual"><div class="zh">{esc(zs)}</div><div class="ko">{esc(ks)}</div></div>')
        parts.append('<ol class="opts">')
        L="ABCD"
        for j in range(4):
            parts.append(f'<li><strong>{L[j]}.</strong> <span class="zh">{esc(oz[j])}</span> / <span class="ko">{esc(ok[j])}</span></li>')
        parts.append(f'</ol><button class="btn" onclick="this.nextElementSibling.classList.toggle(\'show\')">显示答案 / 정답 보기</button>')
        parts.append(f'<div class="ans"><strong>答案 / 정답：{ans}</strong><br>{esc(ez)}<br>{esc(ek)}</div></div>')

    # Multi choice
    parts.append('<div class="section"><h2>二、双选题 20 道 / 복수선택 20문항（每题选 2 项）</h2></div>')
    for i, row in enumerate(MC, 1):
        w, stems, opts, ans, ez, ek = row
        zs, ks = stems
        parts.append(f'<div class="q" id="m{i}"><div class="qid">M{i} <span class="tag">Week {w}</span> <span class="tag">双选</span></div>')
        parts.append(f'<div class="bilingual"><div class="zh">{esc(zs)}</div><div class="ko">{esc(ks)}</div></div><ol class="opts">')
        L="ABCD"
        for j,opt in enumerate(opts):
            parts.append(f'<li><strong>{L[j]}.</strong> {esc(opt)}</li>')
        ans_s = ", ".join(ans)
        parts.append(f'</ol><button class="btn" onclick="this.nextElementSibling.classList.toggle(\'show\')">显示答案 / 정답 보기</button>')
        parts.append(f'<div class="ans"><strong>答案 / 정답：{ans_s}</strong><br>{esc(ez)}<br>{esc(ek)}</div></div>')

    parts.append('<div class="section"><h2>三、计算题 5 道（第9周）/ 계산 5문항 (Week 9)</h2></div>')
    for cid, title, stem, ez, ans in CALC:
        zh, ko = stem.split("\n", 1) if "\n" in stem else (stem, stem)
        parts.append(f'<div class="q calc" id="{cid.lower()}"><div class="qid">{cid} <span class="tag">Week 9</span> <span class="tag">计算</span></div>')
        parts.append(f'<div class="bilingual"><div class="zh">{esc(zh)}</div><div class="ko">{esc(ko)}</div></div>')
        parts.append(f'<button class="btn" onclick="this.nextElementSibling.classList.toggle(\'show\')">显示参考答案 / 참고답안</button>')
        parts.append(f'<div class="ans"><strong>{esc(ans)}</strong><br>{esc(ez)}</div></div>')

    parts.append('<div class="section"><h2>四、算法伪代码 5 道（第9周）/ 의사코드 5문항 (Week 9)</h2></div>')
    for pid, title, stem, ez, ans in PSEUDO:
        zh, ko = (stem, "아래 요구에 맞는 의사코드를 작성하세요.") if "中韩" not in stem else (stem, "아래 요구에 맞는 의사코드를 작성하세요.")
        parts.append(f'<div class="q pseudo" id="{pid.lower()}"><div class="qid">{pid} <span class="tag">Week 9</span> <span class="tag">伪代码</span></div>')
        parts.append(f'<div class="bilingual"><div class="zh">{esc(stem)}</div><div class="ko">아래 요구에 맞는 의사코드(한국어/중국어 요점)를 작성하세요: {esc(title)}</div></div>')
        parts.append(f'<button class="btn" onclick="this.nextElementSibling.classList.toggle(\'show\')">显示参考要点 / 참고 요점</button>')
        parts.append(f'<div class="ans"><pre style="white-space:pre-wrap;margin:0">{esc(ez)}\n---\n{esc(ans)}</pre></div></div>')

    parts.append("""<footer>AI 机器人课程 · 信韩大学 软件学院 · 复习用，非正式试卷<br>AI 로봇 공학 · 복습 전용</footer>
</div></body></html>""")
    return "".join(parts)

html_content = build()
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_content)
print("Wrote", OUT, "chars", len(html_content))
