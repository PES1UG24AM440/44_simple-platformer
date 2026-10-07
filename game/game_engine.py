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

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 0.6
        self.terminal_velocity = 14.0

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.goal_x = 740

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            return

        # Apply gravity capped at terminal velocity
        self.player.vy = min(self.player.vy + self.gravity, self.terminal_velocity)
        self.player.x = max(0, self.player.x + self.player.vx)

        # Track pre-movement vertical position for swept collision detection
        old_bottom = self.player.y + self.player.height
        self.player.y += self.player.vy
        new_bottom = self.player.y + self.player.height
        self.player.on_ground = False

        if self.player.vy >= 0:
            player_left = self.player.x
            player_right = self.player.x + self.player.width

            best_platform = None
            best_landing_y = float("inf")

            for platform in self.platforms:
                plat_left = platform.x
                plat_right = platform.x + platform.width
                plat_top = platform.y

                if player_right > plat_left and player_left < plat_right:
                    if old_bottom <= plat_top and new_bottom >= plat_top:
                        if plat_top < best_landing_y:
                            best_landing_y = plat_top
                            best_platform = platform

            if best_platform is not None:
                self.player.y = best_platform.y - self.player.height
                self.player.vy = 0
                self.player.on_ground = True

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Semi-transparent dark overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Game Over text
            game_over_surf = self.large_font.render("Game Over!", True, RED)
            game_over_rect = game_over_surf.get_rect(center=(self.width // 2, self.height // 2 - 30))
            screen.blit(game_over_surf, game_over_rect)

            # Final Score text
            final_score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_surf.get_rect(center=(self.width // 2, self.height // 2 + 25))
            screen.blit(final_score_surf, final_score_rect)