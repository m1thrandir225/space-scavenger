import pygame
import random
import sys
from enum import Enum

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class GameState(Enum):
    MENU = 1
    DIFFICULTY = 2
    PLAYING = 3
    LOSE = 4
    WIN = 5

class Difficulty(Enum):
    EASY = {"speed": 5, "target_score": 100}
    MEDIUM = {"speed": 7, "target_score": 200}
    HARD = {"speed": 10, "target_score": 300}

def is_mouse_clicked(rect: pygame.Rect, last_click_time, cooldown=300):
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    current_time = pygame.time.get_ticks()

    if rect.collidepoint(mouse_pos) and mouse_clicked and (current_time - last_click_time > cooldown):
        return True, current_time
    return False, last_click_time

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.opacity = random.randint(50, 255)
        self.speed = self.size

    def draw(self, screen):
        star_surface = pygame.Surface((self.size, self.size))
        star_surface.fill(WHITE)
        star_surface.set_alpha(self.opacity)
        screen.blit(star_surface, (self.x, self.y))

    def twinkle(self):
        self.opacity = max(50, min(255, self.opacity + random.randint(-15, 15)))
    def move(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            self.size = random.randint(1, 3)
            self.speed = self.size
            self.opacity = random.randint(50, 255)
class Game:
    def __init__(self):
        self.game_state = None
        self.score = None
        self.difficulty = None
        self.player_pos = None
        self.player_speed = None
        self.asteroids = None
        self.crystals = None
        self.game_time = None
        self.last_click_time = None
        self.start_time = None
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Scavenger")
        self.clock = pygame.time.Clock()

        self.spaceship_img = pygame.image.load("assets/spaceship.png").convert_alpha()
        self.asteroid_img = pygame.image.load("assets/asteroid.png").convert_alpha()
        self.crystal_img = pygame.image.load("assets/energy_crystal.png").convert_alpha()

        # Base sizes
        self.ASTEROID_BASE_SIZE = 40
        self.MAX_ASTEROID_SCALE = 4.0  # Maximum scale factor for asteroids

        self.spaceship_img = pygame.transform.scale(self.spaceship_img, (50, 50))
        self.base_asteroid_img = pygame.transform.scale(self.asteroid_img, (self.ASTEROID_BASE_SIZE, self.ASTEROID_BASE_SIZE))
        self.crystal_img = pygame.transform.scale(self.crystal_img, (30, 30))

        self.stars = [Star() for _ in range(100)]


        self.background_music = pygame.mixer.Sound("assets/background_music.wav")
        self.clash_sound = pygame.mixer.Sound("assets/clash_sound.wav")
        self.background_music.play(-1)

        self.reset_game()

    def reset_game(self):
        self.game_state = GameState.MENU
        self.score = 0
        self.difficulty = None
        self.player_pos = [SCREEN_WIDTH // 2 - self.spaceship_img.get_width() // 2,
                   SCREEN_HEIGHT - self.spaceship_img.get_height() - 20]
        self.player_speed = 5
        self.asteroids = []
        self.crystals = []
        self.game_time = 0
        self.last_click_time = 0
        self.start_time = 0

    def draw_stars(self):
        for star in self.stars:
            star.move()
            star.draw(self.screen)
            if random.random() < 0.05:
                star.twinkle()

    def get_current_asteroid_scale(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        # Reach max size for asteroid after 60 sec
        scale = 1.0 + (elapsed_time / 60) * (self.MAX_ASTEROID_SCALE - 1.0)

        return min(scale, self.MAX_ASTEROID_SCALE)

    def get_scaled_asteroid(self, scale):
        size = int(self.ASTEROID_BASE_SIZE * scale)
        return pygame.transform.scale(self.base_asteroid_img, (size, size))

    def handle_menu(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        font = pygame.font.Font(None, 74)
        title = font.render("Space Scavenger", True, WHITE)
        play_text = font.render("Play", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)

        title_rect = self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        play_rect = self.screen.blit(play_text, (SCREEN_WIDTH//2 - play_text.get_width()//2, 300))
        exit_rect = self.screen.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, 400))

        clicked_play, self.last_click_time = is_mouse_clicked(play_rect, self.last_click_time)
        clicked_exit, self.last_click_time = is_mouse_clicked(exit_rect, self.last_click_time)

        if clicked_play:
            self.game_state = GameState.DIFFICULTY

        if clicked_exit:
            pygame.quit()
            sys.exit()

    def handle_difficulty(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        font = pygame.font.Font(None, 74)
        smaller_font = pygame.font.Font(None, 54)

        easy_text = font.render("Easy", True, WHITE)
        medium_text = font.render("Medium", True, WHITE)
        hard_text = font.render("Hard", True, WHITE)
        back_text = smaller_font.render("Back", True, YELLOW)


        back_rect = self.screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, 500))

        easy_rect = self.screen.blit(easy_text, (SCREEN_WIDTH//2 - easy_text.get_width()//2, 200))
        medium_rect = self.screen.blit(medium_text, (SCREEN_WIDTH//2 - medium_text.get_width()//2, 300))
        hard_rect = self.screen.blit(hard_text, (SCREEN_WIDTH//2 - hard_text.get_width()//2, 400))

        easy_pressed, self.last_click_time = is_mouse_clicked(easy_rect, self.last_click_time)
        medium_pressed, self.last_click_time = is_mouse_clicked(medium_rect, self.last_click_time)
        hard_pressed, self.last_click_time = is_mouse_clicked(hard_rect, self.last_click_time)
        back_pressed, self.last_click_time = is_mouse_clicked(back_rect, self.last_click_time)

        if easy_pressed:
            self.difficulty = Difficulty.EASY
            self.start_game()
        if medium_pressed:
            self.difficulty = Difficulty.MEDIUM
            self.start_game()
        if hard_pressed:
            self.difficulty = Difficulty.HARD
            self.start_game()
        if back_pressed:
            self.game_state = GameState.MENU

    def start_game(self):
        self.game_state = GameState.PLAYING
        self.score = 0
        self.player_speed = self.difficulty.value["speed"]
        self.asteroids = []
        self.crystals = []
        self.player_pos = [SCREEN_WIDTH // 2 - self.spaceship_img.get_width() // 2,
                           SCREEN_HEIGHT - self.spaceship_img.get_height() - 20]
        self.start_time = pygame.time.get_ticks()  # Record start time

    def spawn_asteroid(self):
        if random.random() < 0.02:
            current_scale = self.get_current_asteroid_scale()
            size = int(self.ASTEROID_BASE_SIZE * current_scale)
            x = random.randint(0, SCREEN_WIDTH - size)
            self.asteroids.append([x, -size, current_scale])

    def spawn_crystal(self):
        if random.random() < 0.01:
            x = random.randint(0, SCREEN_WIDTH - self.crystal_img.get_width())
            self.crystals.append([x, -self.crystal_img.get_height()])

    def handle_playing(self):
        self.screen.fill(BLACK)
        self.draw_stars()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and self.player_pos[0] > 0:
            self.player_pos[0] -= self.player_speed
        if keys[pygame.K_d] and self.player_pos[0] < SCREEN_WIDTH - self.spaceship_img.get_width():
            self.player_pos[0] += self.player_speed
        if keys[pygame.K_w] and self.player_pos[1] > 0:
            self.player_pos[1] -= self.player_speed
        if keys[pygame.K_s] and self.player_pos[1] < SCREEN_HEIGHT - self.spaceship_img.get_height():
            self.player_pos[1] += self.player_speed

        self.spawn_asteroid()
        self.spawn_crystal()
        spaceship_rect = self.screen.blit(self.spaceship_img, self.player_pos)

        for asteroid in self.asteroids[:]:
            asteroid[1] += 5
            if asteroid[1] > SCREEN_HEIGHT:
                self.asteroids.remove(asteroid)
            else:
                scaled_asteroid = self.get_scaled_asteroid(asteroid[2])
                self.screen.blit(scaled_asteroid, (asteroid[0], asteroid[1]))

                asteroid_rect = pygame.Rect(asteroid[0], asteroid[1],
                                            int(self.ASTEROID_BASE_SIZE * asteroid[2]),
                                            int(self.ASTEROID_BASE_SIZE * asteroid[2]))
                player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1],
                                          self.spaceship_img.get_width(),
                                          self.spaceship_img.get_height())

                if asteroid_rect.colliderect(player_rect):
                    self.clash_sound.play()
                    self.game_state = GameState.LOSE

        for crystal in self.crystals[:]:
            crystal[1] += 3
            if crystal[1] > SCREEN_HEIGHT:
                self.crystals.remove(crystal)
            else:
                self.screen.blit(self.crystal_img, crystal)
                if self.check_collision(crystal, self.player_pos):
                    self.score += 10
                    self.crystals.remove(crystal)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 10))

        if self.score >= self.difficulty.value["target_score"]:
            self.game_state = GameState.WIN

    def check_collision(self, obj_pos, player_pos):
        obj_rect = pygame.Rect(obj_pos[0], obj_pos[1],
                               self.crystal_img.get_width(), self.crystal_img.get_height())
        player_rect = pygame.Rect(player_pos[0], player_pos[1],
                                  self.spaceship_img.get_width(), self.spaceship_img.get_height())
        return obj_rect.colliderect(player_rect)

    def handle_lose(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        font = pygame.font.Font(None, 74)

        game_over = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        restart_text = font.render("Restart", True, WHITE)
        menu_text = font.render("Main Menu", True, WHITE)

        game_over_rect = self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 100))
        score_rect = self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))
        restart_rect = self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 300))
        menu_rect = self.screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 400))

        clicked_restart, self.last_click_time = is_mouse_clicked(restart_rect, self.last_click_time)
        clicked_menu, self.last_click_time = is_mouse_clicked(menu_rect, self.last_click_time)

        if clicked_restart:
            self.start_game()

        if clicked_menu:
            self.reset_game()

    def handle_win(self):
        self.screen.fill(BLACK)
        self.draw_stars()

        font = pygame.font.Font(None, 74)
        win_text = font.render("YOU WIN!", True, GREEN)
        score_text = font.render(f"Final Score: {self.score}", True, WHITE)
        menu_text = font.render("Main Menu", True, WHITE)

        win_rect = self.screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, 100))
        score_rect = self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))
        menu_rect = self.screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 300))

        clicked_menu, self.last_click_time = is_mouse_clicked(menu_rect, self.last_click_time)

        if clicked_menu:
            self.reset_game()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.game_state == GameState.MENU:
                self.handle_menu()
            elif self.game_state == GameState.DIFFICULTY:
                self.handle_difficulty()
            elif self.game_state == GameState.PLAYING:
                self.handle_playing()
            elif self.game_state == GameState.LOSE:
                self.handle_lose()
            elif self.game_state == GameState.WIN:
                self.handle_win()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()