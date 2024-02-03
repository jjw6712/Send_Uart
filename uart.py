import serial
import struct
import random

uart_port = 'COM6'  # 컴퓨터 UART 포트로 변경하세요
baud_rate = 115200   # 바우드 레이트

# 데이터 패킷 생성 함수


def create_data_packet():
    stx = 0x02
    cmd = 0x10
    pressure = random.randint(0x0000, 0xFFFF)
    water_level = random.randint(0x0000, 0xFFFF)
    humidity = random.randint(0x00, 0x64)
    battery = 0x07
    drive = 0x01
    stop = 0x00
    wh = 0x00
    blackout = 0x00
    etx = 0x03

    # 체크섬 계산 최적화: 직접적인 XOR 연산
    checksum = (stx ^ cmd ^
                (pressure >> 8) ^ (pressure & 0xFF) ^
                (water_level >> 8) ^ (water_level & 0xFF) ^
                humidity ^ battery ^ drive ^ stop ^ wh ^ blackout ^ etx)

    # 데이터 패킷 구성 및 바이트 패킹
    data_packet = struct.pack('>B B H H B B B B B B B B', stx, cmd, pressure, water_level, humidity, battery, drive,
                              stop, wh, blackout, etx, checksum)
    return data_packet

# 패킷 생성 및 출력
#data_packet = create_data_packet()
#print(data_packet)



# UART를 통해 데이터를 보내는 함수
def send_data(ser):
    while True:
        data_packet = create_data_packet()
        print(f"송신된 데이터 패킷: {data_packet}")
        ser.write(data_packet)
        # 바우드 레이트에 맞춰 데이터 전송 속도 조절
        #time.sleep(len(data_packet) / (baud_rate / 8))

        # 수신 데이터 확인
        if ser.in_waiting > 0:
            received_data = ser.read(ser.in_waiting).decode('utf-8').strip()
            print(f"수신된 데이터: {received_data}")

            # 디바이스로부터 '0'을 수신하면 데이터 전송 중단
            if received_data == '0':
                print("송신 중단, 수신 대기 상태로 전환")
                break

# UART 통신을 설정하는 메인 함수
def main():
    try:
        with serial.Serial(uart_port, baud_rate, timeout=1) as ser:
            print("UART 통신 연결 성공. 수신 대기중")
            while True:
                if ser.in_waiting > 0:
                    received_data = ser.read(ser.in_waiting).decode('utf-8').strip()
                    print(f"수신된 데이터: {received_data}")

                    # 디바이스로부터 '1'을 수신하면 데이터 전송 시작
                    if received_data == '1':
                        send_data(ser)
    except serial.SerialException as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    main()
