# Your Setting
global SIZE
SIZE = 1.0

# Program Start
import sys, copy
sys.path.append("..")
import CtrlTool as ctl
import cv2

# Setting
global THRESHOLD, DELTA
global BDOWN, BUP, BLOCKSIZE
BUP = 1.1
BLOCKSIZE = BUP
BDOWN = 0.9
THRESHOLD = 0.8
DELTA = 10

# Pictures
global adv_img, next_img, block_img, close_img
adv_img = ctl.read_img("./Img/Adv.png", SIZE)
next_img = ctl.read_img("./Img/Next.png", SIZE)
block_img = ctl.read_img("./Img/Block.png", SIZE * BLOCKSIZE)
close_img = ctl.read_img("./Img/Close.png", SIZE)


def dist(a, b):
    l, r = len(a), 0
    for i in range(l): r += abs(a[i] - b[i])
    return r // l


def build_map(block_res, img):
    # Get Info
    BG_COL = [59, 43, 35, 255]
    BLC_COL = [204, 204, 204, 255]
    a, w, h = block_img.shape[::-1]
    ai, wi, hi = img.shape[::-1]

    # Get Map Range
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(block_res)
    bx, by = max_loc[1], max_loc[0]
    mix = miy = mxx = mxy = 0
    for i in range(-10, 10):
        for j in range(-10, 10):
            x, y = int(bx + i * h + h / 2), int(by + j * w + w / 2)
            if (x in range(hi)) and (y in range(wi)) and (dist(img[x, y], BLC_COL) < DELTA):
                mix, miy = min(mix, i), min(miy, j)
                mxx, mxy = max(mxx, i), max(mxy, j)

    # Gen Map
    n, m = mxx - mix + 1, mxy - miy + 1
    bx, by = bx + mix * h, by + miy * w
    global map_arr, map_pos
    map_arr = [[0 for _ in range(m)] for _ in range(n)]
    map_pos = [[(int(bx + i * h + h / 2), int(by + j * w + w / 2)) for j in range(m)] for i in range(n)]

    sx, sy = 0, 0
    # Fill Map
    for i in range(n):
        for j in range(m):
            x, y = map_pos[i][j][0], map_pos[i][j][1]
            if (x in range(hi)) and (y in range(wi)):
                col = img[x, y]
                if dist(col, BG_COL) < DELTA: continue
                if dist(col, BLC_COL) < DELTA:
                    map_arr[i][j] = 1
                else:
                    map_arr[i][j] = 2
                    sx, sy = i, j

    return n, m, sx, sy


def dfs(n, m, x, y, c, ans):
    if c == 0: return True

    dx = [0, -1, 0, 1]
    dy = [-1, 0, 1, 0]
    for k in range(4):
        tx, ty = x + dx[k], y + dy[k]
        if (tx in range(n)) and (ty in range(m)) and map_arr[tx][ty] == 1:
            ans.append((tx, ty))
            map_arr[tx][ty] = 2
            if dfs(n, m, tx, ty, c - 1, ans): return True
            ans.pop()
            map_arr[tx][ty] = 1

    return False


def dfs_map(n, m, sx, sy):
    # Calc Rest
    cnt = 0
    for i in range(n):
        for j in range(m):
            if map_arr[i][j] == 1: cnt = cnt + 1

    ans = []
    dfs(n, m, sx, sy, cnt, ans)
    return ans


def exec_game(sx, sy, ans):
    for p in ans:
        ctl.long_click(map_pos[p[0]][p[1]][1], map_pos[p[0]][p[1]][0], 50)


def click_button(res, img):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    ai, wi, hi = img.shape[::-1]
    bx, by = max_loc[1], max_loc[0]
    x, y = bx + hi / 2, by + wi / 2
    ctl.click(y, x)

def map_err():
    global BDOWN, BUP, BLOCKSIZE
    global adv_img, next_img, block_img, close_img
    print("Map Error: %f" % BLOCKSIZE)
    BLOCKSIZE = BLOCKSIZE + 0.01
    if BLOCKSIZE > BUP: BLOCKSIZE = BDOWN
    block_img = ctl.read_img("./Img/Block.png", SIZE * BLOCKSIZE)

def main():
    global adv_img, next_img, block_img, close_img
    last_err = err = 0
    while True:
        # Get Screen
        img = ctl.screen()
        ori = copy.copy(img)

        # Match Pattern
        block_loc, block_res = ctl.match_img(img, block_img, THRESHOLD)
        close_loc, close_res = ctl.match_img(img, close_img, THRESHOLD)
        next_loc, next_res = ctl.match_img(img, next_img, THRESHOLD)
        adv_loc, adv_res = ctl.match_img(img, adv_img, THRESHOLD)

        # Debug
        key = ctl.show_img(img) & 0xFF

        # Err Ctrl
        last_err = err
        err = 0

        # Machine
        if len(block_loc[0]) > 100:  # Game State
            print("> Game State")

            # Build Map
            n, m, sx, sy = build_map(block_res, ori)

            # Print Map
            print(">> Map")
            code = [" ", "#", "*"]
            for i in range(n):
                print(">> ", end="")
                for j in range(m):
                    print(code[map_arr[i][j]], end="")
                print("")

            # Get Answer
            ans = dfs_map(n, m, sx, sy)

            # Error
            if len(ans)==0: map_err()

            # Exec Answer
            exec_game(sx, sy, ans)

        elif len(adv_loc[0]) > 0 or len(close_loc[0]) > 0:  # Advertisement State / Close State
            print("> Close State")
            click_button(close_res, close_img)

        elif len(next_loc[0]) > 0:  # Next State
            print("> Next State")
            click_button(next_res, next_img)

        else:  # Error State
            print("> Error State")
            err = last_err + 1
            if err > 5: map_err()

        # Keep Awake
        ctl.click(0, 0)

if __name__ == "__main__": main()
