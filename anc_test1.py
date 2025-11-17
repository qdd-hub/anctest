import serial
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from collections import deque

# =====================
# 설정
# =====================
SERIAL_PORT = 'COM3'   
BAUD_RATE = 115200
FILTER_LEN = 64
MU = 0.01
FS = 44100
PLOT_LEN = 500

# =====================
# 시리얼 및 필터 초기화
# =====================
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
w_L = np.zeros(FILTER_LEN)
w_R = np.zeros(FILTER_LEN)
x_buffer = np.zeros(FILTER_LEN)
out_buffer_L = deque(maxlen=PLOT_LEN)
out_buffer_R = deque(maxlen=PLOT_LEN)
primary_buffer = deque(maxlen=PLOT_LEN)

# =====================
# 사운드 출력 콜백 (stereo)
# =====================
def callback(outdata, frames, time, status):
    global out_buffer_L, out_buffer_R
    if len(out_buffer_L) < frames:
        outdata[:,0] = np.zeros(frames)
        outdata[:,1] = np.zeros(frames)
    else:
        outdata[:,0] = np.array([out_buffer_L.popleft() for _ in range(frames)])
        outdata[:,1] = np.array([out_buffer_R.popleft() for _ in range(frames)])

stream = sd.OutputStream(channels=2, samplerate=FS, callback=callback)
stream.start()

# =====================
# Matplotlib 실시간 그래프
# =====================
plt.ion()
fig, ax = plt.subplots()
line_primary, = ax.plot(np.zeros(PLOT_LEN), label="Primary Mic")
line_out_L, = ax.plot(np.zeros(PLOT_LEN), label="Vib L")
line_out_R, = ax.plot(np.zeros(PLOT_LEN), label="Vib R")
ax.set_ylim(-1,1)
ax.set_title("Dual Vib ANC 실시간 시각화")
ax.legend()

# =====================
# FX-LMS 메인 루프
# =====================
print("Dual Vib ANC 시작")
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if not line:
        continue
    try:
        val_primary, val_ref = map(int, line.split(','))
    except:
        continue

    # reference signal 버퍼 업데이트
    x_buffer = np.roll(x_buffer, -1)
    x_buffer[-1] = val_ref

    # FX-LMS 필터 출력
    y_L = np.dot(w_L, x_buffer)
    y_R = np.dot(w_R, x_buffer)

    # error signal
    e_L = val_primary - y_L
    e_R = val_primary - y_R

    # weight 업데이트
    w_L += 2 * MU * e_L * x_buffer
    w_R += 2 * MU * e_R * x_buffer

    # 진동자 출력 신호 (-1 ~ 1)
    sig_L = np.clip(y_L/512.0 - 1.0, -1.0, 1.0)
    sig_R = np.clip(y_R/512.0 - 1.0, -1.0, 1.0)
    out_buffer_L.append(sig_L)
    out_buffer_R.append(sig_R)

    # 시각화
    primary_buffer.append(val_primary/512.0 - 1.0)
    if len(primary_buffer) == PLOT_LEN:
        line_primary.set_ydata(np.array(primary_buffer))
        line_out_L.set_ydata(np.array(out_buffer_L))
        line_out_R.set_ydata(np.array(out_buffer_R))
        plt.pause(0.001)
