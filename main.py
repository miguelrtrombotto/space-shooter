import pygame
import random
import sys
import os
import math
import json
from pygame import mixer

# Inicializar pygame
pygame.init()
mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 7
ENEMY_SPEED = 2
BULLET_SPEED = 10
STAR_COUNT = 100

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            # Intentar cargar imagen del jugador
            self.image = pygame.image.load(os.path.join('assets', 'player.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))
        except:
            # Si no se encuentra la imagen, crear una superficie en blanco
            self.image = pygame.Surface((50, 40))
            self.image.fill(GREEN)

        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.speed = PLAYER_SPEED
        self.health = 100
        self.max_health = 100
        self.shoot_delay = 250  # milisegundos
        self.last_shot = pygame.time.get_ticks()
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            shot_level = getattr(self, 'shot_level', 1)
            
            if shot_level == 1:
                # Disparo normal
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif shot_level == 3:
                # Disparo triple
                bullet1 = Bullet(self.rect.centerx - 15, self.rect.top)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.centerx + 15, self.rect.top)
                all_sprites.add(bullet1, bullet2, bullet3)
                bullets.add(bullet1, bullet2, bullet3)
            elif shot_level >= 6:
                # Disparo séxtuple
                positions = [-30, -18, -6, 6, 18, 30]
                for pos in positions:
                    bullet = Bullet(self.rect.centerx + pos, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            
            shoot_sound.play()
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, special=False):
        super().__init__()
        self.special = special
        try:
            # Intentar cargar imagen del enemigo
            self.image = pygame.image.load(os.path.join('assets', 'enemy.png')).convert_alpha()
            if special:
                self.image = pygame.transform.scale(self.image, (80, 80))  # Doble tamaño para especiales
            else:
                self.image = pygame.transform.scale(self.image, (40, 40))
        except:
            # Si no se encuentra la imagen, crear una superficie en blanco
            if special:
                self.image = pygame.Surface((80, 80))  # Doble tamaño para especiales
                self.image.fill(MAGENTA)  # Nave especial magenta
            else:
                self.image = pygame.Surface((40, 40))
                self.image.fill(RED)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(1, 3)
        self.health = 30
        self.can_shoot = random.random() < 0.3
        self.shoot_delay = random.randint(2000, 4000)
        self.last_shot = pygame.time.get_ticks()
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
        
        if self.can_shoot and self.rect.y > 0 and self.rect.y < HEIGHT - 100:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot_delay = random.randint(2000, 4000)
                enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Intentar cargar imagen de la bala
            self.image = pygame.image.load(os.path.join('assets', 'bullet.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (5, 15))
        except:
            # Si no se encuentra la imagen, crear una superficie en blanco
            self.image = pygame.Surface((5, 15))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()
            
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
            
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)
        
class PlayerFragment:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-4, -1)
        self.rotation = 0
        self.rotation_speed = random.uniform(-10, 10)
        self.size = random.randint(3, 8)
        self.color = random.choice([WHITE, YELLOW, RED])
        self.life = 120
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.1
        self.rotation += self.rotation_speed
        self.life -= 1
    
    def draw(self, screen):
        if self.life > 0:
            points = []
            for dx, dy in [(-self.size//2, -self.size//2), (self.size//2, -self.size//2), 
                          (self.size//2, self.size//2), (-self.size//2, self.size//2)]:
                angle = math.radians(self.rotation)
                rx = dx * math.cos(angle) - dy * math.sin(angle)
                ry = dx * math.sin(angle) + dy * math.cos(angle)
                points.append((self.x + rx, self.y + ry))
            pygame.draw.polygon(screen, self.color, points)
            
class EnergyHalo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 80
        self.alpha = 255
        self.life = 60
        self.expand_speed = 2
    
    def update(self):
        self.radius += self.expand_speed
        self.alpha = int(255 * (self.life / 60))
        self.life -= 1
    
    def draw(self, screen):
        if self.life > 0 and self.radius < self.max_radius:
            halo_surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
            for i in range(3):
                radius = max(1, self.radius - i * 5)
                alpha = max(0, self.alpha - i * 50)
                color = (*YELLOW[:3], alpha)
                pygame.draw.circle(halo_surface, color, (self.max_radius, self.max_radius), radius, 3)
            screen.blit(halo_surface, (self.x - self.max_radius, self.y - self.max_radius))
        
class EnemyWave:
    def __init__(self):
        self.wave_number = 0
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.spawn_delay = 1000  # milisegundos entre apariciones
        self.last_spawn = 0
        self.wave_complete = False
    
    def start_new_wave(self):
        self.wave_number += 1
        # Incrementar enemigos gradualmente (máximo 15 por oleada)
        self.enemies_in_wave = min(5 + self.wave_number, 15)
        self.enemies_spawned = 0
        self.spawn_delay = max(300, 1000 - (self.wave_number * 50))  # Apariciones más rápidas conforme avanzan las oleadas
        self.wave_complete = False
    
    def update(self):
        now = pygame.time.get_ticks()
        if (self.enemies_spawned < self.enemies_in_wave and 
            now - self.last_spawn > self.spawn_delay):
            self.last_spawn = now
            self.spawn_enemy()
            self.enemies_spawned += 1
            if self.enemies_spawned >= self.enemies_in_wave:
                self.wave_complete = True
    
    def spawn_enemy(self):
        # Generar enemigos en diferentes patrones
        if self.wave_number % 3 == 0:
            # Formación en V
            cols = min(5, self.enemies_in_wave)
            spacing = WIDTH // (cols + 1)
            x = spacing * ((self.enemies_spawned % cols) + 1)
            y = -40 - (20 * (self.enemies_spawned // cols))
        else:
            # Dispersión aleatoria
            x = random.randint(50, WIDTH-50)
            y = -40
        
        # 10% de probabilidad de nave especial
        special = random.random() < 0.1
        enemy = Enemy(x, y, special)
        all_sprites.add(enemy)
        enemies.add(enemy)
        
def draw_lives(surface, x, y, lives, max_lives, font):
    # Calcular dimensiones de los círculos
    circle_radius = 7  # La mitad del tamaño original
    circle_spacing = 18  # Espaciado ajustado para círculos más pequeños
    total_circles_width = (max_lives - 1) * circle_spacing
    
    # Dibujar texto "Vidas" centrado arriba de los círculos
    lives_text = font.render("Vidas", True, WHITE)
    text_x = x + (total_circles_width - lives_text.get_width()) // 2
    surface.blit(lives_text, (text_x, y))
    
    # Dibujar círculos debajo del texto
    circle_y = y + 30  # Posicionar círculos debajo del texto
    
    for i in range(max_lives):
        circle_x = x + (i * circle_spacing)
        if i < lives:
            # Círculo blanco para vidas restantes
            pygame.draw.circle(surface, WHITE, (circle_x, circle_y), circle_radius)
        else:
            # Círculo negro con borde blanco para vidas perdidas
            pygame.draw.circle(surface, BLACK, (circle_x, circle_y), circle_radius)
            pygame.draw.circle(surface, WHITE, (circle_x, circle_y), circle_radius, 2)

def load_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_scores(scores):
    with open('scores.json', 'w') as f:
        json.dump(scores, f)

def add_score(initials, score):
    scores = load_scores()
    scores.append({'initials': initials, 'score': score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    scores = scores[:10]
    save_scores(scores)

def get_player_initials():
    initials = ""
    input_active = True
    
    while input_active:
        screen.fill(BLACK)
        if background:
            screen.blit(background, (0, 0))
        else:
            for star in stars:
                star.draw(screen)
        
        title = big_font.render("INGRESA TUS INICIALES", True, WHITE)
        prompt = font.render("Escribe 3 letras y presiona ENTER:", True, WHITE)
        current = font.render(initials + "_" * (3 - len(initials)), True, YELLOW)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))
        screen.blit(current, (WIDTH//2 - current.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(initials) == 3:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha():
                    initials += event.unicode.upper()
    
    return initials

def show_high_scores():
    scores = load_scores()
    waiting = True
    
    while waiting:
        screen.fill(BLACK)
        if background:
            screen.blit(background, (0, 0))
        else:
            for star in stars:
                star.draw(screen)
        
        title = big_font.render("MEJORES PUNTAJES", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        for i, score_data in enumerate(scores[:10]):
            rank_text = font.render(f"{i+1:2d}. {score_data['initials']} - {score_data['score']:,}", True, WHITE)
            screen.blit(rank_text, (WIDTH//2 - rank_text.get_width()//2, 120 + i * 40))
        
        continue_text = font.render("Presiona cualquier tecla para continuar", True, WHITE)
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                waiting = False
    
def show_start_screen():
    screen.fill(BLACK)
    if background:
        screen.blit(background, (0, 0))
    else:
        for star in stars:
            star.draw(screen)
    
    title = big_font.render("DISPARADOR ESPACIAL", True, WHITE)
    start = font.render("Presiona cualquier tecla para comenzar", True, WHITE)
    controls = font.render("Flechas para mover, ESPACIO para disparar", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2))
    screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT*3//4))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False
                
def show_game_over_screen():
    screen.fill(BLACK)
    if background:
        screen.blit(background, (0, 0))
    else:
        for star in stars:
            star.draw(screen)
    
    game_over = big_font.render("JUEGO TERMINADO", True, RED)
    final_score = font.render(f"Puntuación Final: {score}", True, WHITE)
    restart = font.render("Presiona cualquier tecla para reiniciar o ESC para salir", True, WHITE)
    
    screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//3))
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2))
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT*2//3))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return False
                else:
                    return True
                
if __name__ == "__main__":
    # Crear ventana del juego
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Disparador Espacial")
    clock = pygame.time.Clock()

    # Intentar cargar imagen de fondo
    try:
        background = pygame.image.load(os.path.join('assets', 'background.jpg')).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = None

    # Crear estrellas para el fondo (si no hay imagen de fondo)
    stars = [Star() for _ in range(STAR_COUNT)] if background is None else []
    
    # Variables de fuentes
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    
    # Obtener iniciales del jugador
    player_initials = get_player_initials()
    
    # Mostrar puntajes altos
    show_high_scores()

    # Crear grupos de sprites
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # Crear jugador
    player = Player()
    all_sprites.add(player)

    # Crear controlador de oleadas de enemigos
    wave_controller = EnemyWave()
    wave_controller.start_new_wave()

    # Cargar sonidos
    try:
        shoot_sound = mixer.Sound(os.path.join('assets', 'shoot.wav'))
        explosion_sound = mixer.Sound(os.path.join('assets', 'explosion.wav'))
        mixer.music.load(os.path.join('assets', 'background.mp3'))
        mixer.music.set_volume(0.5)
        mixer.music.play(loops=-1)
    except:
        print("Archivos de sonido no encontrados - continuando sin sonido")
        shoot_sound = mixer.Sound(buffer=bytearray(44))
        explosion_sound = mixer.Sound(buffer=bytearray(44))

    # Variables del juego
    score = 0
    game_over = False
    paused = False
    
    # Sistema de vidas
    lives = 4
    max_lives = 4
    
    # Variables de explosión
    player_exploding = False
    explosion_start_time = 0
    explosion_sounds_played = 0
    explosion_sound_delay = 150
    explosion_fragments = []
    explosion_duration = 3000
    explosion_sound_channel = None
    
    # Variables de efecto de halo
    energy_halos = []
    
    # Sistema de niveles de disparo
    player.shot_level = 1

    # Bucle principal del juego
    running = True
    show_start_screen()

    while running:
        # Efecto de cámara lenta durante la explosión
        if player_exploding:
            clock.tick(FPS // 3)
        else:
            clock.tick(FPS)
        
        # Procesar entrada
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not paused:
                    player.shoot()
                elif event.key == pygame.K_p and not game_over:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Manejar secuencia de explosión del jugador
        if player_exploding:
            current_time = pygame.time.get_ticks()
            explosion_elapsed = current_time - explosion_start_time
            
            # Actualizar fragmentos
            for fragment in explosion_fragments[:]:
                fragment.update()
                if fragment.life <= 0:
                    explosion_fragments.remove(fragment)
            
            # Terminar explosión después de la duración
            if explosion_elapsed > explosion_duration:
                game_over = True
                player_exploding = False
                explosion_fragments.clear()
                if explosion_sound_channel:
                    explosion_sound_channel.stop()
        
        if not game_over and not paused and not player_exploding:
            # Actualizar
            # Actualizar oleada de enemigos
            wave_controller.update()
            
            # Iniciar nueva oleada si la actual está completa
            if wave_controller.wave_complete and len(enemies) == 0:
                wave_controller.start_new_wave()
            
            # Actualizar todos los sprites
            all_sprites.update()
            
            # Actualizar estrellas (si no hay imagen de fondo)
            if background is None:
                for star in stars:
                    star.update()
            
            # Actualizar halos de energía
            for halo in energy_halos[:]:
                halo.update()
                if halo.life <= 0:
                    energy_halos.remove(halo)
            
            # Verificar colisiones bala-enemigo
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                explosion_sound.play()
                if hit.special:
                    # Nave especial mejora el nivel de disparo
                    if player.shot_level == 1:
                        player.shot_level = 3  # De normal a triple
                    elif player.shot_level == 3:
                        player.shot_level = 6  # De triple a séxtuple
                    score += 100  # Más puntos por nave especial
                else:
                    score += 50 - hit.speed * 10  # Enemigos más rápidos dan menos puntos
            
            # Verificar colisiones jugador-enemigo
            hits = pygame.sprite.spritecollide(player, enemies, True)
            for hit in hits:
                explosion_sound.play()
                lives -= 1
                # Resetear a disparo normal al perder una vida
                player.shot_level = 1
                # Crear halo de energía cuando se pierde una vida
                halo = EnergyHalo(player.rect.centerx, player.rect.centery)
                energy_halos.append(halo)
            
            # Verificar colisiones bala enemiga-jugador
            bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for bullet_hit in bullet_hits:
                explosion_sound.play()
                lives -= 1
                # Resetear a disparo normal al perder una vida
                player.shot_level = 1
                # Crear halo de energía cuando se pierde una vida
                halo = EnergyHalo(player.rect.centerx, player.rect.centery)
                energy_halos.append(halo)
                
            if lives <= 0 and not player_exploding:
                player_exploding = True
                explosion_start_time = pygame.time.get_ticks()
                explosion_sounds_played = 0
                # Crear fragmentos de explosión
                for _ in range(15):
                    fragment = PlayerFragment(player.rect.centerx, player.rect.centery)
                    explosion_fragments.append(fragment)
                # Ocultar jugador
                player.rect.x = -1000
                # Iniciar sonido continuo de explosión
                explosion_sound_channel = explosion_sound.play(loops=-1)
        
        # Dibujar
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)
            for star in stars:
                star.draw(screen)
        
        # Dibujar todos los sprites
        all_sprites.draw(screen)
        
        # Dibujar fragmentos de explosión
        for fragment in explosion_fragments:
            fragment.draw(screen)
        
        # Dibujar halos de energía
        for halo in energy_halos:
            halo.draw(screen)
        
        # Dibujar interfaz de usuario
        draw_lives(screen, 20, 20, lives, max_lives, font)
        score_text = font.render(f"Puntos: {score}", True, WHITE)
        wave_text = font.render(f"Oleada: {wave_controller.wave_number}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 50))
        
        if paused:
            pause_text = big_font.render("PAUSADO", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))
        
        if game_over:
            # Guardar puntaje
            add_score(player_initials, score)
            
            if show_game_over_screen():
                # Mostrar puntajes altos
                show_high_scores()
                
                # Reiniciar juego
                game_over = False
                score = 0
                lives = max_lives
                player_exploding = False
                explosion_sounds_played = 0
                explosion_fragments.clear()
                energy_halos.clear()
                if explosion_sound_channel:
                    explosion_sound_channel.stop()
                
                # Limpiar todos los sprites
                for sprite in all_sprites:
                    sprite.kill()
                
                # Recrear jugador
                player = Player()
                player.shot_level = 1
                all_sprites.add(player)
                
                # Reiniciar controlador de oleadas
                wave_controller = EnemyWave()
                wave_controller.start_new_wave()
            else:
                running = False
        
        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()
    sys.exit()