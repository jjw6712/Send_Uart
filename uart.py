import random
import serial
import time

uart_port = 'COM6'  # 컴퓨터 UART 포트로 변경하세요
baud_rate = 115200   # 바우드 레이트

# 응답 프로토콜에 따른 데이터 패킷 구성
stx = 0x02
cmd = 0x10
etx = 0x03

# 데이터 패킷 생성 함수
def create_data_packet(counter):
    pressure = random.uniform(1.0, 5.0)  # 1.0 ~ 5.0 범위의 랜덤 수압
    battery = random.randint(10, 100)  # 10% ~ 100% 범위의 랜덤 배터리 잔량

    # 데이터를 ASCII 코드 형태로 변환
    pressure_bytes = bytearray(str(f"{pressure:.3f}"), 'utf-8')
    battery_bytes = bytearray(str(f"{battery}"), 'utf-8')

    data_bytes = pressure_bytes + b',' + battery_bytes + b'%'
    data_packet = bytearray([stx, cmd]) + data_bytes + bytearray([etx])
    checksum = sum(data_packet) % 256  # 체크섬 계산
    data_packet.append(checksum)
    return data_packet

# UART를 통해 데이터를 보내는 함수
def send_data(ser):
    counter = 0
    while True:
        data_packet = create_data_packet(counter)
        print(f"송신된 데이터 패킷: {data_packet}")
        ser.write(data_packet)
        # 바우드 레이트에 맞춰 데이터 전송 속도 조절
        time.sleep(len(data_packet) / (baud_rate / 8))
        counter += 1

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
