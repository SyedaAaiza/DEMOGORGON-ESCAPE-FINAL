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

        # --- MIKE MOVEMENT: 5 SPRITES LOADING (160px Target Height & PNG Format) ---
        for i in range(1, 6):
            path = os.path.join(assets_dir, f"mike{i}.png")
            if not os.path.exists(path):
                path = os.path.join(assets_dir, f"mike{i}.PNG")

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

        self.current_frame = 0.0
        self.anim_speed = 0.20

        self.image = self.sprites_right[0]
        self.x = self.char_x
        self.y = self.char_y

    def clean_and_scale_image(self, image_path, target_height=160):
        if not os.path.exists(image_path):
            surf = pygame.Surface((100, target_height), pygame.SRCALPHA)
            surf.fill((30, 144, 255, 0))  # Blue fallback surface for Mike
            return surf

        pil_img = Image.open(image_path).convert("RGBA")
        data = pil_img.getdata()
        new_data = []

        # Transparent box complete removal logic
        for item in data:
            r, g, b, a = item
            if r > 180 and g > 180 and b > 180:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))

        pil_img.putdata(new_data)

        # Auto-crop extra background space to fix sizing
        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)

        orig_w, orig_h = pil_img.size
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
            render_image = pygame.transform.scale(render_image, (130, 80))

        draw_y = self.char_y if not self.is_rolling else self.char_y + 60
        self.image = render_image
        self.x = self.char_x
        self.y = draw_y

        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        w = self.image.get_width()
        h = self.image.get_height()
        return pygame.Rect(self.x, self.y, w, 80 if self.is_rolling else h)