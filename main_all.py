import os
import random
import sys
import math
import pygame

from UI.pause import PauseMenu
from movement.will_move import PlayerRunner as WillRunner
from obstacle import ObstacleManager
from UI.game_over import AestheticHorrorGameOver

# --- HIGH SCORE MANAGER IMPORT ---
try:
    from UI.high_score_mngr import save_high_score
except ImportError:
    from high_score_mngr import save_high_score

# --- CHARACTER SELECTION ROUTING ---
try:
    from movement.mike_move import PlayerRunner as MikeRunner
except ImportError:
    MikeRunner = WillRunner

try:
    from movement.eleven_move import PlayerRunner as ElevenRunner
except ImportError:
    ElevenRunner = WillRunner

try:
    from movement.dustin_move import PlayerRunner as DustinRunner
except ImportError:
    DustinRunner = WillRunner

try:
    from movement.lucas_move import PlayerRunner as LucasRunner
except ImportError:
    LucasRunner = WillRunner

CHARACTER_CLASSES = {
    "WILL": WillRunner,
    "MIKE": MikeRunner,
    "ELEVEN": ElevenRunner,
    "DUSTIN": DustinRunner,
    "LUCAS": LucasRunner,
}

# --- EXTERNAL WORD BANK LOADER FROM ROOT DIRECTORY (WORDS.txt) ---
WORD_BANK = ["RUN", "GATE", "ELEVEN", "HAWKINS", "UPSIDE", "DOWN", "VECNA"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WORDS_FILE_PATH = os.path.join(BASE_DIR, "WORDS.txt")
if not os.path.exists(WORDS_FILE_PATH):
    WORDS_FILE_PATH = os.path.join(BASE_DIR, "words.txt")

if os.path.exists(WORDS_FILE_PATH):
    try:
        with open(WORDS_FILE_PATH, "r", encoding="utf-8") as f:
            file_words = [line.strip().upper() for line in f if line.strip()]
            if file_words:
                WORD_BANK = file_words
                print(f"Successfully loaded {len(WORD_BANK)} aesthetic words from {os.path.basename(WORDS_FILE_PATH)}!")
    except Exception as err:
        print("WORDS.txt load nahi ho saka, fallback words use ho rahe hain:", err)


# --- SHARD / PARTICLE EFFECT FOR BREAKING OBSTACLES ---
class ShardParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(4, 10)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 4)
        self.color = random.choice([
            (255, 50, 50),
            (255, 140, 0),
            (200, 20, 20),
            (255, 215, 0),
            (180, 180, 200)
        ])
        self.alpha = 255
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
        self.alpha = max(0, int((self.life / 40) * 255))

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill((*self.color, self.alpha))
            surface.blit(s, (int(self.x), int(self.y)))


def run(volume=5, muted=False, selected_character="WILL"):
    pygame.init()

    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Audio initialization failed: {e}")

    actual_volume = 0.0 if muted else max(0.0, min(1.0, volume / 10.0))

    DISP_WIDTH, DISP_HEIGHT = 1280, 720
    WIDTH, HEIGHT = 800, 600

    screen = pygame.display.set_mode((DISP_WIDTH, DISP_HEIGHT))
    pygame.display.set_caption("Stranger Things - Runner")

    clock = pygame.time.Clock()
    game_surface = pygame.Surface((WIDTH, HEIGHT))

    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    track_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # --- UI INITIALIZATION ---
    game_over_ui = AestheticHorrorGameOver(WIDTH, HEIGHT)
    pause_menu = PauseMenu(DISP_WIDTH, DISP_HEIGHT)

    # --- ASSETS ---
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    BG_PATH = os.path.join(ASSETS_DIR, "BG2.jpeg")

    try:
        background = pygame.image.load(BG_PATH).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except (pygame.error, OSError) as e:
        print(f"Error loading background: {BG_PATH}\n{e}")
        pygame.quit()
        return

    # --- HORROR FONT SYSTEM LOADER ---
    HORROR_FONT_PATH = os.path.join(ASSETS_DIR, "horror.ttf")

    def get_font(size):
        if os.path.exists(HORROR_FONT_PATH):
            try:
                return pygame.font.Font(HORROR_FONT_PATH, size)
            except Exception:
                pass
        return pygame.font.SysFont("Impact", size)

    font_title = get_font(72)
    font_hud = get_font(24)
    font_word = get_font(18)
    font_power = get_font(11)
    font_popout = get_font(38)

    # --- COIN PNG ASSET LOADING ---
    coin_img_original = None
    COIN_PNG_PATH = os.path.join(ASSETS_DIR, "coin.png")

    if os.path.exists(COIN_PNG_PATH):
        try:
            coin_img_original = pygame.image.load(COIN_PNG_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Could not load coin image: {e}")

    # ==========================================================
    # BACKGROUND ZOOM & TRUE 3D TRACK MOTION
    # ==========================================================
    ZOOM_CYCLE_SECONDS = 3.0
    MAX_ZOOM = 1.30
    CROSSFADE_START = 0.80

    background_start_ticks = pygame.time.get_ticks()
    track_offset = 0.0

    def draw_animated_background(surface, current_speed_factor):
        cycle_time = ZOOM_CYCLE_SECONDS / current_speed_factor
        elapsed = (pygame.time.get_ticks() - background_start_ticks) / 1000.0
        phase = (elapsed % cycle_time) / cycle_time

        zoom = 1.0 + (MAX_ZOOM - 1.0) * phase

        scaled_width = int(WIDTH * zoom)
        scaled_height = int(HEIGHT * zoom)

        scaled_bg = pygame.transform.smoothscale(background, (scaled_width, scaled_height))

        x = (WIDTH - scaled_width) // 2
        y = (HEIGHT - scaled_height) // 2

        surface.blit(scaled_bg, (x, y))

        if phase >= CROSSFADE_START:
            fade_progress = (phase - CROSSFADE_START) / (1.0 - CROSSFADE_START)
            fade_progress = fade_progress * fade_progress * (3.0 - 2.0 * fade_progress)

            fade_surface.fill((0, 0, 0, 0))
            fade_surface.blit(background, (0, 0))
            fade_surface.set_alpha(int(255 * fade_progress))

            surface.blit(fade_surface, (0, 0))

    def draw_track_motion(surface, dt, speed_factor, screen_lanes, horizon_y):
        nonlocal track_offset
        track_offset += dt * 0.002 * speed_factor

        if track_offset >= 1.0:
            track_offset -= 1.0

        track_surface.fill((0, 0, 0, 0))

        # 1. Draw Perspective Lane Divider Lines (Converging from horizon to screen bottom)
        if len(screen_lanes) >= 3:
            pygame.draw.line(track_surface, (60, 40, 80), (screen_lanes[0]["top_x"], horizon_y),
                             (screen_lanes[0]["bottom_x"], HEIGHT), 3)
            pygame.draw.line(track_surface, (60, 40, 80), (screen_lanes[2]["top_x"], horizon_y),
                             (screen_lanes[2]["bottom_x"], HEIGHT), 3)

            div1_top = (screen_lanes[0]["top_x"] + screen_lanes[1]["top_x"]) // 2
            div1_bot = (screen_lanes[0]["bottom_x"] + screen_lanes[1]["bottom_x"]) // 2
            pygame.draw.line(track_surface, (40, 30, 60), (div1_top, horizon_y), (div1_bot, HEIGHT), 2)

            div2_top = (screen_lanes[1]["top_x"] + screen_lanes[2]["top_x"]) // 2
            div2_bot = (screen_lanes[1]["bottom_x"] + screen_lanes[2]["bottom_x"]) // 2
            pygame.draw.line(track_surface, (40, 30, 60), (div2_top, horizon_y), (div2_bot, HEIGHT), 2)

        # 2. Draw Moving Speed Cross-Bars (Rushing towards player)
        for i in range(10):
            prog = (track_offset + (i * 0.1)) % 1.0
            prog_curved = prog ** 2.2

            y_pos = int(horizon_y + (HEIGHT - horizon_y) * prog_curved)
            alpha = int(200 * prog_curved)

            x_left = int(
                screen_lanes[0]["top_x"] + (screen_lanes[0]["bottom_x"] - screen_lanes[0]["top_x"]) * prog_curved)
            x_right = int(
                screen_lanes[2]["top_x"] + (screen_lanes[2]["bottom_x"] - screen_lanes[2]["top_x"]) * prog_curved)

            thickness = max(1, int(1 + 3 * prog_curved))

            s_line = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(
                s_line,
                (180, 50, 70, alpha),
                (x_left, y_pos),
                (x_right, y_pos),
                thickness
            )
            surface.blit(s_line, (0, 0))

    # ==========================================================
    # BATTERY INDICATOR
    # ==========================================================
    MAX_LIVES = 5

    def draw_battery(surface, lives):
        battery_x = WIDTH - 100
        battery_y = 65
        battery_w = 84
        battery_h = 25

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            (battery_x, battery_y, battery_w, battery_h),
            2,
            border_radius=4,
        )

        pygame.draw.rect(
            surface,
            (220, 220, 220),
            (battery_x + battery_w, battery_y + 7, 5, 11),
            border_radius=2,
        )

        padding = 4
        gap = 3

        segment_w = (battery_w - 2 * padding - 4 * gap) // MAX_LIVES
        segment_h = battery_h - 2 * padding

        for i in range(MAX_LIVES):
            segment_x = battery_x + padding + i * (segment_w + gap)
            segment_y = battery_y + padding

            color = (60, 230, 100) if i < lives else (75, 75, 75)

            pygame.draw.rect(
                surface,
                color,
                (segment_x, segment_y, segment_w, segment_h),
                border_radius=2,
            )

    # ==========================================================
    # HEART HEALTH INDICATOR
    # ==========================================================
    def draw_health_heart(surface, health):
        heart_x = WIDTH - 94
        heart_y = 100
        heart_w = 32
        heart_h = 30

        health = max(0, min(100, health))

        points = [
            (heart_w // 2, heart_h - 1),
            (2, 12),
            (2, 8),
            (5, 3),
            (10, 1),
            (heart_w // 2, 8),
            (heart_w - 10, 1),
            (heart_w - 5, 3),
            (heart_w - 2, 8),
            (heart_w - 2, 12),
        ]

        heart_surface = pygame.Surface((heart_w, heart_h), pygame.SRCALPHA)
        pygame.draw.polygon(heart_surface, (65, 25, 30), points)

        fill_height = int(heart_h * health / 100)

        if fill_height > 0:
            previous_clip = heart_surface.get_clip()
            heart_surface.set_clip(
                pygame.Rect(0, heart_h - fill_height, heart_w, fill_height)
            )
            pygame.draw.polygon(heart_surface, (235, 35, 55), points)
            heart_surface.set_clip(previous_clip)

        pygame.draw.polygon(heart_surface, (255, 205, 210), points, 2)
        surface.blit(heart_surface, (heart_x, heart_y))

        health_font = get_font(20)
        health_text = health_font.render(f"{health}%", True, (255, 255, 255))
        surface.blit(health_text, (heart_x + 38, heart_y + 4))

    # ==========================================================
    # WORD HUNTING & POWER BOX UI DRAWING
    # ==========================================================
    def draw_word_hunt(surface, current_word, collected_indices):
        start_x = 10
        start_y = 55
        box_w, box_h = 24, 28

        for i, char in enumerate(current_word):
            x = start_x + i * (box_w + 4)
            is_collected = i in collected_indices

            bg_col = (220, 20, 30) if is_collected else (30, 30, 45)
            border_col = (255, 80, 80) if is_collected else (90, 90, 110)

            pygame.draw.rect(surface, bg_col, (x, start_y, box_w, box_h), border_radius=4)
            pygame.draw.rect(surface, border_col, (x, start_y, box_w, box_h), 2, border_radius=4)

            txt_col = (255, 255, 255) if is_collected else (120, 120, 140)
            lbl = font_word.render(char, True, txt_col)
            surface.blit(lbl, lbl.get_rect(center=(x + box_w // 2, start_y + box_h // 2)))

    def draw_power_box(surface, has_power):
        box_x = WIDTH - 165
        box_y = 65
        box_w, box_h = 55, 55

        bg_col = (180, 30, 40) if has_power else (25, 25, 35)
        border_col = (255, 215, 0) if has_power else (80, 80, 100)

        pygame.draw.rect(surface, bg_col, (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(surface, border_col, (box_x, box_y, box_w, box_h), 3, border_radius=8)

        if has_power:
            pygame.draw.circle(surface, (255, 255, 255), (box_x + box_w // 2, box_y + box_h // 2), 16)
            lbl = font_word.render("11", True, (200, 10, 20))
            surface.blit(lbl, lbl.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2)))

            sub_lbl = font_power.render("[PRESS E]", True, (255, 215, 0))
            surface.blit(sub_lbl, sub_lbl.get_rect(center=(box_x + box_w // 2, box_y + box_h + 12)))
        else:
            lbl = font_power.render("EMPTY", True, (100, 100, 120))
            surface.blit(lbl, lbl.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2)))

    # --- CENTER POP-OUT BUBBLE NOTIFICATION FOR WORD COMPLETED ---
    def draw_center_word_popout(surface, word, timer):
        if timer <= 0:
            return

        total_frames = 100
        progress = (total_frames - timer) / total_frames

        scale_factor = 1.0 + 0.25 * math.sin(progress * math.pi)

        raw_txt = font_popout.render(f"{word} COMPLETED! (+20)", True, (255, 215, 0))
        w = int(raw_txt.get_width() * scale_factor)
        h = int(raw_txt.get_height() * scale_factor)
        scaled_txt = pygame.transform.smoothscale(raw_txt, (max(1, w), max(1, h)))

        center_x = WIDTH // 2
        center_y = HEIGHT // 2 - 60
        txt_rect = scaled_txt.get_rect(center=(center_x, center_y))

        bg_rect = txt_rect.inflate(40, 20)
        bubble_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)

        alpha = max(0, min(230, int((timer / total_frames) * 255)))
        pygame.draw.rect(bubble_surface, (25, 15, 35, alpha), bubble_surface.get_rect(), border_radius=16)
        pygame.draw.rect(bubble_surface, (255, 50, 50, alpha), bubble_surface.get_rect(), 3, border_radius=16)

        surface.blit(bubble_surface, bg_rect)
        scaled_txt.set_alpha(alpha)
        surface.blit(scaled_txt, txt_rect)

    # ==========================================================
    # MUSIC
    # ==========================================================
    if pygame.mixer.get_init():
        for extension in [".mp3", ".mpeg", ".ogg"]:
            music_path = os.path.join(ASSETS_DIR, f"S2{extension}")

            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(actual_volume)
                    pygame.mixer.music.play(-1)
                    break
                except pygame.error as e:
                    print(f"Could not play music: {e}")

    # ==========================================================
    # GAME INITIALIZATION
    # ==========================================================
    speed_factor = 1.0
    DIFFICULTY_RATE = 0.002
    MAX_SPEED_FACTOR = 2.2

    char_class = CHARACTER_CLASSES.get(selected_character.upper(), WillRunner)

    player_runner = char_class(WIDTH, HEIGHT)
    obstacle_manager = ObstacleManager(WIDTH, HEIGHT)

    LANE_RATIOS = [
        {"top_x": 0.435, "bottom_x": 0.16, "top_y": 0.38},  # Left
        {"top_x": 0.498, "bottom_x": 0.475, "top_y": 0.38},  # Center
        {"top_x": 0.565, "bottom_x": 0.80, "top_y": 0.38},  # Right
    ]

    coins_collected = 0
    coins_list = []
    coin_spawn_timer = 0
    current_guide_lane = random.choice([0, 1, 2])

    # --- WORD HUNTING & POWERUP STATE ---
    current_target_word = random.choice(WORD_BANK)
    collected_indices = []
    letters_list = []
    letter_spawn_timer = 0

    has_telekinesis = False
    powerups_list = []
    powerup_spawn_timer = 0

    shards_list = []
    completed_popout_timer = 0
    last_completed_word = ""

    # Initial Coin Trail Spawn
    for i in range(5):
        coins_list.append({
            "lane": current_guide_lane,
            "progress": 0.15 + (i * 0.08),
            "y_offset": 0.0
        })

    lives_remaining = MAX_LIVES
    health_percentage = 100
    collision_active = False

    # ==========================================================
    # COUNTDOWN
    # ==========================================================
    countdown_steps = ["3", "2", "1", "START!"]

    for step in countdown_steps:
        start_ticks = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_ticks < 1000:
            game_surface.fill((0, 0, 0))
            draw_animated_background(game_surface, 1.0)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            game_surface.blit(overlay, (0, 0))

            count_surf = font_title.render(step, True, (255, 50, 50))
            count_rect = count_surf.get_rect(center=(WIDTH // 2, (HEIGHT // 2) - 20))
            game_surface.blit(count_surf, count_rect)

            scaled_display = pygame.transform.scale(
                game_surface, (DISP_WIDTH, DISP_HEIGHT)
            )
            screen.blit(scaled_display, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    background_start_ticks = pygame.time.get_ticks()

    # ==========================================================
    # MAIN LOOP
    # ==========================================================
    running = True
    paused = False
    game_over = False
    frozen_snapshot = None

    pause_button_rect = pygame.Rect(WIDTH - 55, 15, 40, 40)

    while running:
        dt = clock.tick(60)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and has_telekinesis and not game_over and not paused:
                    has_telekinesis = False

                    for obs in obstacle_manager.obstacles:
                        obs_x = getattr(obs, 'x', WIDTH // 2)
                        obs_y = getattr(obs, 'y', HEIGHT // 2)
                        for _ in range(35):
                            shards_list.append(ShardParticle(obs_x, obs_y))

                    obstacle_manager.obstacles.clear()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                logic_mx = int(mx * (WIDTH / DISP_WIDTH))
                logic_my = int(my * (HEIGHT / DISP_HEIGHT))

                if pause_button_rect.collidepoint((logic_mx, logic_my)) and not game_over:
                    paused = True

            # --- GAME OVER INPUT HANDLING ---
            if game_over:
                event_copy = event
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                    mx, my = event.pos
                    logic_mx = int(mx * (WIDTH / DISP_WIDTH))
                    logic_my = int(my * (HEIGHT / DISP_HEIGHT))

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        event_copy = pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN,
                            {"button": event.button, "pos": (logic_mx, logic_my)},
                        )

                action = game_over_ui.handle_input(event_copy)

                if action == "restart":
                    game_over = False
                    paused = False
                    frozen_snapshot = None

                    obstacle_manager.obstacles.clear()
                    coins_list.clear()
                    letters_list.clear()
                    powerups_list.clear()
                    shards_list.clear()

                    collected_indices.clear()
                    current_target_word = random.choice(WORD_BANK)
                    has_telekinesis = False
                    completed_popout_timer = 0

                    current_guide_lane = random.choice([0, 1, 2])
                    for i in range(5):
                        coins_list.append({
                            "lane": current_guide_lane,
                            "progress": 0.15 + (i * 0.08),
                            "y_offset": 0.0
                        })

                    coins_collected = 0
                    coin_spawn_timer = 0
                    letter_spawn_timer = 0
                    powerup_spawn_timer = 0
                    speed_factor = 1.0

                    lives_remaining = MAX_LIVES
                    health_percentage = 100
                    collision_active = False

                    background_start_ticks = pygame.time.get_ticks()

                    if pygame.mixer.get_init():
                        try:
                            pygame.mixer.music.play(-1)
                            pygame.mixer.music.set_volume(actual_volume)
                        except pygame.error as e:
                            print(f"Error resetting music: {e}")

                # --- ROUTING TO MAIN MENU PAGE ---
                elif action in ["menu", "quit"]:
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()

                    try:
                        from UI.menu_pg import MainMenu
                        main_menu = MainMenu(screen)
                        main_menu.run()
                    except ImportError:
                        try:
                            from menu_pg import MainMenu
                            main_menu = MainMenu(screen)
                            main_menu.run()
                        except Exception as e:
                            print(f"Menu load error: {e}")
                    except Exception as e:
                        print(f"Could not load UI.menu_pg: {e}")

                    running = False
                    return

        # ======================================================
        # PAUSE MENU
        # ======================================================
        if paused:
            action = pause_menu.run(
                screen,
                coins_collected,
                clock,
                DISP_WIDTH,
                DISP_HEIGHT,
                game_surface,
            )

            if action == "RESUME":
                paused = False

            elif action == "RESTART":
                game_over = False
                paused = False
                frozen_snapshot = None

                obstacle_manager.obstacles.clear()
                coins_list.clear()
                letters_list.clear()
                powerups_list.clear()
                shards_list.clear()

                collected_indices.clear()
                current_target_word = random.choice(WORD_BANK)
                has_telekinesis = False
                completed_popout_timer = 0

                current_guide_lane = random.choice([0, 1, 2])
                for i in range(5):
                    coins_list.append({
                        "lane": current_guide_lane,
                        "progress": 0.15 + (i * 0.08),
                        "y_offset": 0.0
                    })

                coins_collected = 0
                coin_spawn_timer = 0
                letter_spawn_timer = 0
                powerup_spawn_timer = 0
                speed_factor = 1.0

                lives_remaining = MAX_LIVES
                health_percentage = 100
                collision_active = False

                background_start_ticks = pygame.time.get_ticks()

                if pygame.mixer.get_init():
                    try:
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(actual_volume)
                    except pygame.error as e:
                        print(f"Error resetting music: {e}")

            # --- QUIT FROM PAUSE REDIRECTS TO MAIN MENU ---
            elif action == "QUIT":
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()

                try:
                    from UI.menu_pg import MainMenu
                    main_menu = MainMenu(screen)
                    main_menu.run()
                except ImportError:
                    try:
                        from menu_pg import MainMenu
                        main_menu = MainMenu(screen)
                        main_menu.run()
                    except Exception as e:
                        print(f"Menu load error: {e}")
                except Exception as e:
                    print(f"Could not load UI.menu_pg from pause menu: {e}")

                running = False
                return

            continue

        game_surface.fill((0, 0, 0))

        # ======================================================
        # ACTIVE GAMEPLAY
        # ======================================================
        if not game_over:
            speed_factor = min(
                MAX_SPEED_FACTOR, speed_factor + DIFFICULTY_RATE * (dt / 1000.0)
            )

            screen_lanes = []
            horizon_y_screen = 0

            for ratio in LANE_RATIOS:
                top_x_screen = int(ratio["top_x"] * WIDTH)
                bottom_x_screen = int(ratio["bottom_x"] * WIDTH)
                top_y_screen = int(ratio["top_y"] * HEIGHT)

                screen_lanes.append(
                    {"top_x": top_x_screen, "bottom_x": bottom_x_screen}
                )
                horizon_y_screen = top_y_screen

            obstacle_manager.lane_positions = screen_lanes
            obstacle_manager.HORIZON_Y = horizon_y_screen

            if hasattr(player_runner, "lane_positions"):
                player_runner.lane_positions = screen_lanes

            obstacle_manager.update_and_spawn(dt * speed_factor)
            player_runner.update(events)

            # --- SINGLE LANE GUIDED COIN TRAIL ---
            coin_spawn_timer += dt

            if coin_spawn_timer > (1200 / speed_factor) and len(coins_list) == 0:
                coin_spawn_timer = 0
                current_guide_lane = random.choice([0, 1, 2])

                for i in range(5):
                    coins_list.append({
                        "lane": current_guide_lane,
                        "progress": 0.0 + (i * 0.08),
                        "y_offset": 0.0
                    })

            # --- WORD HUNTING LETTER SPAWNING FROM WORDS.TXT ---
            letter_spawn_timer += dt
            if letter_spawn_timer > 5000:
                letter_spawn_timer = 0
                uncollected_indices = [i for i in range(len(current_target_word)) if i not in collected_indices]
                if uncollected_indices:
                    chosen_idx = random.choice(uncollected_indices)
                    letters_list.append({
                        "char": current_target_word[chosen_idx],
                        "index": chosen_idx,
                        "lane": random.choice([0, 1, 2]),
                        "progress": 0.0
                    })

            # --- TELEKINESIS POWERUP SPAWNING ---
            powerup_spawn_timer += dt
            if powerup_spawn_timer > 15000 and not has_telekinesis and len(powerups_list) == 0:
                powerup_spawn_timer = 0
                powerups_list.append({
                    "lane": random.choice([0, 1, 2]),
                    "progress": 0.0
                })

            # --- MOVEMENTS ---
            for coin in coins_list[:]:
                coin["progress"] += dt * 0.0006 * speed_factor

                if coin["progress"] >= 1.0:
                    coins_list.remove(coin)

            for item in letters_list[:]:
                item["progress"] += dt * 0.0006 * speed_factor

                if item["progress"] >= 1.0:
                    letters_list.remove(item)

            for item in powerups_list[:]:
                item["progress"] += dt * 0.0006 * speed_factor

                if item["progress"] >= 1.0:
                    powerups_list.remove(item)

            # --- UPDATE SHARDS ---
            for shard in shards_list[:]:
                shard.update()
                if shard.life <= 0:
                    shards_list.remove(shard)

            player_rect = (
                player_runner.get_rect()
                if hasattr(player_runner, "get_rect")
                else pygame.Rect(player_runner.x, player_runner.y, 130, 130)
            )

            # --- DRAWING OBJECTS ---
            draw_animated_background(game_surface, speed_factor)
            draw_track_motion(game_surface, dt, speed_factor, screen_lanes, horizon_y_screen)
            obstacle_manager.draw(game_surface)

            # --- DRAW EXPLODING SHARDS ---
            for shard in shards_list:
                shard.draw(game_surface)

            # --- COIN 3D PERSPECTIVE RENDERING & COLLISION ---
            for coin in coins_list[:]:
                if coin["progress"] < 0:
                    continue

                lane_idx = coin["lane"]
                prog = coin["progress"] ** 2.2  # Exact 3D track depth curve match
                lane_data = screen_lanes[lane_idx]

                cx = int(lane_data["top_x"] + (lane_data["bottom_x"] - lane_data["top_x"]) * prog)
                cy = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog)

                c_radius = int(6 + 18 * prog)
                coin_size = max(1, c_radius * 2)

                if coin_img_original:
                    scaled_coin = pygame.transform.smoothscale(coin_img_original, (coin_size, coin_size))
                    game_surface.blit(scaled_coin, (cx - c_radius, cy - c_radius))
                else:
                    pygame.draw.circle(game_surface, (255, 215, 0), (cx, cy), c_radius)
                    pygame.draw.circle(game_surface, (180, 130, 0), (cx, cy), c_radius, 2)

                coin_rect = pygame.Rect(cx - c_radius, cy - c_radius, coin_size, coin_size)

                if player_rect.colliderect(coin_rect):
                    coins_collected += 1
                    coins_list.remove(coin)

            # --- LETTER 3D PERSPECTIVE RENDERING & COLLISION ---
            for item in letters_list[:]:
                lane_idx = item["lane"]
                prog = item["progress"] ** 2.2
                lane_data = screen_lanes[lane_idx]

                cx = int(lane_data["top_x"] + (lane_data["bottom_x"] - lane_data["top_x"]) * prog)
                cy = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog)

                radius = int(8 + 20 * prog)

                letter_rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

                pygame.draw.circle(game_surface, (220, 20, 30), (cx, cy), radius)
                pygame.draw.circle(game_surface, (255, 255, 255), (cx, cy), radius, 2)

                let_txt = font_hud.render(item["char"], True, (255, 255, 255))
                game_surface.blit(let_txt, let_txt.get_rect(center=(cx, cy)))

                if player_rect.colliderect(letter_rect):
                    if item["index"] not in collected_indices:
                        collected_indices.append(item["index"])

                        if len(collected_indices) == len(current_target_word):
                            coins_collected += 20
                            last_completed_word = current_target_word
                            collected_indices.clear()
                            current_target_word = random.choice(WORD_BANK)
                            completed_popout_timer = 100

                    letters_list.remove(item)

            # --- POWERUP 3D PERSPECTIVE RENDERING & COLLISION ---
            for item in powerups_list[:]:
                lane_idx = item["lane"]
                prog = item["progress"] ** 2.2
                lane_data = screen_lanes[lane_idx]

                cx = int(lane_data["top_x"] + (lane_data["bottom_x"] - lane_data["top_x"]) * prog)
                cy = int(horizon_y_screen + (HEIGHT - horizon_y_screen) * prog)

                radius = int(10 + 22 * prog)

                pw_rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)

                pygame.draw.circle(game_surface, (255, 215, 0), (cx, cy), radius)
                pygame.draw.circle(game_surface, (200, 10, 20), (cx, cy), radius - 3)

                pw_txt = font_hud.render("11", True, (255, 255, 255))
                game_surface.blit(pw_txt, pw_txt.get_rect(center=(cx, cy)))

                if player_rect.colliderect(pw_rect):
                    has_telekinesis = True
                    powerups_list.remove(item)

            # --- PLAYER DRAWING ---
            player_runner.draw(game_surface)

            # --- COLLISION LOGIC ---
            collision_now = obstacle_manager.check_collision(player_runner)

            if collision_now and not collision_active:
                lives_remaining = max(0, lives_remaining - 1)
                health_percentage = int((lives_remaining / MAX_LIVES) * 100)
                collision_active = True

                if lives_remaining == 0:
                    game_over = True

                    try:
                        save_high_score(coins_collected)
                    except Exception as err:
                        print("High score save fail:", err)

                    frozen_snapshot = game_surface.copy()

                    if pygame.mixer.get_init():
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()

            elif not collision_now:
                collision_active = False

            # --- TIMER DECREMENT & CENTER POPOUT RENDER ---
            if completed_popout_timer > 0:
                completed_popout_timer -= 1
                draw_center_word_popout(game_surface, last_completed_word, completed_popout_timer)

            # --- HUD COIN COUNTER ---
            if coin_img_original:
                hud_coin = pygame.transform.smoothscale(coin_img_original, (32, 32))
                game_surface.blit(hud_coin, (10, 10))
            else:
                pygame.draw.circle(game_surface, (255, 215, 0), (25, 25), 14)
                pygame.draw.circle(game_surface, (180, 130, 0), (25, 25), 14, 2)

            coin_label = font_hud.render(
                f"x {coins_collected}", True, (255, 255, 255)
            )
            game_surface.blit(coin_label, (48, 15))

            # --- PAUSE BUTTON ---
            pygame.draw.rect(
                game_surface, (30, 30, 45), pause_button_rect, border_radius=6
            )
            pygame.draw.rect(
                game_surface,
                (200, 50, 50),
                pause_button_rect,
                2,
                border_radius=6,
            )

            game_surface.blit(
                font_hud.render("||", True, (255, 255, 255)),
                (pause_button_rect.x + 11, pause_button_rect.y + 7),
            )

            # --- HUD DRAWINGS ---
            draw_battery(game_surface, lives_remaining)
            draw_health_heart(game_surface, health_percentage)
            draw_word_hunt(game_surface, current_target_word, collected_indices)
            draw_power_box(game_surface, has_telekinesis)

        # ======================================================
        # GAME OVER
        # ======================================================
        else:
            if frozen_snapshot is not None:
                game_surface.blit(frozen_snapshot, (0, 0))

            game_over_ui.draw(
                game_surface,
                final_score=coins_collected,
                max_lives=MAX_LIVES,
            )

        # --- SCALE AND DISPLAY ---
        scaled_display = pygame.transform.scale(
            game_surface, (DISP_WIDTH, DISP_HEIGHT)
        )

        screen.blit(scaled_display, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()