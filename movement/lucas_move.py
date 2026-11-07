import os
import pygame
from PIL import Image
from keys_control import KeysController


class PlayerRunner(pygame.sprite.Sprite):
    def __init__(self, width=800, height=600):
        super().__init__()
        self.width = width
        self.height = height
        self.ground_y = 400

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "..", "assets")

        self.sprites_right = []
        self.sprites_left = []

        # --- LUCAS MOVEMENT: 4 SPRITES LOADING (160px Target Height) ---
        for i in range(1, 5):
            path = os.path.join(assets_dir, f"lucas{i}.jpeg")
            if not os.path.exists(path):
                path = os.path.join(assets_dir, f"lucas{i}.jpg")
            if not os.path.exists(path):
                path = os.path.join(assets_dir, f"lucas{i}.png")

            cleaned_img = self.clean_and_scale_image(path, target_height=160)
            self.sprites_right.append(cleaned_img)
            self.sprites_left.append(pygame.transform.flip(cleaned_img, True, False))

        self.controller = KeysController()
        self.char_x = self.controller.lanes[1]
        self.char_y = self.ground_y
        self.facing_right = True

        self.is_jumping = False
        self.is_rolling = False
        self.jump_count = 0

        # --- FIXED ANIMATION VARIABLES ---
        self.current_frame = 0.0
        self.anim_speed = 0.15  # Smooth cycling speed

        self.image = self.sprites_right[0]
        self.x = self.char_x
        self.y = self.char_y

    def clean_and_scale_image(self, image_path, target_height=160):
        if not os.path.exists(image_path):
            surf = pygame.Surface((100, target_height), pygame.SRCALPHA)
            surf.fill((46, 139, 87, 0))
            return surf

        pil_img = Image.open(image_path).convert("RGBA")
        data = pil_img.getdata()
        new_data = []

        # White/Light background box complete removal logic
        for item in data:
            r, g, b, a = item
            if r > 180 and g > 180 and b > 180:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))

        pil_img.putdata(new_data)

        # Auto-crop to remove extra whitespace and fix small size
        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)

        orig_w, orig_h = pil_img.size
        aspect_ratio = orig_w / float(orig_h)
        target_width = int(target_height * aspect_ratio)

        raw_str = pil_img.tobytes()
        pygame_img = pygame.image.fromstring(raw_str, pil_img.size, "RGBA")
        return pygame.transform.smoothscale(pygame_img, (max(1, target_width), max(1, target_height)))

    def update(self, events):
        (
            self.char_x,
            self.char_y,
            self.facing_right,
            self.is_jumping,
            self.is_rolling,
            self.jump_count,
        ) = self.controller.update(
            self.char_x, self.char_y, self.ground_y, self.facing_right, events
        )

        # --- ANIMATION FRAME INCREMENT FIX ---
        # Har frame pe anim_speed add hogi taake sprites fluidly cycle karein
        self.current_frame += self.anim_speed
        if self.current_frame >= len(self.sprites_right):
            self.current_frame = 0.0

    def draw(self, surface):
        active_set = self.sprites_right if self.facing_right else self.sprites_left
        frame_idx = int(self.current_frame) % len(active_set)
        render_image = active_set[frame_idx]

        if self.is_rolling:
            render_image = pygame.transform.scale(render_image, (130, 80))

        draw_y = self.char_y if not self.is_rolling else self.char_y + 60
        self.image = render_image
        self.x = self.char_x
        self.y = draw_y

        surface.blit(self.image, (int(self.x), int(self.y)))

    def get_rect(self):
        w = self.image.get_width()
        h = self.image.get_height()
        return pygame.Rect(int(self.x), int(self.y), w, 80 if self.is_rolling else h)