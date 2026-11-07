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

        # --- DUSTIN MOVEMENT: 4 SPRITES LOADING ---
        for i in range(1, 5):
            path = os.path.join(assets_dir, f"dustin{i}.jpeg")
            if not os.path.exists(path):
                path = os.path.join(assets_dir, f"dustin{i}.jpg")
            if not os.path.exists(path):
                path = os.path.join(assets_dir, f"dustin{i}.png")

            cleaned_img = self.clean_and_scale_image(path, target_height=170)
            self.sprites_right.append(cleaned_img)
            self.sprites_left.append(pygame.transform.flip(cleaned_img, True, False))

        self.controller = KeysController()
        self.char_x = self.controller.lanes[1]
        self.char_y = self.ground_y
        self.facing_right = True

        self.is_jumping = False
        self.is_rolling = False
        self.jump_count = 0

        self.current_frame = 0.0
        self.anim_speed = 0.20

        self.image = self.sprites_right[0]
        self.x = self.char_x
        self.y = self.char_y

    def clean_and_scale_image(self, image_path, target_height=170):
        if not os.path.exists(image_path):
            surf = pygame.Surface((120, target_height), pygame.SRCALPHA)
            surf.fill((255, 215, 0, 0))
            return surf

        pil_img = Image.open(image_path).convert("RGBA")
        data = pil_img.getdata()
        new_data = []

        # --- PERFECT JPEG BACKGROUND REMOVAL ---
        # Jo bhi pixels white ya light grey hain, unhein 100% transparent (alpha=0) kar do
        for item in data:
            r, g, b, a = item
            if r > 195 and g > 195 and b > 195:
                new_data.append((r, g, b, 0))  # Completely transparent
            else:
                new_data.append((r, g, b, 255)) # Keep character intact

        pil_img.putdata(new_data)

        # Ab getbbox() us transparent background ko bilkul khatam (crop) kar dega
        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)

        orig_w, orig_h = pil_img.size
        if orig_h == 0:
            orig_h = 1
        aspect_ratio = orig_w / float(orig_h)
        target_width = int(target_height * aspect_ratio)

        raw_str = pil_img.tobytes()
        pygame_img = pygame.image.fromstring(raw_str, pil_img.size, "RGBA")
        return pygame.transform.smoothscale(pygame_img, (target_width, target_height))

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

        self.current_frame = (self.current_frame + self.anim_speed) % len(self.sprites_right)

    def draw(self, surface):
        active_set = self.sprites_right if self.facing_right else self.sprites_left
        render_image = active_set[int(self.current_frame)]

        if self.is_rolling:
            render_image = pygame.transform.scale(render_image, (150, 80))

        draw_y = self.char_y if not self.is_rolling else self.char_y + 80
        self.image = render_image
        self.x = self.char_x
        self.y = draw_y

        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        w = self.image.get_width()
        h = self.image.get_height()
        return pygame.Rect(self.x, self.y, w, 80 if self.is_rolling else h)