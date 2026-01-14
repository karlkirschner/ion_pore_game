import asyncio
import pygame
import math
import random


# --- Configuration & Global Helpers ---
async def game():
    # --- Configuration ---
    WIDTH, HEIGHT = 800, 600
    ION_SPEED = -5
    PLAYER_SPEED = 7
    FPS = 60
    MEMBRANE_Y = 250
    MEMBRANE_THICKNESS = 30

    # Colors
    HBRSblue = (0, 158, 224)
    HBRSgreen = (50, 100, 50)
    HBRSred = (199, 51, 38)
    HBRSgray = (168, 175, 175)
    HBRSlightgray = (240, 240, 240)
    BLUE = (0, 32, 229)
    CYAN = (100, 255, 255)
    GOLD = (255, 215, 0)
    ORANGE = (255, 165, 0)
    EXTRACELLULAR_BG = HBRSblue
    MEMBRANE_COLOR = ORANGE
    PORE_COLOR = HBRSlightgray

    class Player:
        def __init__(self):
            self.rect = pygame.Rect(WIDTH // 3, HEIGHT - 50, 40, 20)

        def move(self, keys):
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += PLAYER_SPEED

    # Define Ion Properties
    radius_ratio = 7
    ION_TYPES = {
        "sodium": {"color": (0, 32, 229), "size": 1.0 * radius_ratio, "speed": -6},
        "calcium": {"color": (255, 255, 100), "size": 1.0 * radius_ratio, "speed": -5},
        "potassium": {"color": (150, 100, 255), "size": 1.4 * radius_ratio, "speed": -4},
        "chloride": {"color": (34, 139, 34), "size": 1.8 * radius_ratio, "speed": -2},
    }

    class Ion:
        def __init__(self, x, y, ion_type="sodium"):
            properties = ION_TYPES[ion_type]
            self.size = properties["size"]
            self.rect = pygame.Rect(x - self.size // 2, y, self.size, self.size)
            self.vx = 0
            self.vy = properties["speed"]
            self.color = properties["color"]
            self.has_passed = False

        def update(self):
            self.rect.x += self.vx
            self.rect.y += self.vy

    class Pore:
        def __init__(self, x, speed):
            self.x = x
            self.timer = random.uniform(0, 5)
            self.speed = speed
            self.base_gap = 45
            self.amplitude = 35
            self.current_gap = 45

        def update(self):
            self.timer += self.speed
            self.current_gap = self.base_gap + math.sin(self.timer) * self.amplitude

    def draw_text(surface, text, size, x, y, color=(255, 255, 255), center=True):
        font = pygame.font.SysFont("Arial", size, bold=True)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)

    # --- Initialization ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cellular Ion Flux Simulator")
    clock = pygame.time.Clock()

    player = Player()
    pores = [Pore(200, 0.04), Pore(400, 0.07), Pore(600, 0.03)]
    ions = []

    # --- Counters ---
    intracellular_count = 0
    missed_shots = 0
    leaked_out = 0
    total_fired = 0
    game_state = "MENU"

    # Load Assets (Try/Except for web safety)
    try:
        nachr_image = pygame.image.load("complete.png")
        nx, ny = nachr_image.get_size()
        nachr_image = pygame.transform.scale(nachr_image, (nx / 3, ny / 3))
    except:
        nachr_image = None

    running = True
    while running:
        # --- CRITICAL FOR PYGBAG ---
        # This await allows the browser to process events without freezing
        await asyncio.sleep(0)

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU" and event.key == pygame.K_RETURN:
                    game_state = "PLAY"
                elif game_state == "PLAY" and event.key == pygame.K_SPACE:
                    ions.append(Ion(player.rect.centerx, player.rect.top))
                    total_fired += 1

        if game_state == "MENU":
            screen.fill((10, 10, 25))
            draw_text(screen, "CytoTransport Simulator Game", 50, WIDTH // 2, HEIGHT // 2 - 170, HBRSblue)
            draw_text(screen, "Ions Passing Through a Cell Membrane", 25, WIDTH // 2, HEIGHT // 2 - 125, HBRSblue)
            draw_text(screen, "by K.N. Kirschner, H-BRS", 15, WIDTH // 2, HEIGHT // 2 - 80, HBRSlightgray)

            pygame.draw.rect(screen, (40, 40, 60), (WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 120), border_radius=10)
            draw_text(screen, "CONTROLS", 24, WIDTH // 2, HEIGHT // 2 + 35, HBRSblue)
            draw_text(screen, "ARROWS: Move Launcher", 18, WIDTH // 2, HEIGHT // 2 + 65)
            draw_text(screen, "SPACE: Launch Ion", 18, WIDTH // 2, HEIGHT // 2 + 90)

            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
            start_color = (0, 158, int(224 * pulse))
            draw_text(screen, "PRESS ENTER TO BEGIN", 28, WIDTH // 2, HEIGHT // 2 + 180, start_color)

            if nachr_image:
                screen.blit(nachr_image, (30, 220))

        elif game_state == "PLAY":
            intensity = min(intracellular_count * 5, 150)
            red_channel = min(200 + intensity, 255)
            gb_channels = max(200 - intensity, 50)
            intracellular_bg = (red_channel, gb_channels, gb_channels)

            screen.fill(EXTRACELLULAR_BG)
            pygame.draw.rect(screen, intracellular_bg, (0, 0, WIDTH, MEMBRANE_Y + (MEMBRANE_THICKNESS // 2)))

            keys = pygame.key.get_pressed()
            player.move(keys)
            pygame.draw.rect(screen, HBRSred, player.rect)

            # --- MEMBRANE & PORES ---
            for p in pores:
                p.update()

            current_x = 0
            sorted_pores = sorted(pores, key=lambda p: p.x)
            for p in sorted_pores:
                gap_left = p.x - p.current_gap / 2
                if gap_left > current_x:
                    pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y, gap_left - current_x, MEMBRANE_THICKNESS))
                current_x = p.x + p.current_gap / 2
            if current_x < WIDTH:
                pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y, WIDTH - current_x, MEMBRANE_THICKNESS))

            # --- PORE LIPS ---
            lip_y_top = MEMBRANE_Y - 8
            lip_y_bottom = MEMBRANE_Y + MEMBRANE_THICKNESS + 8
            lip_w_outer, lip_w_inner = 18, 6

            for p in pores:
                gl, gr = p.x - p.current_gap / 2, p.x + p.current_gap / 2
                pygame.draw.polygon(
                    screen,
                    PORE_COLOR,
                    [(gl - lip_w_outer, lip_y_bottom), (gl, lip_y_bottom), (gl, lip_y_top), (gl - lip_w_inner, lip_y_top)],
                )
                pygame.draw.polygon(
                    screen,
                    PORE_COLOR,
                    [(gr, lip_y_bottom), (gr + lip_w_outer, lip_y_bottom), (gr + lip_w_inner, lip_y_top), (gr, lip_y_top)],
                )

            # --- ION PHYSICS ---
            pressure_multiplier = 1.0 + (intracellular_count / 25.0)

            for ion in ions[:]:
                ion.update()
                pygame.draw.circle(screen, ion.color, ion.rect.center, ion.size)

                if not ion.has_passed:
                    if MEMBRANE_Y <= ion.rect.centery <= MEMBRANE_Y + MEMBRANE_THICKNESS:
                        is_safe = any((p.x - p.current_gap / 2) < ion.rect.centerx < (p.x + p.current_gap / 2) for p in pores)
                        if not is_safe:
                            missed_shots += 1
                            ion.vy = abs(ion.vy)
                            ion.vx = random.uniform(-2, 2)
                            ion.rect.top = MEMBRANE_Y + MEMBRANE_THICKNESS + 1
                    elif ion.rect.bottom < MEMBRANE_Y:
                        ion.has_passed = True
                        intracellular_count += 1
                        ion.color = (100, 255, 255)
                        ion.vx, ion.vy = random.uniform(-2, 2), random.uniform(-2, -1)
                else:
                    if ion.rect.left <= 0 or ion.rect.right >= WIDTH:
                        ion.vx *= -1 * pressure_multiplier
                        ion.vx = max(min(ion.vx, 15), -15)  # Cap velocity to avoid inifity
                    if ion.rect.top <= 0:
                        ion.vy *= -1 * pressure_multiplier
                        ion.vy = max(min(ion.vy, 15), -15)

                    if MEMBRANE_Y <= ion.rect.bottom <= MEMBRANE_Y + (MEMBRANE_THICKNESS / 2):
                        is_in_gap = any((p.x - p.current_gap / 2) < ion.rect.centerx < (p.x + p.current_gap / 2) for p in pores)
                        if is_in_gap:
                            ion.has_passed = False
                            ion.color = (255, 215, 0)
                            ion.vx, ion.vy = random.uniform(-1, 1), 5
                            intracellular_count -= 1
                            leaked_out += 1
                        else:
                            ion.vy *= -1
                            ion.rect.bottom = MEMBRANE_Y - 1

                if ion.rect.top > HEIGHT:
                    ions.remove(ion)

            # --- UI ---
            ui_bg = pygame.Surface((300, 155), pygame.SRCALPHA)
            ui_bg.fill((30, 30, 30, 150))
            screen.blit(ui_bg, (10, 10))
            draw_text(screen, f"Intracellular Count: {intracellular_count}", 18, 20, 20, (100, 255, 255), False)
            draw_text(screen, f"Blocked (Bounced): {missed_shots}", 18, 20, 45, (255, 100, 100), False)
            draw_text(screen, f"Efflux (Leaked): {leaked_out}", 18, 20, 70, (255, 200, 100), False)
            draw_text(screen, f"Total Fired: {total_fired}", 18, 20, 95, (255, 255, 255), False)
            draw_text(screen, f"Pressure Factor: {pressure_multiplier:.2f}x", 18, 20, 120, (200, 150, 255), False)

        pygame.display.flip()
        clock.tick(FPS)


# This is the standard entry point for pygbag
asyncio.run(game())
