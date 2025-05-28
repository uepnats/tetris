import pygame
import random

# --- 定数（ゲームの設定） ---
SCREEN_WIDTH = 300  # 画面の横幅
SCREEN_HEIGHT = 600 # 画面の縦幅
BLOCK_SIZE = 30     # 各ブロックの1辺のサイズ (30x30ピクセル)

BOARD_WIDTH = SCREEN_WIDTH // BLOCK_SIZE  # ボードの横のブロック数 (10)
BOARD_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE # ボードの縦のブロック数 (20)

FPS = 30            # フレームレート (1秒あたりの描画回数)
FALL_SPEED = 500    # ブロックが1マス落下するまでの時間 (ミリ秒)

# 色の定義 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# テトリミノの色
COLORS = [
    (0, 0, 0),      # 空
    (0, 255, 255),  # I (水色)
    (0, 0, 255),    # J (青)
    (255, 165, 0),  # L (オレンジ)
    (255, 255, 0),  # O (黄)
    (0, 255, 0),    # S (緑)
    (128, 0, 128),  # T (紫)
    (255, 0, 0)     # Z (赤)
]

# テトリミノの形状 (0:空, 1~7:ブロックの種類)
# 各ブロックは4x4のグリッドで定義。中心は回転の基準。
SHAPES = [
    [], # インデックス0は使わない
    [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], # I
    [[0,0,0,0], [2,0,0,0], [2,2,2,0], [0,0,0,0]], # J
    [[0,0,0,0], [0,0,4,0], [4,4,4,0], [0,0,0,0]], # L
    [[0,0,0,0], [0,5,5,0], [0,5,5,0], [0,0,0,0]], # O (回転しない)
    [[0,0,0,0], [0,6,6,0], [6,6,0,0], [0,0,0,0]], # S
    [[0,0,0,0], [0,7,0,0], [7,7,7,0], [0,0,0,0]], # T
    [[0,0,0,0], [8,8,0,0], [0,8,8,0], [0,0,0,0]]  # Z (COLORSに合わせて8を7に修正)
]
# Zの定義をCOLORSに合わせて修正
SHAPES[7] = [[0,0,0,0], [7,7,0,0], [0,7,7,0], [0,0,0,0]] # Z

# --- グローバル変数 ---
screen = None
clock = None
game_board = [] # ゲームボードの状態
current_mino = None # 現在操作中のテトリミノ
mino_x, mino_y = 0, 0 # 現在のテトリミノの位置（ボード座標）
last_fall_time = 0 # 最後に落下した時間
score = 0 # ゲームのスコア

# --- 関数定義 ---

def init_game():
    """Pygameの初期化とゲームボードの準備"""
    global screen, clock, game_board

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Tetris")
    clock = pygame.time.Clock()

    # フォントの初期化
    pygame.font.init()

    # ゲームボードを空で初期化 (0は空セル)
    game_board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def create_new_mino():
    """新しいテトリミノを生成し、ボードの上部に配置"""
    global current_mino, mino_x, mino_y
    mino_type = random.randint(1, len(SHAPES) - 1)
    current_mino = SHAPES[mino_type]
    mino_x = BOARD_WIDTH // 2 - len(current_mino[0]) // 2 # 中心に配置
    mino_y = 0 # 一番上から

    # 生成時にすでに衝突している場合はゲームオーバー（簡易実装）
    if check_collision(current_mino, mino_x, mino_y):
        print("ゲームオーバー！")
        return False
    return True

def draw_block(x, y, color_index):
    """指定された座標にブロックを描画"""
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, COLORS[color_index], rect)
    pygame.draw.rect(screen, GRAY, rect, 1) # ブロックの境界線

def draw_ui():
    global score
    """スコアなどのUI要素を描画"""
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", False, WHITE)
    screen.blit(score_text, (10, 10)) # 画面の左上にスコアを表示

def draw_board():
    """ゲームボードと現在操作中のテトリミノを描画"""
    # 既存のボードのブロックを描画
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if game_board[y][x] != 0:
                draw_block(x, y, game_board[y][x])

    # 現在操作中のテトリミノを描画
    if current_mino:
        mino_type = 0 # 初期化
        # 現在のミノのタイプを特定する（適当な方法）
        for row in current_mino:
            for cell in row:
                if cell != 0:
                    mino_type = cell
                    break
            if mino_type != 0:
                break

        for y, row in enumerate(current_mino):
            for x, cell in enumerate(row):
                if cell != 0:
                    draw_block(mino_x + x, mino_y + y, mino_type) # mino_typeで色指定

def check_collision(mino, x_pos, y_pos):
    """テトリミノがボードの端や他のブロックと衝突するか判定"""
    for y, row in enumerate(mino):
        for x, cell in enumerate(row):
            if cell != 0: # ブロックが存在するセルのみ判定
                board_x = x_pos + x
                board_y = y_pos + y

                # 画面外に出ているか、または既存のブロックと重なっているか
                if (board_x < 0 or board_x >= BOARD_WIDTH or
                    board_y >= BOARD_HEIGHT or
                    (board_y >= 0 and game_board[board_y][board_x] != 0)): # ボードの上部外は判定しない
                    return True
    return False

def rotate_mino(mino):
    """テトリミノを時計回りに90度回転"""
    # 4x4の行列として回転
    rotated_mino = [[0 for _ in range(len(mino))] for _ in range(len(mino[0]))]
    for y, row in enumerate(mino):
        for x, cell in enumerate(row):
            rotated_mino[x][len(mino) - 1 - y] = cell
    return rotated_mino

def solidify_mino():
    """テトリミノをボードに固定し、新しいテトリミノを生成"""
    global current_mino, mino_x, mino_y

    # 現在のミノのタイプを特定
    mino_type = 0
    for row in current_mino:
        for cell in row:
            if cell != 0:
                mino_type = cell
                break
        if mino_type != 0:
            break

    for y, row in enumerate(current_mino):
        for x, cell in enumerate(row):
            if cell != 0:
                game_board[mino_y + y][mino_x + x] = mino_type
    
    # ラインクリアチェック
    clear_lines()
    
    # 新しいミノを生成
    if not create_new_mino():
        return False # ゲームオーバー
    return True

def clear_lines():
    """揃ったラインを消去し、上の行を落とす"""
    global game_board, score

    full_lines = []
    for y in range(BOARD_HEIGHT):
        if all(cell != 0 for cell in game_board[y]): # その行が全て埋まっているか
            full_lines.append(y)

    num_cleared_lines = len(full_lines) # 揃ったラインの数

    for line_to_clear in sorted(full_lines, reverse=True): # 下から削除
        del game_board[line_to_clear]
        game_board.insert(0, [0 for _ in range(BOARD_WIDTH)]) # 新しい空の行を一番上に追加
    
    # スコアの加算
    if num_cleared_lines == 1:
        score += 100
    elif num_cleared_lines == 2:
        score += 300
    elif num_cleared_lines == 3:
        score += 500
    elif num_cleared_lines >= 4:
        score += 800


def main_loop():
    """ゲームのメインループ"""
    global mino_x, mino_y, last_fall_time, current_mino

    running = True
    if not create_new_mino(): # ゲーム開始時に最初のミノを生成
        running = False # ゲームオーバー

    while running:
        current_time = pygame.time.get_ticks()

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if current_mino is None:
                    continue
                
                if event.key == pygame.K_LEFT:
                    # 左移動
                    if not check_collision(current_mino, mino_x - 1, mino_y):
                        mino_x -= 1
                elif event.key == pygame.K_RIGHT:
                    # 右移動
                    if not check_collision(current_mino, mino_x + 1, mino_y):
                        mino_x += 1
                elif event.key == pygame.K_DOWN:
                    # 下へ1マス落下 (ソフトドロップ)
                    if not check_collision(current_mino, mino_x, mino_y + 1):
                        mino_y += 1
                        last_fall_time = current_time # 落下時間をリセットして次の自動落下を遅らせる
                    else:
                        if not solidify_mino(): # 固定して新しいミノを生成
                            running = False
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    # 回転
                    rotated = rotate_mino(current_mino)
                    if not check_collision(rotated, mino_x, mino_y):
                        current_mino = rotated
                elif event.key == pygame.K_SPACE:
                    # ハードドロップ（一気に落下）
                    while not check_collision(current_mino, mino_x, mino_y + 1):
                        mino_y += 1
                    if not solidify_mino(): # 固定して新しいミノを生成
                        running = False

        # --- 自動落下処理 ---
        if current_mino is None:
            running = False
            continue

        if current_time - last_fall_time > FALL_SPEED:
            if not check_collision(current_mino, mino_x, mino_y + 1):
                mino_y += 1
            else:
                if not solidify_mino(): # 固定して新しいミノを生成
                    running = False
            last_fall_time = current_time

        # --- 描画処理 ---
        screen.fill(BLACK) # 画面を黒でクリア
        draw_board() # ボードとテトリミノを描画
        draw_ui() # UI要素を描画
        pygame.display.flip() # 画面を更新

        clock.tick(FPS) # フレームレートを制限

    pygame.quit()

# --- メイン実行部分 ---
if __name__ == "__main__":
    init_game()
    main_loop()