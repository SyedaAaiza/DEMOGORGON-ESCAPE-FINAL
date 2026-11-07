import importlib
import json
import os
import sys
import pygame

# --- COLOR PALETTE ---
COLOR_RED = (220, 20, 60)
COLOR_NEON_RED = (255, 45, 0)
COLOR_DARK_RED = (80, 0, 0)
COLOR_WHITE = (245, 245, 245)
COLOR_LIGHT_GRAY = (190, 190, 200)

# --- ALAG PLAYER DATA JSON LOADER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POSSIBLE_PLAYER_DATA_PATHS = [
    os.path.join(BASE_DIR, "player_data.json"),
    os.path.join(BASE_DIR, "..", "player_data.json"),
    os.path.join("player_data.json"),
]


def load_player_username():
    """Separate player_data.json file se name fetch karta hai."""
    for filepath in POSSIBLE_PLAYER_DATA_PATHS:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = (
                            data.get("player_name")
                            or data.get("username")
                            or data.get("name")
                    )
                    if name:
                        return str(name).upper()[:12]
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    return "PLAYER 01"


def load_selected_character():
    """JSON file se user ka saved character fetch karta hai."""
    for filepath in POSSIBLE_PLAYER_DATA_PATHS:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    char = (
                            data.get("selected_character")
                            or data.get("character")
                            or data.get("hero")
                    )
                    if char:
                        return str(char).upper()
            except Exception as e:
                print(f"Error reading {filepath} for character: {e}")
    return "WILL"  # Default fallback character


# ==========================================
# BUTTON CLASS (Fully Rounded / Pill Shape)
# ==========================================
class Button:

    def __init__(self, text, x, y, width, height, font, is_icon=False):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_icon = is_icon
        self.font = font

    def draw(self, surface):
        if self.is_hovered:
            border_color = COLOR_NEON_RED
            text_color = COLOR_WHITE
            bg_alpha = 200
        else:
            border_color = COLOR_DARK_RED
            text_color = COLOR_LIGHT_GRAY
            bg_alpha = 140

        btn_surface = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )
        radius = self.rect.height // 2
        pygame.draw.rect(
            btn_surface,
            (10, 10, 15, bg_alpha),
            (0, 0, self.rect.width, self.rect.height),
            border_radius=radius,
        )
        surface.blit(btn_surface, self.rect.topleft)

        pygame.draw.rect(
            surface, border_color, self.rect, width=3, border_radius=radius
        )

        if self.is_icon:
            cx, cy = self.rect.center
            offset = 8
            pygame.draw.line(
                surface,
                text_color,
                (cx - offset, cy - offset),
                (cx + offset, cy + offset),
                3,
            )
            pygame.draw.line(
                surface,
                text_color,
                (cx - offset, cy + offset),
                (cx + offset, cy - offset),
                3,
            )
        else:
            text_surf = self.font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def is_clicked(self, mouse_pos, event):
        return (
                self.is_hovered
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
        )


# ==========================================
# MAIN MENU CLASS
# ==========================================
class MainMenu:

    def __init__(self, screen, clock=None):
        self.screen = screen
        self.clock = clock if clock else pygame.time.Clock()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen.get_size()
        self.FPS = 60

        # --- FONT LOADING ---
        possible_font_paths = [
            os.path.join(
                os.path.dirname(__file__), "..", "assets", "horror_font.ttf"
            ),
            os.path.join(
                os.path.dirname(__file__), "..", "assets", "horror.ttf"
            ),
            os.path.join("assets", "horror_font.ttf"),
            os.path.join("assets", "horror.ttf"),
        ]

        self.FONT_BUTTON = None
        self.FONT_BODY = None

        for fpath in possible_font_paths:
            if os.path.exists(fpath):
                try:
                    self.FONT_BUTTON = pygame.font.Font(fpath, 22)
                    self.FONT_BODY = pygame.font.Font(fpath, 20)
                    break
                except Exception:
                    pass

        if not self.FONT_BUTTON:
            try:
                self.FONT_BUTTON = pygame.font.SysFont(
                    "chiller", 30, bold=True
                )
            except Exception:
                self.FONT_BUTTON = pygame.font.SysFont("impact", 24)

        if not self.FONT_BODY:
            self.FONT_BODY = pygame.font.SysFont("consolas", 22)

        self.FONT_COUNTDOWN = pygame.font.SysFont("impact", 120)
        self.FONT_USER = pygame.font.SysFont("georgia", 18, bold=True)

        # --- BACKGROUND LOADING ---
        BG_PATH = os.path.join(BASE_DIR, "..", "assets", "trees.jpeg")
        if not os.path.exists(BG_PATH):
            if os.path.exists(os.path.join("assets", "trees.jpeg")):
                BG_PATH = os.path.join("assets", "trees.jpeg")

        if os.path.exists(BG_PATH):
            self.base_bg = pygame.image.load(BG_PATH).convert()
            self.base_bg = pygame.transform.scale(
                self.base_bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            )
        else:
            self.base_bg = pygame.Surface(
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            )
            self.base_bg.fill((15, 10, 20))

        self.zoom_scale = 1.0
        self.zoom_direction = 1
        self.zoom_speed = 0.0006

        # --- LOAD SAVED SETTINGS FROM JSON ---
        self.sound_volume = 5
        self.music_muted = False
        self.sound_muted = False
        self.load_settings()

    def get_settings_filepath(self):
        for filepath in POSSIBLE_PLAYER_DATA_PATHS:
            if os.path.exists(filepath):
                return filepath
        return POSSIBLE_PLAYER_DATA_PATHS[0]

    def load_settings(self):
        """JSON file se volume aur mute states load karta hai."""
        filepath = self.get_settings_filepath()
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sound_volume = data.get("sound_volume", 5)
                    self.music_muted = data.get("music_muted", False)
                    self.sound_muted = data.get("sound_muted", False)
            except Exception as e:
                print(f"Error loading settings from JSON: {e}")

    def save_settings(self):
        """Current settings ko JSON file mein permanently save karta hai."""
        filepath = self.get_settings_filepath()
        data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

        data["sound_volume"] = self.sound_volume
        data["music_muted"] = self.music_muted
        data["sound_muted"] = self.sound_muted

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings to JSON: {e}")

    def draw_top_left_username(self):
        username = load_player_username()
        user_badge_w, user_badge_h = 230, 46
        user_x, user_y = 35, 30

        user_surf = pygame.Surface(
            (user_badge_w, user_badge_h), pygame.SRCALPHA
        )
        pygame.draw.rect(
            user_surf,
            (15, 8, 22, 210),
            (0, 0, user_badge_w, user_badge_h),
            border_radius=23,
        )
        pygame.draw.rect(
            user_surf,
            COLOR_NEON_RED,
            (0, 0, user_badge_w, user_badge_h),
            width=2,
            border_radius=23,
        )

        pygame.draw.circle(user_surf, COLOR_RED, (24, user_badge_h // 2), 10)
        pygame.draw.circle(user_surf, COLOR_WHITE, (24, user_badge_h // 2), 4)

        self.screen.blit(user_surf, (user_x, user_y))

        tag_lbl = self.FONT_BODY.render("AGENT:", True, (160, 150, 170))
        name_lbl = self.FONT_USER.render(username, True, COLOR_WHITE)

        self.screen.blit(tag_lbl, (user_x + 44, user_y + 5))
        self.screen.blit(name_lbl, (user_x + 44, user_y + 21))

    def show_warning_and_countdown(self):
        showing_warning = True
        start_btn = Button(
            "ENTER THE SHADOWS",
            self.SCREEN_WIDTH // 2 - 140,
            self.SCREEN_HEIGHT - 150,
            280,
            52,
            self.FONT_BUTTON,
        )

        while showing_warning:
            mouse_pos = pygame.mouse.get_pos()
            start_btn.check_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()
                if start_btn.is_clicked(mouse_pos, event) or (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN
                ):
                    showing_warning = False

            self.zoom_scale += self.zoom_speed * self.zoom_direction
            if self.zoom_scale >= 1.35:
                self.zoom_direction = -1
            elif self.zoom_scale <= 1.0:
                self.zoom_direction = 1

            current_w = int(self.SCREEN_WIDTH * self.zoom_scale)
            current_h = int(self.SCREEN_HEIGHT * self.zoom_scale)
            scaled_bg = pygame.transform.smoothscale(
                self.base_bg, (current_w, current_h)
            )

            bg_x = (self.SCREEN_WIDTH - current_w) // 2
            bg_y = (self.SCREEN_HEIGHT - current_h) // 2

            self.screen.blit(scaled_bg, (bg_x, bg_y))

            overlay = pygame.Surface(
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 215))
            self.screen.blit(overlay, (0, 0))

            title_surf = self.FONT_BUTTON.render(
                "WARNING: THE UPSIDE DOWN AWAITS", True, COLOR_RED
            )
            title_rect = title_surf.get_rect(
                center=(self.SCREEN_WIDTH // 2, int(self.SCREEN_HEIGHT * 0.22))
            )
            self.screen.blit(title_surf, title_rect)

            lines = [
                "You are about to cross into a dark, corrupted realm.",
                "Demogorgons and shadows lurk in the mist.",
                "Make sure your controls and defenses are ready.",
                "",
                "Press ENTER or click below to proceed...",
            ]

            for idx, line in enumerate(lines):
                line_surf = self.FONT_BODY.render(
                    line, True, COLOR_WHITE if idx == 4 else COLOR_LIGHT_GRAY
                )
                line_rect = line_surf.get_rect(
                    center=(
                        self.SCREEN_WIDTH // 2,
                        int(self.SCREEN_HEIGHT * 0.38) + idx * 45,
                    )
                )
                self.screen.blit(line_surf, line_rect)

            start_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        for count in [3, 2, 1]:
            start_ticks = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_ticks < 900:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                self.screen.blit(self.base_bg, (0, 0))
                overlay = pygame.Surface(
                    (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA
                )
                overlay.fill((0, 0, 0, 225))
                self.screen.blit(overlay, (0, 0))

                num_surf = self.FONT_COUNTDOWN.render(
                    str(count), True, COLOR_NEON_RED
                )
                num_rect = num_surf.get_rect(
                    center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
                )
                self.screen.blit(num_surf, num_rect)

                pygame.display.flip()
                self.clock.tick(self.FPS)

    def launch_main_game(self):
        self.show_warning_and_countdown()
        try:
            if "main" in sys.modules:
                del sys.modules["main"]
            import main

            # Load the saved character from JSON and pass it to main.run()
            selected_hero = load_selected_character()

            if hasattr(main, "run"):
                main.run(
                    volume=self.sound_volume,
                    muted=self.music_muted,
                    sound_muted=self.sound_muted,
                    selected_character=selected_hero,
                )
            elif hasattr(main, "main"):
                main.main()
        except ImportError as e:
            print(f"[ERROR] Could not import main.py: {e}")

    def launch_customization(self):
        try:
            if "custom" in sys.modules:
                del sys.modules["custom"]
            if "UI.custom" in sys.modules:
                del sys.modules["UI.custom"]

            try:
                from custom import CustomizationScreen

                custom_screen = CustomizationScreen(self.screen, self.clock)
                custom_screen.run()
            except ImportError:
                from UI.custom import CustomizationScreen

                custom_screen = CustomizationScreen(self.screen, self.clock)
                custom_screen.run()
        except Exception as e:
            print(f"[ERROR] Could not launch custom.py: {e}")

    def open_settings(self):
        in_settings = True

        back_btn = Button(
            "BACK TO MENU",
            self.SCREEN_WIDTH // 2 - 110,
            self.SCREEN_HEIGHT - 130,
            220,
            50,
            self.FONT_BUTTON,
        )
        vol_down_btn = Button(
            "-",
            self.SCREEN_WIDTH // 2 - 120,
            int(self.SCREEN_HEIGHT * 0.38),
            48,
            48,
            self.FONT_BUTTON,
        )
        vol_up_btn = Button(
            "+",
            self.SCREEN_WIDTH // 2 + 75,
            int(self.SCREEN_HEIGHT * 0.38),
            48,
            48,
            self.FONT_BUTTON,
        )

        music_mute_btn = Button(
            "MUSIC: ON",
            self.SCREEN_WIDTH // 2 - 125,
            int(self.SCREEN_HEIGHT * 0.52),
            250,
            48,
            self.FONT_BUTTON,
        )
        sound_mute_btn = Button(
            "SOUND FX: ON",
            self.SCREEN_WIDTH // 2 - 125,
            int(self.SCREEN_HEIGHT * 0.64),
            250,
            48,
            self.FONT_BUTTON,
        )

        while in_settings:
            music_mute_btn.text = "MUSIC: MUTED" if self.music_muted else "MUSIC: ON"
            sound_mute_btn.text = "SOUND FX: MUTED" if self.sound_muted else "SOUND FX: ON"

            mouse_pos = pygame.mouse.get_pos()
            for btn in [back_btn, vol_down_btn, vol_up_btn, music_mute_btn, sound_mute_btn]:
                btn.check_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE
                ):
                    in_settings = False

                if back_btn.is_clicked(mouse_pos, event):
                    in_settings = False

                if vol_down_btn.is_clicked(mouse_pos, event):
                    self.sound_volume = max(0, self.sound_volume - 1)
                    self.save_settings()

                if vol_up_btn.is_clicked(mouse_pos, event):
                    self.sound_volume = min(10, self.sound_volume + 1)
                    self.save_settings()

                if music_mute_btn.is_clicked(mouse_pos, event):
                    self.music_muted = not self.music_muted
                    self.save_settings()

                if sound_mute_btn.is_clicked(mouse_pos, event):
                    self.sound_muted = not self.sound_muted
                    self.save_settings()

            self.zoom_scale += self.zoom_speed * self.zoom_direction
            if self.zoom_scale >= 1.35:
                self.zoom_direction = -1
            elif self.zoom_scale <= 1.0:
                self.zoom_direction = 1

            current_w = int(self.SCREEN_WIDTH * self.zoom_scale)
            current_h = int(self.SCREEN_HEIGHT * self.zoom_scale)
            scaled_bg = pygame.transform.smoothscale(
                self.base_bg, (current_w, current_h)
            )

            bg_x = (self.SCREEN_WIDTH - current_w) // 2
            bg_y = (self.SCREEN_HEIGHT - current_h) // 2

            self.screen.blit(scaled_bg, (bg_x, bg_y))

            overlay = pygame.Surface(
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((5, 5, 12, 220))
            self.screen.blit(overlay, (0, 0))

            title = self.FONT_BUTTON.render("AUDIO SETTINGS", True, COLOR_RED)
            self.screen.blit(
                title,
                title.get_rect(
                    center=(self.SCREEN_WIDTH // 2, int(self.SCREEN_HEIGHT * 0.2))
                ),
            )

            vol_label = self.FONT_BODY.render(
                f"Master Volume:  [ {self.sound_volume} / 10 ]", True, COLOR_WHITE
            )
            self.screen.blit(
                vol_label,
                vol_label.get_rect(
                    center=(
                        self.SCREEN_WIDTH // 2,
                        int(self.SCREEN_HEIGHT * 0.33),
                    )
                ),
            )

            vol_down_btn.draw(self.screen)
            vol_up_btn.draw(self.screen)
            music_mute_btn.draw(self.screen)
            sound_mute_btn.draw(self.screen)
            back_btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.FPS)

    def run(self):
        btn_w, btn_h = 240, 50
        center_x = self.SCREEN_WIDTH // 2

        start_y = self.SCREEN_HEIGHT - 170
        btn_start = Button(
            "START",
            center_x - btn_w // 2,
            start_y,
            btn_w,
            btn_h,
            self.FONT_BUTTON,
        )

        sub_y = start_y + 62
        gap = 25
        btn_custom = Button(
            "CUSTOMIZATION",
            center_x - btn_w - gap // 2,
            sub_y,
            btn_w,
            btn_h,
            self.FONT_BUTTON,
        )
        btn_settings = Button(
            "SETTINGS",
            center_x + gap // 2,
            sub_y,
            btn_w,
            btn_h,
            self.FONT_BUTTON,
        )

        btn_exit = Button(
            "",
            self.SCREEN_WIDTH - 70,
            30,
            45,
            45,
            self.FONT_BUTTON,
            is_icon=True,
        )

        buttons = [btn_start, btn_custom, btn_settings, btn_exit]

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for btn in buttons:
                btn.check_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE
                ):
                    return

                if btn_start.is_clicked(mouse_pos, event):
                    self.launch_main_game()

                elif btn_custom.is_clicked(mouse_pos, event):
                    self.launch_customization()

                elif btn_settings.is_clicked(mouse_pos, event):
                    self.open_settings()

                elif btn_exit.is_clicked(mouse_pos, event):
                    pygame.quit()
                    sys.exit()

            self.zoom_scale += self.zoom_speed * self.zoom_direction
            if self.zoom_scale >= 1.35:
                self.zoom_direction = -1
            elif self.zoom_scale <= 1.0:
                self.zoom_direction = 1

            current_w = int(self.SCREEN_WIDTH * self.zoom_scale)
            current_h = int(self.SCREEN_HEIGHT * self.zoom_scale)
            scaled_bg = pygame.transform.smoothscale(
                self.base_bg, (current_w, current_h)
            )

            bg_x = (self.SCREEN_WIDTH - current_w) // 2
            bg_y = (self.SCREEN_HEIGHT - current_h) // 2

            self.screen.blit(scaled_bg, (bg_x, bg_y))

            self.draw_top_left_username()

            for btn in buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    menu = MainMenu(screen, clock)
    menu.run()