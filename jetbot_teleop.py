# coding:utf-8

import socket

from multiprocessing import Process
from jetbot import Robot
import subprocess


def handle_client(client):
    """
    处理客户端请求
    """
    request_bytes = client.recv(1024)
    if request_bytes == b'':
        print('request body is null.')
        client.close()
        return
    request_data = bytes.decode(request_bytes)
    print("request data:", request_data)

    rsp = ''
    i = request_data.find('HTTP/')
    if request_data.startswith('GET'):
        print('GET request.')
        path = request_data[5:i].strip()
        if path.startswith('teleop/'):
            print('jetbot command:' + path)
            handle_command(path)
        elif path.startswith('info/'):
            rsp = get_info(path)
        else:
            print('not service request.' + path)
            client.close()
            return
    elif request_data.startswith('POST'):
        print('POST request.')
        path = request_data[6:i].strip()
        if path.startswith('teleop/'):
            print('jetbot command:' + path)
            handle_command(path)
        elif path.startswith('info/'):
            rsp = get_info(path)
        else:
            print('not service request.' + path)
            client.close()
            return
    else:
        print('not support http method, only [GET][POST] support.')
        client.close()
        return

    # 构造响应数据
    response_start_line = "HTTP/1.1 200 OK\r\n"
    response_headers = "Server: jetbot teleop http\r\n"
    response_headers += 'Access-Control-Allow-Headers: Content-Type,Authorization,session_id\r\n'
    response_headers += 'Access-Control-Allow-Methods: GET,PUT,POST,DELETE,OPTIONS,HEAD\r\n'
    response_headers += 'Access-Control-Allow-Origin: *\r\n'

    response = response_start_line + response_headers + "\r\n" + rsp

    # 向客户端返回响应数据
    print('response success.')
    client.send(bytes(response, "utf-8"))

    # 关闭客户端连接
    client.close()


def get_info(path):
    try:
        rsp = ''
        code = path[5:6]
        # 内存使用
        if code == '1':
            print('get memory.')
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
            mem_usage = subprocess.check_output(cmd, shell=True)
            rsp = str(mem_usage.decode('utf-8'))
        # 磁盘使用
        elif code == '2':
            print('get disk used.')
            cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
            disk = subprocess.check_output(cmd, shell=True)
            rsp = str(disk.decode('utf-8'))
            # rsp = 'get_disk_used'
        return rsp
    except Exception as e:
        print(e)


def handle_command(path):
    try:
        code = path[7:8]
        # 停止
        if code == '0':
            print('stop')
            robot.forward(speed=0.1)  # 不能直接停止
            robot.stop()
        # 前进
        elif code == '1':
            print('forward')
            robot.forward(speed=0.6)  # 默认的速度1，比较快
        # 后退
        elif code == '2':
            print('backward')
            robot.backward(speed=0.6)
        # 左转
        elif code == '3':
            print('left')
            robot.left(speed=0.6)
        # 右转
        elif code == '4':
            print('right')
            robot.right(speed=0.6)
        # 设定速度
        elif code == '5':
            lr = path[9:]
            print('setup:' + lr)
            lrs = lr.split('/')
            # 获取速度参数
            left_speed = float(lrs[0])
            right_speed = float(lrs[1])
            if left_speed == 0.0:
                if left_speed == right_speed:  # 停止
                    robot.forward(0.1)
                    robot.stop()
                else:
                    robot.forward(0.1)
                    robot.set_motors(left_speed=left_speed, right_speed=right_speed)
            else:
                if right_speed == 0.0:
                    robot.forward(0.1)
                    robot.set_motors(left_speed=left_speed, right_speed=right_speed)
                else:  # 左右轮都不为0
                    robot.set_motors(left_speed=left_speed, right_speed=right_speed)

    except Exception as e:
        print('setup car speed error.')
        print(e)


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("10.70.10.112", 8000))
    server_socket.listen(128)
    print('server start success.')
    robot = Robot()

    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s, %s] user connect success." % client_address)
        handle_client_process = Process(target=handle_client, args=(client_socket,))
        handle_client_process.start()
        client_socket.close()
