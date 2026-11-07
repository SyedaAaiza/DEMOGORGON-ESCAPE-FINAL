import pygame


class KeysController:
    def __init__(self):
        # Widened lane coordinates (Left: 150 | Center: 335 | Right: 520)
        self.lanes = [150, 335, 520]
        self.current_lane = 1  # Start in Center Lane

        # Smooth transition speed between lanes
        self.lane_transition_speed = 30

        # Jump & Double Jump physics
        self.is_jumping = False
        self.jump_count = 0
        self.max_jumps = 2
        self.jump_velocity = -26
        self.double_jump_velocity = -12
        self.gravity = 0.8
        self.y_velocity = 0

        # Roll state
        self.is_rolling = False

    def update(self, char_x, char_y, ground_y, facing_right, events):
        keys = pygame.key.get_pressed()

        # Hold to Roll
        down_held = keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT]
        if down_held and not self.is_jumping:
            self.is_rolling = True
        else:
            self.is_rolling = False

        # Key press events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.current_lane > 0:
                    self.current_lane -= 1
                    facing_right = False
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.current_lane < 2:
                    self.current_lane += 1
                    facing_right = True
                elif (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.is_rolling:
                    if not self.is_jumping:
                        self.is_jumping = True
                        self.jump_count = 1
                        self.y_velocity = self.jump_velocity
                    elif self.jump_count < self.max_jumps:
                        self.jump_count += 1
                        self.y_velocity = self.double_jump_velocity

        # Smooth lane slide
        target_x = self.lanes[self.current_lane]
        if char_x < target_x:
            char_x = min(target_x, char_x + self.lane_transition_speed)
        elif char_x > target_x:
            char_x = max(target_x, char_x - self.lane_transition_speed)

        # Jump physics update
        if self.is_jumping:
            char_y += self.y_velocity
            self.y_velocity += self.gravity

            if char_y >= ground_y:
                char_y = ground_y
                self.is_jumping = False
                self.jump_count = 0
                self.y_velocity = 0

        return char_x, char_y, facing_right, self.is_jumping, self.is_rolling, self.jump_count