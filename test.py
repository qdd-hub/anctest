import numpy as np
import sounddevice as sd
import time

# ---------------------------
# 설정
# ---------------------------
FS = 44100         # 샘플링 레이트
DURATION = 1       # 1초씩 반복 재생
FREQ_L = 70        # L 채널 사인파 주파수 (Hz)
FREQ_R = 70        # R 채널 사인파 주파수 (Hz)
AMPLITUDE = 0.5    # 0~1, 진폭

# ---------------------------
# 사인파 생성
# ---------------------------
t = np.linspace(0, DURATION, int(FS*DURATION), endpoint=False)

# 진동자 anti-phase 신호
# anti-phase: 1-x or -1*original
tone_L = -AMPLITUDE * np.sin(2 * np.pi * FREQ_L * t)  # L 채널 역위상
tone_R = -AMPLITUDE * np.sin(2 * np.pi * FREQ_R * t)  # R 채널 역위상

# L/R 채널 합치기 (stereo)
stereo = np.column_stack((tone_L, tone_R))

# ---------------------------
# 반복 재생 루프
# ---------------------------
try:
    print("실험용 60~80Hz 사인파 출력 시작...")
    while True:
        sd.play(stereo, samplerate=FS, blocking=True)
except KeyboardInterrupt:
    print("실험 종료")
