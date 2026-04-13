"""
╔══════════════════════════════════════════════════════════════╗
║                   SPACE INVADERS EN PYTHON                  ║
║                  Desarrollado con pygame                    ║
╚══════════════════════════════════════════════════════════════╝

CÓMO EJECUTAR:
    1. Instala pygame:  pip install pygame
    2. Ejecuta:         python space_invaders.py

CONTROLES:
    ← →      Mover nave izquierda / derecha
    ESPACIO  Disparar
    P        Pausar / reanudar
    R        Reiniciar partida
    ESC      Salir

REGLAS:
    - Elimina todos los aliens antes de que lleguen al suelo.
    - Los aliens se aceleran conforme quedan menos en pantalla.
    - Los bunkers te protegen pero se van destruyendo con los disparos.
    - Tienes 3 vidas. El alien misterioso da puntos extra al destruirlo.
    - Cada oleada superada aumenta la velocidad inicial de los aliens.
"""

import pygame
import random
import sys
import math

# ─────────────────────────────────────────────────────────────
# CONSTANTES GLOBALES
# ─────────────────────────────────────────────────────────────

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS           = 60

# ── Colores (R, G, B) ─────────────────────────────────────────
COLOR_BG         = (5,   5,  20)   # Fondo negro espacial
COLOR_TEXT       = (220, 220, 255)
COLOR_TITLE      = (80,  220, 120) # Verde arcade clásico
COLOR_PLAYER     = (80,  200, 255) # Cian — nave del jugador
COLOR_BULLET_P   = (80,  200, 255) # Bala del jugador
COLOR_BULLET_E   = (255, 80,  80)  # Bala enemiga (roja)
COLOR_BUNKER     = (80,  200, 80)  # Bunkers verdes
COLOR_MYSTERY    = (255, 50,  200) # Alien misterioso (magenta)
COLOR_HUD        = (180, 180, 220) # Barra HUD

# ── Dimensiones de sprites ────────────────────────────────────
PLAYER_W, PLAYER_H    = 48, 28
ALIEN_W,  ALIEN_H     = 36, 28
BULLET_W, BULLET_H    = 4,  14
MYSTERY_W, MYSTERY_H  = 52, 22

# ── Rejilla de aliens ─────────────────────────────────────────
ALIEN_COLS   = 11   # Columnas de aliens
ALIEN_ROWS   = 5    # Filas de aliens
ALIEN_X0     = 70   # X inicial del primer alien
ALIEN_Y0     = 80   # Y inicial de la primera fila
ALIEN_GAP_X  = 58   # Separación horizontal entre aliens
ALIEN_GAP_Y  = 48   # Separación vertical entre filas

# ── Puntos por tipo de alien (fila 0 = arriba) ───────────────
ALIEN_POINTS = [30, 20, 20, 10, 10]

# ── Bunkers ───────────────────────────────────────────────────
BUNKER_COUNT = 4
BUNKER_Y     = SCREEN_HEIGHT - 130
BUNKER_W     = 64
BUNKER_H     = 44
BUNKER_COLS  = 8    # Cuadrícula interna de píxeles del bunker
BUNKER_ROWS  = 6

# ── HUD ───────────────────────────────────────────────────────
HUD_HEIGHT   = 36
LIVES_START  = 3

# ── Alien misterioso ──────────────────────────────────────────
MYSTERY_POINTS_OPTIONS = [50, 100, 150, 300]
MYSTERY_INTERVAL       = 600   # Frames entre apariciones
MYSTERY_SPEED          = 2.5


# ─────────────────────────────────────────────────────────────
# FUNCIONES PARA DIBUJAR SPRITES PIXELADOS
#
# En lugar de cargar imágenes externas, dibujamos cada sprite
# directamente con rectángulos, dando el look retro clásico.
# ─────────────────────────────────────────────────────────────

def draw_player(surface, x, y, color):
    """
    Dibuja la nave del jugador como una forma de cohete simple:
      - Base rectangular
      - Cuerpo central
      - Cañón superior
    """
    cx = x + PLAYER_W // 2
    # Base
    pygame.draw.rect(surface, color, (x, y + 18, PLAYER_W, 10))
    # Cuerpo
    pygame.draw.rect(surface, color, (cx - 10, y + 8, 20, 12))
    # Cañón
    pygame.draw.rect(surface, color, (cx - 3,  y,     6,  10))
    # Alas
    pygame.draw.rect(surface, color, (x,       y + 14, 14, 6))
    pygame.draw.rect(surface, color, (x + PLAYER_W - 14, y + 14, 14, 6))


def draw_alien(surface, x, y, row, frame, color):
    """
    Dibuja un alien pixelado. Hay 3 diseños según la fila.
    'frame' alterna entre 0 y 1 para la animación de 2 poses.

    row 0        → alien tipo A (puntero, el más valioso)
    row 1, 2     → alien tipo B
    row 3, 4     → alien tipo C (el más común)
    """
    cx = x + ALIEN_W // 2
    cy = y + ALIEN_H // 2

    if row == 0:
        # ── Tipo A: medusa ──
        pygame.draw.ellipse(surface, color, (cx-10, y+2, 20, 14))
        pygame.draw.rect(surface, color, (cx-14, y+10, 28, 8))
        if frame == 0:
            pygame.draw.rect(surface, color, (cx-14, y+18, 6, 6))
            pygame.draw.rect(surface, color, (cx-4,  y+18, 8, 6))
            pygame.draw.rect(surface, color, (cx+8,  y+18, 6, 6))
        else:
            pygame.draw.rect(surface, color, (cx-12, y+18, 6, 8))
            pygame.draw.rect(surface, color, (cx-2,  y+18, 6, 6))
            pygame.draw.rect(surface, color, (cx+8,  y+18, 6, 8))

    elif row in (1, 2):
        # ── Tipo B: cangrejo ──
        pygame.draw.rect(surface, color, (cx-10, y+4, 20, 16))
        pygame.draw.rect(surface, color, (cx-14, y+8, 28, 8))
        # Ojos
        pygame.draw.rect(surface, COLOR_BG, (cx-8, y+6, 4, 4))
        pygame.draw.rect(surface, COLOR_BG, (cx+4, y+6, 4, 4))
        if frame == 0:
            pygame.draw.rect(surface, color, (cx-18, y+4,  6, 8))
            pygame.draw.rect(surface, color, (cx+12,  y+4,  6, 8))
            pygame.draw.rect(surface, color, (cx-12, y+18, 6, 6))
            pygame.draw.rect(surface, color, (cx+6,  y+18, 6, 6))
        else:
            pygame.draw.rect(surface, color, (cx-18, y+8,  6, 8))
            pygame.draw.rect(surface, color, (cx+12,  y+8,  6, 8))
            pygame.draw.rect(surface, color, (cx-14, y+18, 6, 6))
            pygame.draw.rect(surface, color, (cx+8,  y+18, 6, 6))

    else:
        # ── Tipo C: pulpo ──
        pygame.draw.rect(surface, color, (cx-12, y+2, 24, 18))
        pygame.draw.rect(surface, color, (cx-8,  y,   16,  4))
        # Ojos
        pygame.draw.rect(surface, COLOR_BG, (cx-8, y+5, 5, 5))
        pygame.draw.rect(surface, COLOR_BG, (cx+3, y+5, 5, 5))
        if frame == 0:
            pygame.draw.rect(surface, color, (cx-16, y+8,  6, 10))
            pygame.draw.rect(surface, color, (cx+10, y+8,  6, 10))
            for i, ox in enumerate([-12, -4, 4, 10]):
                pygame.draw.rect(surface, color, (cx+ox, y+18, 4, 6 if i%2==0 else 8))
        else:
            pygame.draw.rect(surface, color, (cx-16, y+10, 6, 10))
            pygame.draw.rect(surface, color, (cx+10, y+10, 6, 10))
            for i, ox in enumerate([-12, -4, 4, 10]):
                pygame.draw.rect(surface, color, (cx+ox, y+18, 4, 8 if i%2==0 else 6))


def draw_mystery_ship(surface, x, y, color):
    """Dibuja el alien misterioso como un OVNI clásico."""
    cx = x + MYSTERY_W // 2
    pygame.draw.ellipse(surface, color, (x, y + 8, MYSTERY_W, 14))
    pygame.draw.ellipse(surface, color, (cx-18, y, 36, 16))
    # Ventanillas
    for ox in [-10, 0, 10]:
        pygame.draw.circle(surface, COLOR_BG, (cx + ox, y + 8), 3)


# ─────────────────────────────────────────────────────────────
# CLASE: Bullet
#
# Representa un proyectil — tanto del jugador como de los aliens.
# ─────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, dy, color):
        """
        x, y  : posición inicial
        dy    : velocidad vertical (negativo = sube, positivo = baja)
        color : distingue bala del jugador vs enemiga
        """
        self.rect  = pygame.Rect(x - BULLET_W//2, y, BULLET_W, BULLET_H)
        self.dy    = dy
        self.color = color
        self.alive = True

    def update(self):
        """Mueve la bala y la elimina si sale de la pantalla."""
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


# ─────────────────────────────────────────────────────────────
# CLASE: Alien
#
# Un alien individual con su posición, tipo (fila) y estado.
# ─────────────────────────────────────────────────────────────
class Alien:
    def __init__(self, row, col, x, y):
        self.row   = row          # Fila (determina tipo y puntos)
        self.col   = col          # Columna en la rejilla
        self.x     = float(x)
        self.y     = float(y)
        self.alive = True
        self.points = ALIEN_POINTS[row]
        # Color degradado según la fila: arriba más cálido
        r = 80  + row * 30
        g = 255 - row * 40
        b = 80
        self.color = (min(r,255), max(g,80), b)

    @property
    def rect(self):
        """Hitbox calculada en tiempo real desde la posición float."""
        return pygame.Rect(int(self.x), int(self.y), ALIEN_W, ALIEN_H)

    def draw(self, surface, frame):
        if self.alive:
            draw_alien(surface, int(self.x), int(self.y),
                       self.row, frame, self.color)


# ─────────────────────────────────────────────────────────────
# CLASE: Bunker
#
# Estructura de protección representada como una cuadrícula
# de bloques pequeños que se van destruyendo al recibir impactos.
# ─────────────────────────────────────────────────────────────
class Bunker:
    # Máscara de forma del bunker (1 = bloque presente, 0 = hueco)
    # 8 columnas × 6 filas
    SHAPE = [
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,0,0,0,0,1,1],
        [1,1,0,0,0,0,1,1],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Copiamos la máscara para poder destruir bloques individualmente
        self.grid = [row[:] for row in self.SHAPE]

    def cell_size(self):
        """Tamaño en píxeles de cada bloque del bunker."""
        return BUNKER_W // BUNKER_COLS, BUNKER_H // BUNKER_ROWS

    def get_rects(self):
        """
        Genera todos los rectángulos de bloques activos.
        Retorna lista de (pygame.Rect, fila, col) para poder
        destruirlos al recibir un impacto.
        """
        cw, ch = self.cell_size()
        rects = []
        for r in range(BUNKER_ROWS):
            for c in range(BUNKER_COLS):
                if self.grid[r][c]:
                    rx = self.x + c * cw
                    ry = self.y + r * ch
                    rects.append((pygame.Rect(rx, ry, cw, ch), r, c))
        return rects

    def hit(self, bullet_rect):
        """
        Verifica si una bala colisiona con algún bloque.
        Si choca, destruye el bloque y retorna True.
        """
        for rect, r, c in self.get_rects():
            if rect.colliderect(bullet_rect):
                self.grid[r][c] = 0
                return True
        return False

    def draw(self, surface):
        cw, ch = self.cell_size()
        for rect, r, c in self.get_rects():
            pygame.draw.rect(surface, COLOR_BUNKER, rect)
            # Borde oscuro para efecto pixelado
            pygame.draw.rect(surface, (0, 100, 0), rect, 1)


# ─────────────────────────────────────────────────────────────
# CLASE: MysteryShip
#
# El alien misterioso que cruza la pantalla periódicamente.
# Al destruirlo da una cantidad aleatoria de puntos extra.
# ─────────────────────────────────────────────────────────────
class MysteryShip:
    def __init__(self):
        self.active = False
        self.x      = 0.0
        self.y      = HUD_HEIGHT + 10
        self.dir    = 1    # 1 = izquierda→derecha, -1 = derecha→izquierda
        self.points = random.choice(MYSTERY_POINTS_OPTIONS)

    def spawn(self):
        """Hace aparecer la nave desde un borde aleatorio."""
        self.dir    = random.choice([-1, 1])
        self.x      = -MYSTERY_W if self.dir == 1 else SCREEN_WIDTH
        self.active = True
        self.points = random.choice(MYSTERY_POINTS_OPTIONS)

    def update(self):
        if not self.active:
            return
        self.x += self.dir * MYSTERY_SPEED
        # Desaparece al salir por el otro borde
        if self.x > SCREEN_WIDTH or self.x + MYSTERY_W < 0:
            self.active = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), MYSTERY_W, MYSTERY_H)

    def draw(self, surface):
        if self.active:
            draw_mystery_ship(surface, int(self.x), int(self.y), COLOR_MYSTERY)


# ─────────────────────────────────────────────────────────────
# CLASE: StarField
#
# Fondo de estrellas animadas para dar sensación de movimiento.
# ─────────────────────────────────────────────────────────────
class StarField:
    def __init__(self, count=80):
        # Genera estrellas en posiciones y velocidades aleatorias
        self.stars = [
            [random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.uniform(0.2, 1.2),           # velocidad
             random.randint(1, 3)]                # tamaño
            for _ in range(count)
        ]

    def update(self):
        """Las estrellas bajan lentamente (efecto parallax)."""
        for s in self.stars:
            s[1] += s[2]
            if s[1] > SCREEN_HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for x, y, speed, size in self.stars:
            brightness = int(100 + speed * 100)
            color = (brightness, brightness, brightness)
            pygame.draw.rect(surface, color, (int(x), int(y), size, size))


# ─────────────────────────────────────────────────────────────
# CLASE: Explosion
#
# Partículas de explosión al destruir un alien.
# Se crean en el punto de impacto y desaparecen con el tiempo.
# ─────────────────────────────────────────────────────────────
class Explosion:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(12):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 4)
            self.particles.append({
                "x": float(x), "y": float(y),
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "life": random.randint(15, 30),
                "color": color,
            })

    def update(self):
        for p in self.particles:
            p["x"]    += p["dx"]
            p["y"]    += p["dy"]
            p["life"] -= 1

    @property
    def alive(self):
        return any(p["life"] > 0 for p in self.particles)

    def draw(self, surface):
        for p in self.particles:
            if p["life"] > 0:
                alpha = max(0, p["life"] * 8)
                size  = max(1, p["life"] // 8)
                pygame.draw.rect(surface, p["color"],
                                 (int(p["x"]), int(p["y"]), size, size))


# ─────────────────────────────────────────────────────────────
# CLASE: Game
#
# Orquesta toda la lógica:
#   - Creación y movimiento de la horda de aliens
#   - Disparo del jugador y de los aliens
#   - Colisiones (balas ↔ aliens, balas ↔ bunkers, aliens ↔ jugador)
#   - Progresión de oleadas y Game Over
# ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.stars   = StarField()
        self.font_lg = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 13)
        self.reset()

    # ── Inicialización / reset ────────────────────────────────

    def reset(self):
        """Reinicia el estado para una nueva partida."""
        self.score      = 0
        self.lives      = LIVES_START
        self.wave       = 1
        self.paused     = False
        self.game_over  = False
        self.won        = False

        # Nave del jugador (posición y hitbox)
        self.player_x  = float(SCREEN_WIDTH // 2 - PLAYER_W // 2)
        self.player_y  = float(SCREEN_HEIGHT - HUD_HEIGHT - PLAYER_H - 10)
        self.player_speed = 4.0
        self.invincible   = 0   # Frames de invencibilidad tras ser golpeado

        # Balas
        self.player_bullet  = None   # Solo 1 bala del jugador a la vez
        self.enemy_bullets  = []
        self.shoot_cooldown = 0      # Frames hasta que el jugador puede volver a disparar

        # Aliens
        self._create_aliens()

        # Bunkers
        self._create_bunkers()

        # Alien misterioso
        self.mystery      = MysteryShip()
        self.mystery_timer = 0

        # Efectos visuales
        self.explosions   = []
        self.score_popups = []   # Puntos flotantes al destruir un alien

        # Animación de aliens: cambian de pose cada N frames
        self.anim_frame   = 0
        self.anim_timer   = 0
        self.anim_interval = 30   # Frames entre cambio de pose

        # Movimiento de aliens
        self.alien_dir    = 1     # 1 = derecha, -1 = izquierda
        self.alien_step_x = 0.0  # Acumulador de movimiento horizontal
        self.alien_drop   = False # Indica si deben bajar en este tick
        self._update_alien_speed()

        # Cadencia de disparo enemigo
        self.enemy_shoot_timer    = 0
        self.enemy_shoot_interval = 80   # Frames entre disparos enemigos

    def _create_aliens(self):
        """Crea la cuadrícula inicial de aliens."""
        self.aliens = []
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                x = ALIEN_X0 + col * ALIEN_GAP_X
                y = ALIEN_Y0 + row * ALIEN_GAP_Y
                self.aliens.append(Alien(row, col, x, y))

    def _create_bunkers(self):
        """Distribuye los bunkers equidistantes en la pantalla."""
        self.bunkers = []
        spacing = SCREEN_WIDTH // (BUNKER_COUNT + 1)
        for i in range(BUNKER_COUNT):
            bx = spacing * (i + 1) - BUNKER_W // 2
            self.bunkers.append(Bunker(bx, BUNKER_Y))

    def _update_alien_speed(self):
        """
        Ajusta la velocidad horizontal de los aliens según cuántos
        quedan vivos. Cuanto menos aliens, más rápido se mueven.
        Además, cada oleada empieza un poco más rápido.
        """
        alive = sum(1 for a in self.aliens if a.alive)
        alive = max(1, alive)
        # Base speed aumenta con la oleada
        base    = 0.3 + (self.wave - 1) * 0.1
        # Acelera conforme hay menos aliens
        factor  = 1 + (ALIEN_COLS * ALIEN_ROWS - alive) * 0.03
        self.alien_speed_x = base * factor

    # ── Lógica de movimiento de aliens ───────────────────────

    def _move_aliens(self):
        """
        Mueve la horda de aliens en bloque:
          1. Suma el desplazamiento horizontal.
          2. Si algún alien toca el borde, invierte la dirección
             y activa la bandera de descenso.
          3. Si debe bajar, desplaza todos los aliens hacia abajo.
        """
        alive_aliens = [a for a in self.aliens if a.alive]
        if not alive_aliens:
            return

        # 1. Calcular los límites actuales de la horda
        left_edge  = min(a.x for a in alive_aliens)
        right_edge = max(a.x + ALIEN_W for a in alive_aliens)

        # 2. Detectar colisión con bordes
        drop = False
        if self.alien_dir == 1 and right_edge + self.alien_speed_x >= SCREEN_WIDTH - 10:
            self.alien_dir = -1
            drop = True
        elif self.alien_dir == -1 and left_edge - self.alien_speed_x <= 10:
            self.alien_dir = 1
            drop = True

        # 3. Mover todos los aliens
        for a in alive_aliens:
            a.x += self.alien_dir * self.alien_speed_x
            if drop:
                a.y += 20   # Descenso fijo al rebotar en el borde

        self._update_alien_speed()

    # ── Lógica de disparo ─────────────────────────────────────

    def _player_shoot(self):
        """El jugador dispara si no hay bala activa y el cooldown terminó."""
        if self.player_bullet is None and self.shoot_cooldown <= 0:
            cx = int(self.player_x) + PLAYER_W // 2
            self.player_bullet = Bullet(cx,
                                        int(self.player_y),
                                        dy=-10,
                                        color=COLOR_BULLET_P)
            self.shoot_cooldown = 20

    def _enemy_shoot(self):
        """
        Un alien aleatorio de la columna más baja de cada columna
        dispara hacia abajo. Simula el comportamiento del original:
        solo los aliens del frente pueden disparar.
        """
        self.enemy_shoot_timer += 1
        if self.enemy_shoot_timer < self.enemy_shoot_interval:
            return
        self.enemy_shoot_timer = 0

        # Construir diccionario col → alien más bajo vivo
        shooters = {}
        for a in self.aliens:
            if a.alive:
                if a.col not in shooters or a.row > shooters[a.col].row:
                    shooters[a.col] = a

        if not shooters:
            return

        # Elegir uno al azar
        shooter = random.choice(list(shooters.values()))
        cx = int(shooter.x) + ALIEN_W // 2
        self.enemy_bullets.append(
            Bullet(cx, int(shooter.y) + ALIEN_H, dy=5, color=COLOR_BULLET_E)
        )
        # Aumentar cadencia con la oleada (min 40 frames)
        self.enemy_shoot_interval = max(40, 80 - self.wave * 5)

    # ── Detección de colisiones ───────────────────────────────

    def _check_collisions(self):
        """
        Verifica y resuelve todas las colisiones:
          1. Bala del jugador vs aliens
          2. Bala del jugador vs alien misterioso
          3. Bala del jugador vs bunkers
          4. Balas enemigas vs bunkers
          5. Balas enemigas vs jugador
          6. Aliens que alcanzan la tierra (línea del jugador)
        """
        # 1. Bala del jugador vs aliens
        if self.player_bullet:
            for a in self.aliens:
                if a.alive and a.rect.colliderect(self.player_bullet.rect):
                    a.alive = False
                    self.score += a.points * self.wave
                    self.explosions.append(Explosion(
                        a.x + ALIEN_W//2, a.y + ALIEN_H//2, a.color))
                    self._add_popup(a.points * self.wave,
                                    int(a.x), int(a.y))
                    self.player_bullet.alive = False
                    self.player_bullet = None
                    self._update_alien_speed()
                    break

        # 2. Bala del jugador vs alien misterioso
        if self.player_bullet and self.mystery.active:
            if self.mystery.rect.colliderect(self.player_bullet.rect):
                self.score += self.mystery.points
                self.explosions.append(Explosion(
                    self.mystery.x + MYSTERY_W//2,
                    self.mystery.y + MYSTERY_H//2,
                    COLOR_MYSTERY))
                self._add_popup(self.mystery.points,
                                int(self.mystery.x), int(self.mystery.y))
                self.mystery.active = False
                self.player_bullet.alive = False
                self.player_bullet = None

        # 3. Bala del jugador vs bunkers
        if self.player_bullet:
            for b in self.bunkers:
                if b.hit(self.player_bullet.rect):
                    self.player_bullet.alive = False
                    self.player_bullet = None
                    break

        # 4. Balas enemigas vs bunkers
        for bullet in self.enemy_bullets:
            if not bullet.alive:
                continue
            for b in self.bunkers:
                if b.hit(bullet.rect):
                    bullet.alive = False
                    break

        # 5. Balas enemigas vs jugador
        player_rect = pygame.Rect(int(self.player_x), int(self.player_y),
                                  PLAYER_W, PLAYER_H)
        if self.invincible <= 0:
            for bullet in self.enemy_bullets:
                if bullet.alive and bullet.rect.colliderect(player_rect):
                    bullet.alive = False
                    self._player_hit()
                    break

        # 6. Aliens que alcanzan la línea del jugador → Game Over
        for a in self.aliens:
            if a.alive and a.y + ALIEN_H >= self.player_y:
                self.game_over = True
                return

    def _player_hit(self):
        """El jugador pierde una vida; si llega a 0, Game Over."""
        self.lives -= 1
        self.explosions.append(Explosion(
            int(self.player_x) + PLAYER_W//2,
            int(self.player_y) + PLAYER_H//2,
            COLOR_PLAYER))
        if self.lives <= 0:
            self.game_over = True
        else:
            # Invencibilidad temporal para no perder varias vidas de golpe
            self.invincible = 120

    def _add_popup(self, points, x, y):
        """Agrega un texto flotante de puntos que sube y desaparece."""
        self.score_popups.append({"x": x, "y": float(y),
                                  "text": f"+{points}", "life": 50})

    # ── Gestión de oleadas ────────────────────────────────────

    def _check_wave(self):
        """Si no quedan aliens vivos, inicia la siguiente oleada."""
        if all(not a.alive for a in self.aliens):
            self.wave += 1
            self._create_aliens()
            self._create_bunkers()
            self.mystery_timer = 0
            self._update_alien_speed()

    # ── Loop de actualización ─────────────────────────────────

    def update(self, keys):
        if self.paused or self.game_over:
            return

        self.stars.update()

        # Temporizador de invencibilidad
        if self.invincible > 0:
            self.invincible -= 1

        # ── Movimiento del jugador ──
        if keys[pygame.K_LEFT]:
            self.player_x = max(0, self.player_x - self.player_speed)
        if keys[pygame.K_RIGHT]:
            self.player_x = min(SCREEN_WIDTH - PLAYER_W,
                                self.player_x + self.player_speed)

        # ── Cooldown de disparo ──
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # ── Bala del jugador ──
        if self.player_bullet:
            self.player_bullet.update()
            if not self.player_bullet.alive:
                self.player_bullet = None

        # ── Balas enemigas ──
        for b in self.enemy_bullets:
            b.update()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        # ── Animación de aliens ──
        self.anim_timer += 1
        if self.anim_timer >= self.anim_interval:
            self.anim_timer = 0
            self.anim_frame = 1 - self.anim_frame   # Alterna 0 ↔ 1

        # ── Movimiento y disparo de aliens ──
        self._move_aliens()
        self._enemy_shoot()

        # ── Alien misterioso ──
        self.mystery_timer += 1
        if self.mystery_timer >= MYSTERY_INTERVAL and not self.mystery.active:
            self.mystery.spawn()
            self.mystery_timer = 0
        self.mystery.update()

        # ── Colisiones ──
        self._check_collisions()

        # ── Efectos ──
        for exp in self.explosions:
            exp.update()
        self.explosions = [e for e in self.explosions if e.alive]

        for p in self.score_popups:
            p["y"]   -= 0.8
            p["life"] -= 1
        self.score_popups = [p for p in self.score_popups if p["life"] > 0]

        # ── Siguiente oleada ──
        self._check_wave()

    # ── Renderizado ───────────────────────────────────────────

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.stars.draw(surface)

        # HUD superior (puntaje, vidas, oleada)
        self._draw_hud(surface)

        # Bunkers
        for b in self.bunkers:
            b.draw(surface)

        # Aliens
        for a in self.aliens:
            a.draw(surface, self.anim_frame)

        # Alien misterioso
        self.mystery.draw(surface)

        # Nave del jugador (parpadea si es invencible)
        if self.invincible == 0 or (self.invincible // 6) % 2 == 0:
            draw_player(surface,
                        int(self.player_x), int(self.player_y),
                        COLOR_PLAYER)

        # Balas
        if self.player_bullet:
            self.player_bullet.draw(surface)
        for b in self.enemy_bullets:
            b.draw(surface)

        # Efectos
        for exp in self.explosions:
            exp.draw(surface)

        # Puntos flotantes
        for p in self.score_popups:
            alpha = min(255, p["life"] * 8)
            txt = self.font_sm.render(p["text"], True,
                                      (255, 255, 100))
            surface.blit(txt, (p["x"], int(p["y"])))

        # Línea del suelo
        pygame.draw.line(surface, (60, 60, 100),
                         (0, SCREEN_HEIGHT - HUD_HEIGHT),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT), 1)

        # Overlays
        if self.paused:
            self._draw_overlay(surface, "PAUSA", "(P) continuar")
        elif self.game_over:
            self._draw_overlay(surface, "GAME OVER",
                               f"Puntaje: {self.score}   (R) reiniciar")

    def _draw_hud(self, surface):
        """Barra superior con puntaje, oleada y vidas."""
        # Puntaje
        score_txt = self.font_md.render(f"Score  {self.score:06d}", True, COLOR_TITLE)
        surface.blit(score_txt, (10, 6))

        # Oleada
        wave_txt = self.font_md.render(f"Oleada {self.wave}", True, COLOR_HUD)
        surface.blit(wave_txt, (SCREEN_WIDTH//2 - wave_txt.get_width()//2, 6))

        # Vidas (dibujamos miniaturas de la nave)
        lives_lbl = self.font_sm.render("Vidas:", True, COLOR_HUD)
        surface.blit(lives_lbl, (SCREEN_WIDTH - 160, 8))
        for i in range(self.lives):
            draw_player(surface,
                        SCREEN_WIDTH - 110 + i * 34, 4,
                        COLOR_PLAYER)

    def _draw_overlay(self, surface, title, subtitle):
        """Overlay semitransparente para pausa y Game Over."""
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        surface.blit(ov, (0, 0))

        t1 = self.font_lg.render(title, True, (255, 80, 80))
        surface.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2,
                          SCREEN_HEIGHT//2 - 40))
        t2 = self.font_sm.render(subtitle, True, COLOR_TEXT)
        surface.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2,
                          SCREEN_HEIGHT//2 + 10))


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Space Invaders – Python")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    game = Game()

    while True:
        # ── Eventos ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r:
                    game.reset()

                if event.key == pygame.K_p and not game.game_over:
                    game.paused = not game.paused

                if event.key == pygame.K_SPACE:
                    if not game.paused and not game.game_over:
                        game._player_shoot()

        # ── Actualización ──
        keys = pygame.key.get_pressed()
        game.update(keys)

        # ── Renderizado ──
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
