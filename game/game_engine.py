import sys
import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
YELLOW = (240, 220, 80)

DIFFICULTIES = {
    "Easy": {"gravity": 0.45, "jump_strength": -13.0, "terminal_velocity": 12.0},
    "Medium": {"gravity": 0.60, "jump_strength": -12.0, "terminal_velocity": 14.0},
    "Hard": {"gravity": 0.80, "jump_strength": -11.0, "terminal_velocity": 16.0},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)[cite: 2]

        ground_y = height - 40[cite: 2]
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ][cite: 2]
        self.hazards = [Hazard(240, ground_y - 14, 100)][cite: 2]
        self.goal_x = 740[cite: 2]

        self.score = 0[cite: 2]
        self.game_over = False[cite: 2]
        self.current_difficulty = "Medium"
        self.apply_difficulty("Medium")

        self.small_font = pygame.font.SysFont("Arial", 20)
        self.font = pygame.font.SysFont("Arial", 30)[cite: 2]
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)

    def apply_difficulty(self, difficulty_name):
        settings = DIFFICULTIES[difficulty_name]
        self.current_difficulty = difficulty_name
        self.gravity = settings["gravity"]
        self.terminal_velocity = settings["terminal_velocity"]
        self.player.jump_strength = settings["jump_strength"]

    def reset_game(self, difficulty_name):
        self.apply_difficulty(difficulty_name)
        self.score = 0
        self.game_over = False
        self.player.x = self.start_x
        self.player.y = self.start_y
        self.player.vx = 0
        self.player.vy = 0
        self.player.on_ground = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.reset_game("Easy")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.reset_game("Medium")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.reset_game("Hard")
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()[cite: 2]

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()[cite: 2]
        self.player.vx = 0[cite: 2]
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed[cite: 2]
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed[cite: 2]

    def update(self):
        if self.game_over:[cite: 2]
            return[cite: 2]

        # Apply gravity capped at terminal velocity
        self.player.vy = min(self.player.vy + self.gravity, self.terminal_velocity)
        self.player.x = max(0, self.player.x + self.player.vx)[cite: 2]

        # Swept collision detection
        old_bottom = self.player.y + self.player.height
        self.player.y += self.player.vy
        new_bottom = self.player.y + self.player.height
        self.player.on_ground = False[cite: 2]

        if self.player.vy >= 0:
            player_left = self.player.x
            player_right = self.player.x + self.player.width

            best_platform = None
            best_landing_y = float("inf")

            for platform in self.platforms:
                plat_left = platform.x[cite: 4]
                plat_right = platform.x + platform.width[cite: 4]
                plat_top = platform.y[cite: 4]

                if player_right > plat_left and player_left < plat_right:
                    if old_bottom <= plat_top and new_bottom >= plat_top:
                        if plat_top < best_landing_y:
                            best_landing_y = plat_top
                            best_platform = platform

            if best_platform is not None:
                self.player.y = best_platform.y - self.player.height[cite: 2]
                self.player.vy = 0[cite: 2]
                self.player.on_ground = True[cite: 2]

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):[cite: 2]
                self.game_over = True[cite: 2]
                return[cite: 2]

        if self.player.y > self.height:[cite: 2]
            self.game_over = True[cite: 2]
            return[cite: 2]

        if self.player.x >= self.goal_x:[cite: 2]
            self.score += 1[cite: 2]
            self.player.x, self.player.y = self.start_x, self.start_y[cite: 2]
            self.player.vy = 0[cite: 2]

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())[cite: 2]
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())[cite: 2]

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)[cite: 2]
        pygame.draw.rect(screen, GREEN, goal_rect)[cite: 2]

        pygame.draw.rect(screen, WHITE, self.player.rect())[cite: 2]

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)[cite: 2]
        screen.blit(score_text, (10, 10))[cite: 2]

        diff_text = self.small_font.render(f"Mode: {self.current_difficulty}", True, WHITE)
        screen.blit(diff_text, (10, 45))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            game_over_surf = self.large_font.render("Game Over!", True, RED)
            screen.blit(game_over_surf, game_over_surf.get_rect(center=(self.width // 2, self.height // 2 - 80)))

            final_score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(final_score_surf, final_score_surf.get_rect(center=(self.width // 2, self.height // 2 - 30)))

            options_title = self.small_font.render("Select difficulty to play again or quit:", True, YELLOW)
            screen.blit(options_title, options_title.get_rect(center=(self.width // 2, self.height // 2 + 25)))

            options = [
                "[1] Easy   (Low Gravity, Higher Jump)",
                "[2] Medium (Standard Physics)",
                "[3] Hard   (Heavy Gravity, Lower Jump)",
                "[Q] Quit Game",
            ]
            for idx, text in enumerate(options):
                opt_surf = self.small_font.render(text, True, WHITE)
                screen.blit(opt_surf, opt_surf.get_rect(center=(self.width // 2, self.height // 2 + 60 + (idx * 24))))