import math, time

W, H = 56, 28            # terminal size
SHADE = ".,-~:;=!*#$@"   # dark -> bright
REDS = [52, 88, 124, 160, 196, 197,
        198, 204, 205, 211, 218, 225]
lx, ly, lz = -0.35, 0.45, -0.82  # light
sin, cos = math.sin, math.cos


def heart(u, v):
    """a puffy 3D heart surface"""
    s = sin(u)
    x = s * 16 * sin(v) ** 3
    y = s * (13 * cos(v) - 5 * cos(2 * v)
             - 2 * cos(3 * v) - cos(4 * v))
    z = 6 * cos(u)
    return x, y, z


def normal(u, v, e=1e-4):
    px, py, pz = heart(u, v)
    ax, ay, az = heart(u + e, v)
    bx, by, bz = heart(u, v + e)
    ax, ay, az = ax - px, ay - py, az - pz
    bx, by, bz = bx - px, by - py, bz - pz
    n = (ay * bz - az * by,
         az * bx - ax * bz,
         ax * by - ay * bx)
    k = math.hypot(*n) or 1
    if n[0]*px + n[1]*py + n[2]*pz < 0:
        k = -k           # face outwards
    return [c / k for c in n]


# sample the surface once
pts = []
for i in range(1, 80):
    for j in range(320):
        u = i * math.pi / 80
        v = j * math.tau / 320
        pts.append((heart(u, v), normal(u, v)))


def render(t):
    A = t * 1.1                  # spin
    beat = 1 + 0.06 * sin(t * 4) ** 16
    c, s = cos(A), sin(A)
    zbuf = [0.0] * (W * H)
    out = [-1] * (W * H)
    for (x, y, z), (nx, ny, nz) in pts:
        # rotate around the vertical axis
        x, z = x*c + z*s, z*c - x*s
        nx, nz = nx*c + nz*s, nz*c - nx*s
        ooz = 1 / (z + 60)       # 1 / depth
        k = 92 * beat * ooz
        col = int(W / 2 + k * x)
        row = int(H / 2 - k * (y + 2.5) / 2)
        inside = 0 <= col < W and 0 <= row < H
        i = col + W * row
        if inside and ooz > zbuf[i]:
            zbuf[i] = ooz
            L = nx * lx + ny * ly + nz * lz
            B = int(12 * L)      # brightness
            out[i] = min(11, max(0, B))
    return out


def draw(out):
    frame = "\x1b[H"
    for row in range(H):
        for col in range(W):
            b = out[col + W * row]
            if b < 0:
                frame += " "
            else:
                frame += f"\x1b[38;5;{REDS[b]}m"
                frame += SHADE[b]
        frame += "\n"
    msg = "♥  I  L O V E  Y O U  ♥"
    frame += "\n\x1b[1;38;5;205m"
    frame += msg.center(W)
    print(frame, end="", flush=True)


print("\x1b[2J\x1b[?25l", end="")  # clear
t0 = time.time()
try:
    while True:
        draw(render(time.time() - t0))
        time.sleep(0.015)
except KeyboardInterrupt:
    print("\x1b[0m\x1b[?25h")  # show cursor
