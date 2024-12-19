import pyxel
import random

# 定数定義
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300
CELL_SIZE = 25
PLAYER_SPEED = 2
ENEMY_SPEED = 1

# 迷路データ（1: 壁, 0: 通路）
MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class PacmanGame:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)

        # プレイヤーの初期位置
        self.player_x, self.player_y = self.find_valid_start_position()
        self.score = 0

        # 敵キャラクターの初期位置リスト
        self.enemies = [self.find_valid_start_position()]

        # ドットの初期配置
        self.all_dots = self.generate_dots()
        self.dots = self.all_dots[:]

        # 取られたエサの復活管理
        self.eaten_dots = []  # [(dot_position, time_eaten)]

        # プレイヤーの移動方向（初期は右向き）
        self.direction = 'RIGHT'

        # 口の開閉状態
        self.mouth_open = True

        # ゲームオーバーフラグ
        self.game_over = False

        # 時間管理
        self.start_time = pyxel.frame_count

        # ゲームの開始
        pyxel.run(self.update, self.draw)

    def find_valid_start_position(self):
        """迷路内の通路上で有効な初期位置を探す"""
        while True:
            x = random.randint(1, len(MAZE[0]) - 2)
            y = random.randint(1, len(MAZE) - 2)
            if MAZE[y][x] == 0:
                return x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2

    def generate_dots(self):
        """迷路上にドット（エサ）を配置"""
        dots = []
        for y in range(len(MAZE)):
            for x in range(len(MAZE[0])):
                if MAZE[y][x] == 0:
                    dots.append((x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        return dots

    def update(self):
        if self.game_over:
            return

        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_UP):
            new_x = self.player_x
            new_y = self.player_y - PLAYER_SPEED
            if self.is_valid_move(new_x, new_y):
                self.player_y = new_y
            self.direction = 'UP'
        if pyxel.btn(pyxel.KEY_DOWN):
            new_x = self.player_x
            new_y = self.player_y + PLAYER_SPEED
            if self.is_valid_move(new_x, new_y):
                self.player_y = new_y
            self.direction = 'DOWN'
        if pyxel.btn(pyxel.KEY_LEFT):
            new_x = self.player_x - PLAYER_SPEED
            new_y = self.player_y
            if self.is_valid_move(new_x, new_y):
                self.player_x = new_x
            self.direction = 'LEFT'
        if pyxel.btn(pyxel.KEY_RIGHT):
            new_x = self.player_x + PLAYER_SPEED
            new_y = self.player_y
            if self.is_valid_move(new_x, new_y):
                self.player_x = new_x
            self.direction = 'RIGHT'

        # 敵キャラクターの移動
        self.update_enemies()

        # ドットとの衝突判定
        for dot in self.dots[:]:
            if abs(self.player_x - dot[0]) < 8 and abs(self.player_y - dot[1]) < 8:
                self.dots.remove(dot)
                self.eaten_dots.append((dot, pyxel.frame_count))
                self.score += 1

        # 取られたエサを復活
        self.respawn_eaten_dots()

        # プレイヤーと敵の衝突判定
        for enemy_x, enemy_y in self.enemies:
            if abs(self.player_x - enemy_x) < 10 and abs(self.player_y - enemy_y) < 10:
                self.game_over = True

        # 5秒経過ごとに敵を追加
        if (pyxel.frame_count - self.start_time) // 30 == 5:
            self.enemies.append(self.find_valid_start_position())
            self.start_time = pyxel.frame_count

        # 口の開閉アニメーション
        if pyxel.frame_count % 10 == 0:
            self.mouth_open = not self.mouth_open

    def update_enemies(self):
        """敵キャラクターの移動"""
        new_positions = []
        for enemy_x, enemy_y in self.enemies:
            possible_moves = []
            enemy_cell_x = enemy_x // CELL_SIZE
            enemy_cell_y = enemy_y // CELL_SIZE
            player_cell_x = self.player_x // CELL_SIZE
            player_cell_y = self.player_y // CELL_SIZE

            # 上下左右の移動を検討
            if self.is_valid_move(enemy_x, enemy_y - ENEMY_SPEED):
                possible_moves.append(('UP', abs(enemy_cell_y - 1 - player_cell_y) + abs(enemy_cell_x - player_cell_x)))
            if self.is_valid_move(enemy_x, enemy_y + ENEMY_SPEED):
                possible_moves.append(('DOWN', abs(enemy_cell_y + 1 - player_cell_y) + abs(enemy_cell_x - player_cell_x)))
            if self.is_valid_move(enemy_x - ENEMY_SPEED, enemy_y):
                possible_moves.append(('LEFT', abs(enemy_cell_y - player_cell_y) + abs(enemy_cell_x - 1 - player_cell_x)))
            if self.is_valid_move(enemy_x + ENEMY_SPEED, enemy_y):
                possible_moves.append(('RIGHT', abs(enemy_cell_y - player_cell_y) + abs(enemy_cell_x + 1 - player_cell_x)))

            # 距離が最小の方向を選択
            if possible_moves:
                possible_moves.sort(key=lambda move: move[1])  # 距離の昇順でソート
                best_move = possible_moves[0][0]

                if best_move == 'UP':
                    enemy_y -= ENEMY_SPEED
                elif best_move == 'DOWN':
                    enemy_y += ENEMY_SPEED
                elif best_move == 'LEFT':
                    enemy_x -= ENEMY_SPEED
                elif best_move == 'RIGHT':
                    enemy_x += ENEMY_SPEED

            new_positions.append((enemy_x, enemy_y))

        self.enemies = new_positions

    def respawn_eaten_dots(self):
        """5秒経過したエサを復活させる"""
        for dot, time_eaten in self.eaten_dots[:]:
            if (pyxel.frame_count - time_eaten) // 30 >= 5:
                self.dots.append(dot)
                self.eaten_dots.remove((dot, time_eaten))

    def is_valid_move(self, new_x, new_y):
        """移動先が通路か壁かを確認"""
        if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
            maze_x = new_x // CELL_SIZE
            maze_y = new_y // CELL_SIZE
            if MAZE[maze_y][maze_x] == 0:  # 通路のみ移動可能
                return True
        return False

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.frame_count % 16)
            return

        # 迷路の描画
        self.draw_maze()

        # プレイヤーの描画
        self.draw_pacman()

        # 敵キャラクターの描画
        for enemy_x, enemy_y in self.enemies:
            pyxel.circ(enemy_x, enemy_y, 8, 8)  # 敵を赤色で描画

        # ドットの描画
        for dot in self.dots:
            pyxel.circ(dot[0], dot[1], 4, 10)

        # スコアの表示
        pyxel.text(5, 5, f"Score: {self.score}", 7)

    def draw_maze(self):
        """迷路を描画"""
        for y in range(len(MAZE)):
            for x in range(len(MAZE[0])):
                if MAZE[y][x] == 1:
                    pyxel.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, 1)

    def draw_pacman(self):
        """進行方向に応じて口を開閉するパックマンを描画"""
        pyxel.circ(self.player_x, self.player_y, 8, 9)  # 黄色の体
        if self.mouth_open:
            if self.direction == 'UP':
                pyxel.tri(self.player_x, self.player_y, self.player_x - 8, self.player_y - 8, self.player_x + 8, self.player_y - 8, 0)
            elif self.direction == 'DOWN':
                pyxel.tri(self.player_x, self.player_y, self.player_x - 8, self.player_y + 8, self.player_x + 8, self.player_y + 8, 0)
            elif self.direction == 'LEFT':
                pyxel.tri(self.player_x, self.player_y, self.player_x - 8, self.player_y - 8, self.player_x - 8, self.player_y + 8, 0)
            elif self.direction == 'RIGHT':
                pyxel.tri(self.player_x, self.player_y, self.player_x + 8, self.player_y - 8, self.player_x + 8, self.player_y + 8, 0)

# ゲームの起動
PacmanGame()
