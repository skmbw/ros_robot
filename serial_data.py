import serial


def main():
    rs232 = serial.Serial("/dev/ttyTHS1", 115200, timeout=5)
    if not rs232.isOpen():
        print("/dev/ttyTHS1 open failed")
    try:
        while True:
            line = rs232.readline()
            if line != b'':
                print("received: ", line)

    except KeyboardInterrupt:
        if rs232:
            rs232.close()


if __name__ == '__main__':
    main()

