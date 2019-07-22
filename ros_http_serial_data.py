# coding:utf-8

import socket
import serial

from multiprocessing import Process


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

    if request_data.startswith('GET'):
        print('GET request.')
        path = request_data[5:16]
        if path == 'serial/ttl1':
            # response_body = 'get_ttl1'
            response_body = get_serial()
        else:
            print('not service request.' + path)
            client.close()
            return
    elif request_data.startswith('POST'):
        print('POST request.')
        path = request_data[6:17]
        if path == 'serial/ttl1':
            # response_body = 'post_ttl1'
            response_body = get_serial()
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
    response_headers = "Server: ros serial http server\r\n"
    # response_body = "<h1>Python HTTP Test</h1>"
    # response_body = get_serial()
    print('get serial data=[' + response_body + ']')
    response = response_start_line + response_headers + "\r\n" + response_body

    # 向客户端返回响应数据
    print('response success.')
    client.send(bytes(response, "utf-8"))

    # 关闭客户端连接
    client.close()


def get_serial():
    rs232 = serial.Serial("/dev/ttyTHS1", 115200, timeout=5)
    if not rs232.isOpen():
        print("/dev/ttyTHS1 open failed")
    try:
        while True:
            line = rs232.readline()
            if line != b'':
                result = bytes.decode(line)
                break
            else:
                print('cannot get serial data, try again.')
        return result

    except KeyboardInterrupt:
        if rs232:
            rs232.close()
    except Exception as e:
        print('occur exception.')
        print(e)


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("10.70.10.112", 8000))
    server_socket.listen(128)
    print('server start success.')

    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s, %s]用户连接上了" % client_address)
        handle_client_process = Process(target=handle_client, args=(client_socket,))
        handle_client_process.start()
        client_socket.close()
