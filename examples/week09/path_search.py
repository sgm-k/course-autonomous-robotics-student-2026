"""地図の上で、スタートからゴールまでの最短経路を探すプログラム（第9回）。

幅優先探索・ダイクストラ法・A* の3つで探し、結果を表と PNG の画像で見せる。
TODO の部分（A* の見積もりと、経路のたどり直し）を書いて完成させる。

使い方:
    ros2 run week09 path_search 地図のYAML [ゴールのx ゴールのy]
    （スタートは地図の原点 (0, 0)。座標は地図の座標 [m]）
"""

import heapq
import math
import os
import struct
import sys
import time
import zlib
from collections import deque

import yaml

ROBOT_RADIUS = 0.15   # ロボットの半径 [m]。壁からこれだけ離れたマスだけを通れるとする
MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # 8方向


# ------------------------------------------------------------ 地図の読み込み
def read_map(yaml_path):
    """地図（YAML と PGM）を読み、通れるマスを True にした2次元のリストを返す。"""
    with open(yaml_path) as f:
        info = yaml.safe_load(f)
    image = os.path.join(os.path.dirname(os.path.abspath(yaml_path)), info['image'])
    with open(image, 'rb') as f:
        data = f.read()
    # PGM の頭（P5、幅、高さ、最大値）を読む
    fields, pos = [], 0
    while len(fields) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b'#':
            pos = data.index(b'\n', pos)
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        fields.append(data[pos:end])
        pos = end
    width, height = int(fields[1]), int(fields[2])
    pixels = data[pos + 1:]
    free = [[pixels[r * width + c] >= 250 for c in range(width)] for r in range(height)]
    # ロボットの半径の分だけ、壁を太らせる（壁のすぐそばは通れない）
    k = int(math.ceil(ROBOT_RADIUS / info['resolution']))
    wall = [(r, c) for r in range(height) for c in range(width) if pixels[r * width + c] < 100]
    passable = [row[:] for row in free]
    for r, c in wall:
        for dr in range(-k, k + 1):
            for dc in range(-k, k + 1):
                if dr * dr + dc * dc <= k * k and 0 <= r + dr < height and 0 <= c + dc < width:
                    passable[r + dr][c + dc] = False
    return passable, info['resolution'], info['origin']


def to_cell(x, y, resolution, origin, height):
    """地図の座標 (x, y) [m] を、マス (行, 列) に直す。画像は上の行が y の大きい側。"""
    col = int((x - origin[0]) / resolution)
    row = height - 1 - int((y - origin[1]) / resolution)
    return (row, col)


# ------------------------------------------------------------ 探索
def heuristic(cell, goal):
    """A* の見積もり：cell から goal までの距離の見積もり [マス]。"""
    # TODO: cell と goal の直線距離を返す。cell[0]、goal[0] が行、cell[1]、goal[1] が列。
    #       math.hypot を使う。0.0 のままだと、ダイクストラ法と同じ動きになる。
    return 0.0


def reconstruct_path(parent, goal):
    """parent（各マスの1つ前のマス）をゴールから逆にたどり、スタートからゴールまでのマスのリストを返す。"""
    path = []
    # TODO: goal から始めて、parent をたどりながら path に加えていく。
    #       スタートのマスは parent[スタート] が None になっている。
    #       最後に path.reverse() で、スタートからゴールの順に並べ直す。
    return path


def search(grid, start, goal, method):
    """method（'bfs'、'dijkstra'、'astar'）で経路を探す。(経路, 調べたマスの集合) を返す。"""
    height, width = len(grid), len(grid[0])
    parent = {start: None}
    cost = {start: 0.0}
    visited = set()
    if method == 'bfs':
        queue = deque([start])               # 幅優先探索：先に入れたマスから調べる
    else:
        queue = [(0.0, start)]               # 優先度つきキュー：小さい値のマスから調べる
    while queue:
        if method == 'bfs':
            cell = queue.popleft()
        else:
            _, cell = heapq.heappop(queue)
        if cell in visited:
            continue
        visited.add(cell)
        if cell == goal:
            return reconstruct_path(parent, goal), visited
        for dr, dc in MOVES:
            nxt = (cell[0] + dr, cell[1] + dc)
            if not (0 <= nxt[0] < height and 0 <= nxt[1] < width) or not grid[nxt[0]][nxt[1]]:
                continue
            step = math.hypot(dr, dc)        # 横・縦は 1、斜めは √2
            new_cost = cost[cell] + step
            if method == 'bfs':
                if nxt not in parent:
                    parent[nxt] = cell
                    cost[nxt] = new_cost
                    queue.append(nxt)
            elif nxt not in cost or new_cost < cost[nxt]:
                parent[nxt] = cell
                cost[nxt] = new_cost
                priority = new_cost
                if method == 'astar':
                    priority = new_cost + heuristic(nxt, goal)   # A*：ここまでの距離＋残りの見積もり
                heapq.heappush(queue, (priority, nxt))
    return [], visited


def path_length(path, resolution):
    """マスのリストの長さ [m]。"""
    return sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(path, path[1:])) * resolution


# ------------------------------------------------------------ 画像に描く
def save_png(filename, grid, visited, path):
    """通れる所は白、通れない所は灰色、調べたマスは水色、経路は赤で PNG に描く。"""
    on_path = set(path)
    rows = []
    for r, row in enumerate(grid):
        line = bytearray([0])                # 各行の先頭はフィルタの種類（0：なし）
        for c, ok in enumerate(row):
            if (r, c) in on_path:
                line += bytes((220, 0, 0))
            elif (r, c) in visited:
                line += bytes((150, 210, 250))
            elif ok:
                line += bytes((255, 255, 255))
            else:
                line += bytes((120, 120, 120))
        rows.append(bytes(line))

    def chunk(kind, body):
        return (struct.pack('>I', len(body)) + kind + body
                + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff))
    header = struct.pack('>IIBBBBB', len(grid[0]), len(grid), 8, 2, 0, 0, 0)
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
                + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b''))


def main():
    if len(sys.argv) < 2:
        print('使い方: ros2 run week09 path_search 地図のYAML [ゴールのx ゴールのy]')
        return
    goal_xy = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) >= 4 else (5.0, 3.0)
    grid, resolution, origin = read_map(sys.argv[1])
    height = len(grid)
    start = to_cell(0.0, 0.0, resolution, origin, height)
    goal = to_cell(goal_xy[0], goal_xy[1], resolution, origin, height)
    for name, cell in (('スタート', start), ('ゴール', goal)):
        if not grid[cell[0]][cell[1]]:
            print(f'{name}が壁の近くか、地図の外にある。ゴールの座標を変える。')
            return
    print(f'スタート (0.0, 0.0)　ゴール {goal_xy}　地図 {len(grid[0])} × {height} マス')
    print('方法          経路の長さ [m]   調べたマス   かかった時間 [s]')
    for method in ('bfs', 'dijkstra', 'astar'):
        t0 = time.time()
        path, visited = search(grid, start, goal, method)
        dt = time.time() - t0
        print(f'{method:10s}   {path_length(path, resolution):10.2f}   {len(visited):10d}   {dt:12.2f}')
        save_png(f'week09_{method}.png', grid, visited, path)
    print('画像 week09_bfs.png、week09_dijkstra.png、week09_astar.png を保存した')


if __name__ == '__main__':
    main()
