import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class Player:
    """Classe que representa a nave do jogador"""
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 70
        self.speed = 5
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        """Desenha a nave como um triângulo branco"""
        # Nave em formato de triângulo
        pygame.draw.polygon(screen, WHITE, [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ])

    def move(self, keys):
        """Move a nave baseado nas teclas pressionadas"""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Limita a nave dentro da tela
        self.x = max(0, min(self.x, WIDTH - self.width))
        self.y = max(0, min(self.y, HEIGHT - self.height))
        
        self.rect.topleft = (self.x, self.y)

    def get_bullet_pos(self):
        """Retorna a posição onde o tiro deve sair"""
        return (self.rect.centerx, self.rect.top)

class Bullet:
    """Classe que representa um projétil"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 3
        self.speed = 8
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                                self.radius * 2, self.radius * 2)

    def update(self):
        """Atualiza a posição do tiro"""
        self.y -= self.speed
        self.rect.y = self.y - self.radius

    def draw(self, screen):
        """Desenha o tiro como um círculo amarelo"""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        """Verifica se o tiro saiu da tela"""
        return self.y < 0

class Asteroid:
    """Classe que representa um asteroide"""
    def __init__(self):
        self.size = random.randint(20, 50)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = random.randint(-100, -40)
        self.speed_y = random.uniform(1, 4)
        self.speed_x = random.uniform(-2, 2)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))

    def update(self):
        """Atualiza a posição do asteroide"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        """Desenha o asteroide como um retângulo cinza"""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

    def is_off_screen(self):
        """Verifica se o asteroide saiu da tela"""
        return self.y > HEIGHT

class Game:
    """Classe principal que controla o jogo"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Space Shooter')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.font_large = pygame.font.SysFont(None, 72)
        self.reset_game()

    def reset_game(self):
        """Reinicia o jogo"""
        self.player = Player()
        self.bullets = []
        self.asteroids = [Asteroid() for _ in range(5)]
        self.score = 0
        self.time_survived = 0
        self.game_over = False
        self.menu = True

    def handle_events(self):
        """Processa eventos do jogo"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.menu:
                        self.menu = False
                        self.reset_game()
                    elif self.game_over:
                        self.reset_game()
                        self.menu = False
                
                if event.key == pygame.K_SPACE and not self.game_over and not self.menu:
                    x, y = self.player.get_bullet_pos()
                    self.bullets.append(Bullet(x, y))
        
        return True

    def update(self):
        """Atualiza o estado do jogo"""
        if self.menu or self.game_over:
            return
        
        # Atualiza jogador
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Atualiza tiros
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
            
            # Colisão com asteroides
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += 10
                    self.asteroids.append(Asteroid())  # Cria um novo asteroide
                    break
        
        # Atualiza asteroides
        for asteroid in self.asteroids:
            asteroid.update()
            
            # Colisão com jogador
            if asteroid.rect.colliderect(self.player.rect):
                self.game_over = True
            
            # Asteroide saiu da tela
            if asteroid.is_off_screen():
                asteroid.y = random.randint(-100, -40)
                asteroid.x = random.randint(asteroid.size, WIDTH - asteroid.size)
        
        # Incrementa pontuação por tempo
        self.time_survived += 1
        if self.time_survived % 60 == 0:  # A cada segundo
            self.score += 1

    def draw(self):
        """Desenha todos os elementos do jogo"""
        self.screen.fill(BLACK)
        
        # Desenha estrelas de fundo
        self.draw_stars()
        
        if self.menu:
            self.draw_menu()
        elif self.game_over:
            self.draw_game_over()
        else:
            # Desenha elementos do jogo
            self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            
            # Desenha pontuação
            self.draw_score()
        
        pygame.display.flip()

    def draw_stars(self):
        """Desenha estrelas no fundo"""
        random.seed(42)  # Seed fixo para consistência
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)

    def draw_menu(self):
        """Desenha o menu inicial"""
        title = self.font_large.render('SPACE SHOOTER', True, WHITE)
        subtitle = self.font.render('Pressione ENTER para começar', True, WHITE)
        
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Desenha instruções
        controls = [
            "Controles:",
            "Setas ou WASD - Mover",
            "ESPAÇO - Atirar",
            "ENTER - Começar/Reiniciar"
        ]
        
        y_offset = HEIGHT // 2 + 80
        for control in controls:
            text = self.font.render(control, True, YELLOW)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

    def draw_game_over(self):
        """Desenha a tela de Game Over"""
        game_over_text = self.font_large.render('GAME OVER', True, RED)
        score_text = self.font.render(f'Pontuação: {self.score}', True, WHITE)
        restart_text = self.font.render('Pressione ENTER para reiniciar', True, WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_score(self):
        """Desenha a pontuação atual"""
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

    def run(self):
        """Loop principal do jogo"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()