import json
import os
import sys
import pygame
from main import run as run_game


class CustomizationScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.WIDTH, self.HEIGHT = self.screen.get_size()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(BASE_DIR).lower() == "ui":
            self.parent_dir = os.path.dirname(BASE_DIR)
            self.current_dir = BASE_DIR
        else:
            self.parent_dir = BASE_DIR
            self.current_dir = os.path.join(BASE_DIR, "UI")

        self.assets_dir = os.path.join(self.parent_dir, "assets")
        os.makedirs(self.current_dir, exist_ok=True)

        self.characters = [
            {"name": "WILL", "file_base": "will", "color": (70, 130, 180)},
            {"name": "MIKE", "file_base": "mike", "color": (220, 20, 60)},
            {"name": "DUSTIN", "file_base": "dustin", "color": (255, 215, 0)},
            {"name": "LUCAS", "file_base": "lucas", "color": (46, 139, 87)},
            {"name": "MAX", "file_base": "max", "color": (255, 140, 0)},
            {"name": "ELEVEN", "file_base": "el", "color": (147, 112, 219)}
        ]
        self.selected_index = 1

        for char in self.characters:
            img = None
            for ext in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
                test_path = os.path.join(self.assets_dir, char["file_base"] + ext)
                if os.path.exists(test_path):
                    try:
                        img = pygame.image.load(test_path).convert_alpha()
                        break
                    except Exception as e:
                        print(f"Error loading {test_path}: {e}")
            if img:
                if char["name"] == "MIKE":
                    char["image"] = pygame.transform.smoothscale(img, (200, 160))
                else:
                    char["image"] = pygame.transform.smoothscale(img, (95, 140))
            else:
                char["image"] = None

        self.bg_image = None
        for ext in [".png", ".PNG", ".jpeg", ".JPEG", ".jpg", ".JPG"]:
            bg_path = os.path.join(self.assets_dir, "bgchar" + ext)
            if os.path.exists(bg_path):
                try:
                    self.bg_image = pygame.image.load(bg_path).convert()
                    self.bg_image = pygame.transform.scale(self.bg_image, (self.WIDTH, self.HEIGHT))
                    break
                except Exception:
                    pass

        font_path = os.path.join(self.assets_dir, "BebasNeue-Regular.ttf")
        try:
            self.font_title = pygame.font.Font(font_path, 52)
            self.font_name = pygame.font.Font(font_path, 26)
            self.font_instruction = pygame.font.Font(font_path, 22)
        except Exception:
            self.font_title = pygame.font.SysFont("Impact", 52)
            self.font_name = pygame.font.SysFont("Impact", 26)
            self.font_instruction = pygame.font.SysFont("Arial", 22)

        self.BORDER_COLOR = (255, 204, 0)
        self.TEXT_COLOR = (255, 255, 255)

        self.game_state = "SELECT"
        self.chosen_character = self.characters[self.selected_index]["name"]

        # Load existing player name from JSON if available, else default to "Player1"
        self.player_name = self.load_saved_player_name()

        self.name_btn_rect = pygame.Rect(self.WIDTH // 2 - 160, self.HEIGHT - 150, 320, 50)
        self.save_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.back_icon_rect = pygame.Rect(40, 40, 50, 50)

    def load_saved_player_name(self):
        """Read saved player name from JSON without resetting it to character name."""
        json_paths = [
            os.path.join(self.current_dir, "player_data.json"),
            os.path.join(self.parent_dir, "player_data.json")
        ]
        for path in json_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        saved_name = data.get("player_name") or data.get("username")
                        if saved_name and str(saved_name).strip():
                            return str(saved_name).strip()
                except Exception as e:
                    print(f"Error reading saved player name: {e}")
        return "Player1"

    def save_to_json(self, char, name):
        """Save selected character and player name to JSON at both root and UI levels."""
        data = {
            "selected_character": str(char).lower().strip(),
            "player_name": name.strip() if name.strip() != "" else "Player1"
        }

        # Save to both UI folder and root project folder for safety
        paths = [
            os.path.join(self.current_dir, "player_data.json"),
            os.path.join(self.parent_dir, "player_data.json")
        ]

        for json_path in paths:
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Saved to {json_path}: {data}")
            except Exception as e:
                print(f"Error saving JSON to {json_path}: {e}")

    def launch_game(self):
        if self.player_name.strip() == "":
            self.player_name = "Player1"
        self.save_to_json(self.chosen_character, self.player_name)

        print(f"Launching main.py with selected character: {self.chosen_character}")
        run_game(selected_character=self.chosen_character)

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WIDTH, self.HEIGHT = self.screen.get_size()

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.game_state == "SELECT":
                            if self.name_btn_rect.collidepoint(event.pos):
                                self.chosen_character = self.characters[self.selected_index]["name"]
                                self.game_state = "ENTER_NAME"
                            elif self.back_icon_rect.collidepoint(event.pos):
                                print("Returning to Main Menu...")
                                return
                        elif self.game_state == "ENTER_NAME":
                            if self.save_btn_rect.collidepoint(event.pos):
                                self.launch_game()
                                self.game_state = "SELECT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "ENTER_NAME":
                            self.game_state = "SELECT"
                        else:
                            return

                    if self.game_state == "SELECT":
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.selected_index = (self.selected_index - 1) % len(self.characters)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.selected_index = (self.selected_index + 1) % len(self.characters)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.chosen_character = self.characters[self.selected_index]["name"]
                            self.game_state = "ENTER_NAME"
                    elif self.game_state == "ENTER_NAME":
                        if event.key == pygame.K_RETURN:
                            self.launch_game()
                            self.game_state = "SELECT"
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            if len(self.player_name) < 15 and event.unicode.isprintable():
                                self.player_name += event.unicode

            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
                overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill((24, 43, 73))

            if self.game_state == "SELECT":
                header_rect = pygame.Rect(0, 40, self.WIDTH, 80)
                pygame.draw.rect(self.screen, (0, 0, 0), header_rect)
                title_surf = self.font_title.render("SELECT YOUR RUNNER", True, self.BORDER_COLOR)
                self.screen.blit(title_surf, (self.WIDTH // 2 - title_surf.get_width() // 2, 58))

                back_hovered = self.back_icon_rect.collidepoint(mouse_pos)
                icon_bg_color = (60, 90, 140) if back_hovered else (30, 50, 80)
                pygame.draw.rect(self.screen, icon_bg_color, self.back_icon_rect, border_radius=10)
                pygame.draw.rect(self.screen, self.BORDER_COLOR, self.back_icon_rect, 2, border_radius=10)
                arrow_surf = self.font_name.render("←", True, self.TEXT_COLOR)
                self.screen.blit(arrow_surf, (self.back_icon_rect.centerx - arrow_surf.get_width() // 2,
                                              self.back_icon_rect.centery - arrow_surf.get_height() // 2))

                card_width, card_height = 110, 240
                spacing = 15
                total_width = (len(self.characters) * card_width) + ((len(self.characters) - 1) * spacing)
                start_x = (self.WIDTH - total_width) // 2
                y_pos = self.HEIGHT // 2 - 140

                for i, char in enumerate(self.characters):
                    x_pos = start_x + (i * (card_width + spacing))
                    is_selected = (i == self.selected_index)
                    current_card_height = card_height + 15 if is_selected else card_height
                    current_y = y_pos - 15 if is_selected else y_pos
                    card_rect = pygame.Rect(x_pos, current_y, card_width, current_card_height)
                    pygame.draw.rect(self.screen, (40, 70, 110), card_rect, border_radius=15)
                    portrait_rect = pygame.Rect(x_pos + 10, current_y + 10, card_width - 20, current_card_height - 65)
                    pygame.draw.rect(self.screen, char["color"], portrait_rect, border_radius=10)
                    if char["image"]:
                        img_x = portrait_rect.centerx - char["image"].get_width() // 2
                        img_y = portrait_rect.centery - char["image"].get_height() // 2
                        self.screen.blit(char["image"], (img_x, img_y))
                    if is_selected:
                        pygame.draw.rect(self.screen, self.BORDER_COLOR, card_rect, 5, border_radius=15)
                    else:
                        pygame.draw.rect(self.screen, (70, 100, 140), card_rect, 2, border_radius=15)
                    name_surf = self.font_name.render(char["name"], True, self.TEXT_COLOR)
                    name_x = x_pos + (card_width // 2) - (name_surf.get_width() // 2)
                    name_y = current_y + current_card_height - 42
                    self.screen.blit(name_surf, (name_x, name_y))

                btn_hovered = self.name_btn_rect.collidepoint(mouse_pos)
                btn_bg_color = (230, 180, 0) if btn_hovered else self.BORDER_COLOR
                pygame.draw.rect(self.screen, btn_bg_color, self.name_btn_rect, border_radius=12)
                pygame.draw.rect(self.screen, (255, 255, 255), self.name_btn_rect, 2, border_radius=12)
                btn_text = self.font_name.render("CLICK TO ENTER NAME", True, (0, 0, 0))
                self.screen.blit(btn_text, (self.name_btn_rect.centerx - btn_text.get_width() // 2,
                                            self.name_btn_rect.centery - btn_text.get_height() // 2))

                inst_bg = pygame.Rect(0, self.HEIGHT - 70, self.WIDTH, 60)
                pygame.draw.rect(self.screen, (0, 0, 0), inst_bg)
                inst_surf = self.font_instruction.render("◀ ▶ Select Character | Click Button or Press [ENTER]", True,
                                                         self.TEXT_COLOR)
                self.screen.blit(inst_surf, (self.WIDTH // 2 - inst_surf.get_width() // 2, self.HEIGHT - 50))

            elif self.game_state == "ENTER_NAME":
                box_width, box_height = 520, 260
                box_x = self.WIDTH // 2 - box_width // 2
                box_y = self.HEIGHT // 2 - box_height // 2
                input_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                pygame.draw.rect(self.screen, (15, 28, 48), input_box_rect, border_radius=20)
                pygame.draw.rect(self.screen, self.BORDER_COLOR, input_box_rect, 4, border_radius=20)
                prompt_surf = self.font_name.render("ENTER YOUR PLAYER NAME:", True, self.TEXT_COLOR)
                self.screen.blit(prompt_surf, (box_x + box_width // 2 - prompt_surf.get_width() // 2, box_y + 25))
                text_field_rect = pygame.Rect(box_x + 40, box_y + 75, box_width - 80, 45)
                pygame.draw.rect(self.screen, (255, 255, 255), text_field_rect, border_radius=10)
                name_surf = self.font_name.render(self.player_name + "|", True, (0, 0, 0))
                self.screen.blit(name_surf, (text_field_rect.x + 15, text_field_rect.y + 8))
                self.save_btn_rect = pygame.Rect(box_x + 110, box_y + 140, box_width - 220, 45)
                save_hovered = self.save_btn_rect.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, (46, 139, 87) if save_hovered else (34, 102, 64), self.save_btn_rect,
                                 border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), self.save_btn_rect, 2, border_radius=10)
                save_txt = self.font_name.render("SAVE & PLAY", True, self.TEXT_COLOR)
                self.screen.blit(save_txt, (self.save_btn_rect.centerx - save_txt.get_width() // 2,
                                            self.save_btn_rect.centery - save_txt.get_height() // 2))
                sub_inst = self.font_instruction.render("[BACKSPACE] Delete | [ESC] Back to Selection", True,
                                                        (200, 200, 200))
                self.screen.blit(sub_inst, (box_x + box_width // 2 - sub_inst.get_width() // 2, box_y + 205))

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    custom_screen = CustomizationScreen(screen, clock)
    custom_screen.run()