import numpy as np, wave, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SR = 44100; DUR = 30.0
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(pan, 0)); R[i:i + n] += sig[:n] * gain * (1 + min(pan, 0))
def marimba(m, d=0.5, v=1.0):
    t = np.arange(int(SR * d)) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 25) + 0.15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40)
    return s * v * 0.5
def bell(m, d=1.2, v=1.0):
    t = np.arange(int(SR * d)) / SR; f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for a, r, k in [(1, 1, 3), (0.5, 2.76, 5), (0.35, 5.4, 8), (0.25, 3, 4)])
    return s * v * 0.35
def bass(m, d=0.35):
    t = np.arange(int(SR * d)) / SR
    return np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 6) * 0.5
def pop(d=0.18):
    t = np.arange(int(SR * d)) / SR; f = 300 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 20) * 0.5
def whoosh(d=0.5):
    t = np.arange(int(SR * d)) / SR; rng = np.random.default_rng(1)
    n = rng.standard_normal(len(t)); k = 60
    n = np.convolve(n, np.ones(k) / k, 'same')
    return n * np.sin(np.pi * t / d) ** 2 * 1.6
def sweep(d=0.9):
    t = np.arange(int(SR * d)) / SR; f = 800 + 2400 * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.25

BPM = 124; beat = 60 / BPM
# C major pentatonic melody (MIDI), 2 bars loop of 8 eighth notes
mel = [79, 76, 79, 81, 79, 76, 72, 76,  74, 76, 79, 76, 74, 72, 74, 67]
chords = [48, 53, 55, 48]  # C F G C bass roots
n8 = beat / 2
steps = int(DUR / n8)
for s in range(steps):
    t0 = s * n8
    if t0 < 0.2: continue
    m = mel[s % len(mel)]
    add(marimba(m, 0.45), t0, pan=-0.2, gain=0.55)
    if s % 2 == 0: add(marimba(m - 12, 0.4, 0.5), t0, pan=0.2, gain=0.35)
    if s % 4 == 0: add(bass(chords[(s // 8) % 4]), t0, gain=0.7)
    if s % 2 == 1: add(np.hanning(400)[:200] * 0, t0)
# soft tick on beats
for b in range(int(DUR / beat)):
    t = np.arange(int(SR * 0.04)) / SR
    add(np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) * 0.12, b * beat, gain=1)

# SFX
add(whoosh(0.5), 0.0, gain=0.5); add(pop(), 0.35, gain=0.8); add(pop(), 0.6, gain=0.6)
for T in (3.0, 8.0, 15.0, 22.0, 27.0): add(whoosh(0.45), T, gain=0.45)
for i in range(3): add(pop(), 3.3 + 0.5 * i, gain=0.8)
add(sweep(1.0), 10.4, gain=0.8); add(bell(88, 1.5), 10.6, gain=0.9); add(bell(95, 1.5), 10.72, gain=0.7)
for i, m in enumerate([72, 76, 79, 84, 88]): add(bell(m, 1.4), 15.6 + 0.85 * i, gain=0.9)
add(bell(96, 2.0), 19.0, gain=0.6)
# drumroll-ish tension 22.0-23.8
t = np.arange(int(SR * 1.8)) / SR
for k in range(36):
    tt = 22.0 + k * 0.05; add(pop(0.06) * (0.3 + 0.7 * k / 36), tt, gain=0.4)
add(sweep(0.6), 23.5, gain=0.8)
for i, m in enumerate([72, 79, 84, 88, 91]): add(bell(m, 2.0), 23.8 + 0.06 * i, gain=0.8)
add(pop(0.25), 23.8, gain=1.0)
add(pop(), 27.4, gain=0.8); add(bell(91, 2.0), 27.4, gain=0.7); add(bell(96, 2.0), 27.5, gain=0.6)
add(marimba(84, 1.0), 28.0, gain=0.8); add(marimba(88, 1.0), 28.25, gain=0.8); add(marimba(91, 1.2), 28.5, gain=0.9); add(bell(96, 1.5), 28.5, gain=0.5)

# fades
f = np.minimum(1, np.linspace(0, DUR, N) / 0.1) * np.minimum(1, (DUR - np.linspace(0, DUR, N)) / 1.2)
L *= f; R *= f
pk = max(np.abs(L).max(), np.abs(R).max()); g = 0.8 / pk
pcm = (np.stack([L, R], 1) * g * 32767).astype('<i2')
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", pk)
