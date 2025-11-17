import serial
import numpy as np

# ---------------------------
# 설정
# ---------------------------
SERIAL_PORT = 'COM3'  # 아두이노 포트
BAUD_RATE = 115200
FS = 1000             # 아두이노 샘플링 주기와 일치
SAMPLES = 1024        # FFT 샘플 수

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def get_peak_frequency(signal, fs):
    yf = np.abs(np.fft.fft(signal))[:len(signal)//2]
    xf = np.fft.fftfreq(len(signal), 1/fs)[:len(signal)//2]
    peak_freq = xf[np.argmax(yf)]
    return peak_freq

try:
    while True:
        dataL, dataR = [], []
        while len(dataL) < SAMPLES:
            if ser.in_waiting >= 2:
                byteL = ser.read(1)
                byteR = ser.read(1)
                dataL.append(ord(byteL))
                dataR.append(ord(byteR))

        # -1~1 정규화
        sigL = np.array(dataL) / 128.0 - 1.0
        sigR = np.array(dataR) / 128.0 - 1.0

        # FFT로 주요 주파수 계산
        peakL = get_peak_frequency(sigL, FS)
        peakR = get_peak_frequency(sigR, FS)

        print(f"L 채널 주요 주파수: {peakL:.1f} Hz, R 채널 주요 주파수: {peakR:.1f} Hz")

except KeyboardInterrupt:
    ser.close()
    print("종료")
