import os
import sys
import pygame as pg
import random
import math

# 画面サイズと移動量の定義
WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -7),
    pg.K_DOWN: (0, +7),
    pg.K_LEFT: (-7, 0),
    pg.K_RIGHT: (+7, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# スタート画面の表示
def start_screen(screen):
    screen.fill((0, 0, 0))
    font_path = "meiryo.ttc"
    if os.path.exists(font_path):
        title_font = pg.font.Font(font_path, 100)
        button_font = pg.font.Font(font_path, 60)
    else:
        title_font = pg.font.SysFont("msgothic", 100)
        button_font = pg.font.SysFont("msgothic", 60)

    title_text = title_font.render("コウカトンテイル", True, (255, 0, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)

    start_prompt_text = button_font.render("エンターキーを押して続行", True, (255, 255, 255))
    start_prompt_rect = start_prompt_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
    screen.blit(start_prompt_text, start_prompt_rect)

    pg.display.update()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                return

# モード選択画面
def mode_selection_screen(screen, player_hp, enemy_hp):
    screen.fill((0, 0, 0))
    font_path = "meiryo.ttc"
    if os.path.exists(font_path):
        button_font = pg.font.Font(font_path, 60)
    else:
        button_font = pg.font.SysFont("msgothic", 60)

    attack_button_text = button_font.render("攻撃", True, (255, 255, 255))
    evade_button_text = button_font.render("逃げる", True, (255, 255, 255))
    attack_button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)
    evade_button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
    alien_image = pg.image.load("fig/alien1.png")
    alien_rect = alien_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(alien_image, alien_rect)
        pg.draw.rect(screen, (255, 255, 255), (alien_rect.left, alien_rect.top - 20, alien_rect.width, 10), 2)
        pg.draw.rect(screen, (255, 0, 0), (alien_rect.left, alien_rect.top - 20, int(alien_rect.width * (enemy_hp / 100)), 10))

        # 自分のHPバーを描画
        draw_hp_gauge(screen, player_hp, x=20, y=20)

        mouse_pos = pg.mouse.get_pos()

        if attack_button_rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, (255, 255, 0), attack_button_rect, 0)
        else:
            pg.draw.rect(screen, (0, 0, 0), attack_button_rect, 0)
        pg.draw.rect(screen, (255, 255, 255), attack_button_rect, 2)
        screen.blit(attack_button_text, attack_button_text.get_rect(center=attack_button_rect.center))

        if evade_button_rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, (255, 255, 0), evade_button_rect, 0)
        else:
            pg.draw.rect(screen, (0, 0, 0), evade_button_rect, 0)
        pg.draw.rect(screen, (255, 255, 255), evade_button_rect, 2)
        screen.blit(evade_button_text, evade_button_text.get_rect(center=evade_button_rect.center))

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if attack_button_rect.collidepoint(mouse_pos):
                    enemy_hp -= 10
                    if enemy_hp <= 0:
                        victory(screen)  # 敵HPが0になったら終了
                    return "attack", player_hp, enemy_hp
                if evade_button_rect.collidepoint(mouse_pos):
                    return "evade", player_hp, enemy_hp


# 工科トンの画像を取得
def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    kk_images = {
        (0, -7): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 1),
        (0, 7): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 1),
        (-7, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1),
        (7, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1), True, False),
        (7, -7): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1), True, False),
        (-7, 7): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1),
        (-7, -7): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1),
        (7, 7): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1), True, False),
    }
    return kk_images.get(sum_mv, pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1))

# ビームの向きを回転
def rotate_beam(beam_img, target_rct, beam_rct):
    dx = target_rct.centerx - beam_rct.centerx
    dy = target_rct.centery - beam_rct.centery
    angle = math.degrees(math.atan2(-dy, dx))
    return pg.transform.rotozoom(beam_img, angle, 1)

# 爆弾とビームの処理
def post_attack_game(screen, player_hp, enemy_hp):
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()

    mode = random.choice(["bomb", "beam"])
    print("Selected mode:", mode)

    bombs = []
    if mode == "bomb":
        for i in range(3):
            bb_size = bb_imgs[0].get_width()
            x, y = random_non_overlapping_position(kk_rct, bb_size)
            bb_rct = bb_imgs[0].get_rect()
            bb_rct.centerx = x
            bb_rct.centery = y
            vx, vy = +5, -5
            bombs.append({'rct': bb_rct, 'vx': vx, 'vy': vy})
    beam_img_original = pg.image.load("fig/beam.png") if mode == "beam" else None
   # ビームの向きを固定して発射
    beams = []
    if mode == "beam":
        next_beam_time = 25
        beam_size = beam_img_original.get_width()

    flash_counter = 0
    clock = pg.time.Clock()
    tmr = 0
    while True:
        elapsed_time = tmr // 50
        if elapsed_time >= 15:  # 15秒で終了
            return player_hp, enemy_hp

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return player_hp, enemy_hp

        screen.fill((0, 0, 0))
        font = pg.font.SysFont("msgothic", 40)
        timer_text = font.render(f"Time: {15 - elapsed_time} s", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH - 200, 20))

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        current_kk_img = get_kk_img(tuple(sum_mv))
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        idx = min(tmr // 250 + 1, 9)
        # 爆弾処理
        if mode == "bomb":
            for bomb in bombs:
                bb_rct = bomb['rct']
                vx = bomb['vx']
                vy = bomb['vy']

                bb_img = bb_imgs[idx]
                bb_acc = bb_accs[idx]
                avx = vx * bb_acc * 0.8
                avy = vy * bb_acc * 0.8
                bb_rct.move_ip(avx, avy)

                yoko, tate = check_bound(bb_rct)
                if not yoko:
                    bomb['vx'] *= -1
                if not tate:
                    bomb['vy'] *= -1

                screen.blit(bb_img, bb_rct)

                # 当たり判定（無敵中は受けない）
                if flash_counter == 0:
                    kk_mask = pg.mask.from_surface(current_kk_img)
                    bb_mask = pg.mask.from_surface(bb_img)
                    offset = (bb_rct.x - kk_rct.x, bb_rct.y - kk_rct.y)
                    if kk_mask.overlap(bb_mask, offset):
                        player_hp = max(player_hp - 10, 0)
                        # 再配置
                        new_bb_size = bb_img.get_width()
                        x, y = random_non_overlapping_position(kk_rct, new_bb_size)
                        bb_rct.centerx = x
                        bb_rct.centery = y
                        bomb['vx'] = +5
                        bomb['vy'] = -5
                        # 無敵
                        flash_counter = 100
       # ビーム処理
        if mode == "beam":
        # 一定間隔(15フレームごと)にビーム出現
            if tmr > next_beam_time:
                # こうかとんと重ならない位置でビーム出現
                x, y = random_non_overlapping_position(kk_rct, beam_size)
                beam_rct = beam_img_original.get_rect()
                beam_rct.centerx = x
                beam_rct.centery = y
                beams.append({
                    'rct': beam_rct,
                    'state': 'spawned',
                    'spawn_time': tmr,
                    'vx': 0,
                    'vy': 0,
                    'img': beam_img_original
                })
                next_beam_time = tmr + 25
        

            # ビーム更新
            for beam in beams[:]:
                if beam['state'] == 'spawned':
                    if tmr - beam['spawn_time'] > 25:  # 0.5秒後発射
                        vx, vy = calc_orientation(beam['rct'], kk_rct, (0,0))
                        # ビーム速度3倍
                        vx *= 2.7
                        vy *= 2.7
                        beam['vx'] = vx
                        beam['vy'] = vy
                        beam['img'] = rotate_towards(kk_rct, beam['rct'], beam['img'])
                        beam['state'] = 'fired'

                if beam['state'] == 'fired':
                    beam['rct'].move_ip(beam['vx'], beam['vy'])

                screen.blit(beam['img'], beam['rct'])

                # 当たり判定（無敵中は受けない）
                if flash_counter == 0:
                    kk_mask = pg.mask.from_surface(current_kk_img)
                    beam_mask = pg.mask.from_surface(beam['img'])
                    offset = (beam['rct'].x - kk_rct.x, beam['rct'].y - kk_rct.y)
                    if kk_mask.overlap(beam_mask, offset):
                        player_hp = max(player_hp - 10, 0)
                        beams.remove(beam)
                        flash_counter = 100
                        continue

                # 画面外に出たビーム除去
                if (beam['rct'].right < 0 or beam['rct'].left > WIDTH or
                    beam['rct'].bottom < 0 or beam['rct'].top > HEIGHT):
                    beams.remove(beam)


        if player_hp <= 0:
            gameover(screen)
            return player_hp, enemy_hp

        if flash_counter > 0:
            flash_counter -= 1
            if (flash_counter // 5) % 2 == 0:
                screen.blit(current_kk_img, kk_rct)
        else:
            screen.blit(current_kk_img, kk_rct)

        draw_hp_gauge(screen, player_hp)
        pg.display.update()
        tmr += 1
        clock.tick(50)



# 補助関数
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    指定された矩形 (org) からターゲット矩形 (dst) に向かう方向ベクトルを計算する。

    Args:
        org (pg.Rect): 発射元の矩形。
        dst (pg.Rect): ターゲットの矩形。
        current_xy (tuple[float, float]): 現在の位置（未使用）。

    Returns:
        tuple[float, float]: 正規化された方向ベクトル (vx, vy)。
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx**2 + dy**2)
    if norm != 0:
        vx = dx / norm * 5
        vy = dy / norm * 5
    else:
        vx, vy = 0, 0
    return vx, vy

def rotate_towards(target: pg.Rect, source: pg.Rect, image: pg.Surface) -> pg.Surface:
    """
    指定されたターゲット (target) に向かうように、画像 (image) を回転させる。

    Args:
        target (pg.Rect): ターゲットの矩形。
        source (pg.Rect): 発射元の矩形。
        image (pg.Surface): 回転させる画像。

    Returns:
        pg.Surface: 回転させた画像。
    """
    dx = target.centerx - source.centerx
    dy = target.centery - source.centery
    angle = math.degrees(math.atan2(-dy, dx))
    rotated_img = pg.transform.rotozoom(image, angle, 1)
    return rotated_img

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def random_non_overlapping_position(kk_rct: pg.Rect, size: int) -> tuple[int, int]:
    while True:
        x = random.randint(size // 2, WIDTH - size // 2)
        y = random.randint(size // 2, HEIGHT - size // 2)
        new_rect = pg.Rect(x - size // 2, y - size // 2, size, size)
        if not kk_rct.colliderect(new_rect):
            return x, y
def victory(screen):
    font = pg.font.SysFont("msgothic", 80)
    text = font.render("卒業おめでとう", True, (0, 255, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)
    pg.display.update()
    pg.time.wait(5000)
    pg.quit()
    sys.exit()

def gameover(screen: pg.Surface) -> None:
    font = pg.font.SysFont("msgothic", 80)
    text = font.render("留年確定", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rect)
    pg.display.update()
    pg.time.wait(5000)
    pg.quit()
    sys.exit()

def draw_hp_gauge(screen: pg.Surface, hp: int, x=20, y=20):
    """
    HPゲージを描画する関数。

    Args:
        screen (pg.Surface): 描画対象の画面。
        hp (int): 現在のHP（0～100）。
        x (int): ゲージの描画位置のX座標。
        y (int): ゲージの描画位置のY座標。
    """
    gauge_width = 200
    gauge_height = 20
    fill_width = int((hp / 100) * gauge_width)
    pg.draw.rect(screen, (255, 255, 255), (x, y, gauge_width, gauge_height), 2)
    pg.draw.rect(screen, (0, 255, 0), (x, y, fill_width, gauge_height))


# メインループ
if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    start_screen(screen)
    player_hp = 100
    enemy_hp = 100

    while True:
        mode, player_hp, enemy_hp = mode_selection_screen(screen, player_hp, enemy_hp)
        if mode == "attack":
            player_hp, enemy_hp = post_attack_game(screen, player_hp, enemy_hp)
        elif mode == "evade":
            break

    pg.quit()
    sys.exit()
