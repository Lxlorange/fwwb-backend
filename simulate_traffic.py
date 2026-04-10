# _*_ coding : utf-8 _*_
# @Time :  18:15
# @Author : Lxl
# @File ： simulate_traffic
# @ProjectName : fwwb-backend
import time
import random
import signal
import sys
from datetime import datetime
import httpx

# 基础 URL
BASE_URL = "http://localhost:8000/api/v1"


# ANSI 颜色转义序列
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_log(level: str, message: str, color: str = Colors.OKCYAN):
    """带时间戳和颜色的控制台日志打印"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.ENDC}")


def handle_exit(signum, frame):
    """处理优雅退出"""
    print_log("SYSTEM", "接收到退出信号，正在关停海洋路网模拟监测节点...", Colors.HEADER)
    print_log("SYSTEM", "模拟脚本优雅退出。再见！", Colors.OKGREEN)
    sys.exit(0)


def simulate_wind_wave(client: httpx.Client):
    """模拟风浪数据上报并获取预警"""
    print_log("INFO", "海洋气象浮标采集数据上传中...", Colors.OKBLUE)

    # 模拟近期 3 次检测的风速和波高波动
    recent_data = []
    base_wind = random.uniform(5.0, 18.0)
    base_wave = random.uniform(0.5, 3.5)

    for _ in range(3):
        recent_data.append({
            "wind_speed": round(base_wind + random.uniform(-2, 2), 2),
            "wave_height": round(base_wave + random.uniform(-0.5, 0.5), 2)
        })

    try:
        response = client.post(
            f"{BASE_URL}/anomaly/wind_wave",
            json={"recent_data": recent_data},
            timeout=5.0
        )
        if response.status_code == 200:
            data = response.json()["data"]
            prob = data['anomaly_probability']
            level = data['warning_level']
            sink = data['suggest_sink']

            color = Colors.OKGREEN if level == "LOW" else (Colors.WARNING if level == "MEDIUM" else Colors.FAIL)
            print_log("EVENT",
                      f"平台反馈: 异常概率 {(prob * 100):.1f}%, 告警等级 [{level}], 建议下沉: {'是' if sink else '否'}",
                      color)
        else:
            print_log("ERROR", f"风浪预警接口请求失败: {response.status_code}", Colors.FAIL)
    except Exception as e:
        print_log("ERROR", f"风浪预警节点通信断开: {e}", Colors.FAIL)


def simulate_cv_and_workorder(client: httpx.Client):
    """模拟摄像头监控发现垃圾并流转工单"""
    print_log("INFO", "监控摄像头画面推流执行 AI 分析...", Colors.OKBLUE)

    try:
        # 调用垃圾识别接口
        cv_response = client.post(
            f"{BASE_URL}/cv/detect_trash",
            json={"image_base64": "fake_base64_data_of_ocean_surface"},
            timeout=5.0
        )

        if cv_response.status_code == 200:
            results = cv_response.json()["data"]["results"]
            labels = [r["label"] for r in results]
            print_log("WARN", f"发现疑似海洋垃圾! 目标: {', '.join(labels)}", Colors.WARNING)

            # 立即触发工单流转
            alarm_id = f"ALARM-{int(time.time())}"
            print_log("INFO", f"触发清污行动，下发工单请求 (Alarm ID: {alarm_id})...", Colors.OKBLUE)

            wo_response = client.post(
                f"{BASE_URL}/workorder/create",
                json={
                    "alarm_id": alarm_id,
                    "description": f"AI 视觉识别到漂浮物 ({', '.join(labels)})，请求无人船拦截清理"
                },
                timeout=5.0
            )

            if wo_response.status_code == 200:
                wo_data = wo_response.json()["data"]
                print_log("SUCCESS", f"工单生成完毕: {wo_data['order_id']}, 状态: {wo_data['status']}", Colors.OKGREEN)
            else:
                print_log("ERROR", f"工单生成失败: {wo_response.status_code}", Colors.FAIL)
        else:
            print_log("ERROR", f"视觉识别接口异常: {cv_response.status_code}", Colors.FAIL)

    except Exception as e:
        print_log("ERROR", f"监控节点 AI 推理通信异常: {e}", Colors.FAIL)


def main():
    # 注册 Ctrl+C 处理号
    signal.signal(signal.SIGINT, handle_exit)

    print_log("SYSTEM", "初始化模拟节点集群...", Colors.HEADER)
    print_log("SYSTEM", "正在连接智能海洋中枢服务 (FastAPI) ...", Colors.HEADER)
    print_log("SYSTEM", "按 Ctrl+C 安全停止运行\n", Colors.BOLD)

    time.sleep(2)

    # 使用 httpx 长连接保持性能
    with httpx.Client() as client:
        while True:
            # 每隔 5 秒调用风浪状态
            simulate_wind_wave(client)
            print("-" * 60)

            # 使用 20% 的概率触发垃圾识别及工单流转
            if random.random() < 0.20:
                simulate_cv_and_workorder(client)
                print("=" * 60)

            time.sleep(5)


if __name__ == "__main__":
    main()
