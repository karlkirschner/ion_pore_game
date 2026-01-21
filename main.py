import asyncio
import pygame
import math
import random


async def game():
    # --- Configuration ---
    WIDTH, HEIGHT = 800, 600
    PLAYER_SPEED = 7
    FPS = 60
    MEMBRANE_Y = 250
    MEMBRANE_THICKNESS = 30

    # Colors
    HBRSblue = (0, 158, 224)
    HBRSred = (199, 51, 38)
    HBRSlightgray = (240, 240, 240)
    ORANGE = (255, 165, 0)
    EXTRACELLULAR_BG = HBRSblue
    MEMBRANE_COLOR = ORANGE
    PORE_COLOR = HBRSlightgray

    radius_ratio = 7
    ION_TYPES = {
        "sodium": {"color": (0, 32, 229), "size": 1.0 * radius_ratio, "speed": -6},
        "calcium": {"color": (255, 255, 100), "size": 1.0 * radius_ratio, "speed": -5},
        "potassium": {"color": (150, 100, 255), "size": 1.4 * radius_ratio, "speed": -4},
        "chloride": {"color": (34, 139, 34), "size": 1.8 * radius_ratio, "speed": -2},
    }

    class Player:
        def __init__(self):
            self.rect = pygame.Rect(WIDTH // 3, HEIGHT - 50, 40, 20)
            self.current_ion = "sodium"

        def move(self, keys):
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += PLAYER_SPEED

    class Ion:
        def __init__(self, x, y, ion_type="sodium"):
            properties = ION_TYPES[ion_type]
            self.size = int(properties["size"])
            self.rect = pygame.Rect(x - self.size // 2, y, self.size, self.size)
            self.base_speed = properties["speed"]
            self.vx = 0
            self.vy = self.base_speed
            self.color = properties["color"]
            self.type = ion_type
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
    intracellular_count, missed_shots, leaked_out, total_fired = 0, 0, 0, 0
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
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU" and event.key == pygame.K_RETURN:
                    game_state = "PLAY"
                elif game_state == "PLAY":
                    if event.key == pygame.K_SPACE:
                        ions.append(Ion(player.rect.centerx, player.rect.top, player.current_ion))
                        total_fired += 1
                    if event.key == pygame.K_1:
                        player.current_ion = "sodium"
                    if event.key == pygame.K_2:
                        player.current_ion = "potassium"
                    if event.key == pygame.K_3:
                        player.current_ion = "calcium"
                    if event.key == pygame.K_4:
                        player.current_ion = "chloride"

        if game_state == "MENU":
            screen.fill((10, 10, 25))
            draw_text(screen, "CytoTransport Simulator Game", 50, WIDTH // 2, HEIGHT // 2 - 170, HBRSblue)
            draw_text(screen, "Ions Passing Through a Cell Membrane", 25, WIDTH // 2, HEIGHT // 2 - 125, HBRSblue)
            draw_text(screen, "by K.N. Kirschner, H-BRS", 15, WIDTH // 2, HEIGHT // 2 - 80, HBRSlightgray)

            pygame.draw.rect(screen, (40, 40, 60), (WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 120), border_radius=10)
            draw_text(screen, "CONTROLS", 24, WIDTH // 2, HEIGHT // 2 + 35, HBRSblue)
            draw_text(screen, "ARROWS: Move Launcher", 18, WIDTH // 2, HEIGHT // 2 + 65)
            draw_text(screen, "SPACE: Launch Ion", 18, WIDTH // 2, HEIGHT // 2 + 90)
            draw_text(screen, "1, 2, 3 & 4: Ion Types", 18, WIDTH // 2, HEIGHT // 2 + 115)

            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
            start_color = (0, 158, int(224 * pulse))
            draw_text(screen, "PRESS ENTER TO BEGIN", 28, WIDTH // 2, HEIGHT // 2 + 180, start_color)

            if nachr_image:
                screen.blit(nachr_image, (30, 220))

        elif game_state == "PLAY":
            # --- SAFE COLOR MATH ---
            intensity = int(min(intracellular_count * 5, 150))
            red = int(min(200 + intensity, 255))
            gb = int(max(200 - intensity, 50))
            intracellular_bg = (red, gb, gb)

            screen.fill(EXTRACELLULAR_BG)
            pygame.draw.rect(screen, intracellular_bg, (0, 0, WIDTH, MEMBRANE_Y + (MEMBRANE_THICKNESS // 2)))

            keys = pygame.key.get_pressed()
            player.move(keys)

            # --- StATIC PLAYER COLOR ---
            # pygame.draw.rect(screen, HBRSred, player.rect)

            # --- DYNAMIC PLAYER COLOR ---
            # Color of the current ion
            player_color = ION_TYPES[player.current_ion]["color"]

            # Draw the player using that specific color instead of HBRSred
            pygame.draw.rect(screen, player_color, player.rect)

            # Optional: Add a border so the player is still visible
            # if the background color matches the ion color
            pygame.draw.rect(screen, (255, 255, 255), player.rect, 2)

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

            # --- PROTEIN WEDGES ---
            lip_y_top, lip_y_bottom = MEMBRANE_Y, MEMBRANE_Y + MEMBRANE_THICKNESS
            taper_amount = 6
            # This is how far the protein "back" extends into the orange lipid
            protein_length = 35
            protein_width = 15
            for p in pores:
                gl, gr = p.x - p.current_gap / 2, p.x + p.current_gap / 2
                pygame.draw.rect(screen, intracellular_bg, (gl, MEMBRANE_Y, p.current_gap, 15))
                pygame.draw.rect(screen, EXTRACELLULAR_BG, (gl, MEMBRANE_Y, p.current_gap, 15))
                l_wedge = [
                    (gl, lip_y_bottom),
                    (gl - protein_width, lip_y_bottom),
                    (gl - protein_width, lip_y_top),
                    (gl + taper_amount, lip_y_top),
                ]
                r_wedge = [
                    (gr, lip_y_bottom),
                    (gr + protein_width, lip_y_bottom),
                    (gr + protein_width, lip_y_top),
                    (gr - taper_amount, lip_y_top),
                ]

                pygame.draw.polygon(screen, PORE_COLOR, l_wedge)
                pygame.draw.polygon(screen, PORE_COLOR, r_wedge)

            # --- PHYSICS ---
            pressure_multiplier = 1.0 + (intracellular_count / 25.0)

            for ion in ions[:]:
                ion.update()
                pygame.draw.circle(screen, ion.color, ion.rect.center, ion.size // 2)

                if not ion.has_passed:
                    # Collision check at membrane level
                    if MEMBRANE_Y <= ion.rect.top <= MEMBRANE_Y + MEMBRANE_THICKNESS:
                        can_pass = False
                        for p in pores:
                            # Steric Hindrance check
                            taper_buffer = 6
                            effective_gap_left = (p.x - p.current_gap / 2) + taper_buffer
                            effective_gap_right = (p.x + p.current_gap / 2) - taper_buffer

                            if ion.rect.left > effective_gap_left and ion.rect.right < effective_gap_right:
                                can_pass = True

                        # FIX: Only increment missed_shots if the ion is still moving UP
                        if not can_pass and ion.vy < 0:
                            missed_shots += 1
                            ion.vy = abs(ion.vy)  # Change direction to move DOWN
                            ion.vx = random.uniform(-2, 2)
                            # Nudge it slightly below the membrane so it doesn't re-trigger immediately
                            ion.rect.top = MEMBRANE_Y + MEMBRANE_THICKNESS + 1
                    elif ion.rect.bottom < MEMBRANE_Y:
                        ion.has_passed, intracellular_count = True, intracellular_count + 1
                else:
                    # --- INTRACELLULAR BOUNCING ---
                    if ion.rect.left <= 0:
                        ion.rect.left = 1
                        ion.vx = abs(ion.base_speed) * pressure_multiplier
                        ion.vy += random.uniform(-1.5, 1.5)
                    elif ion.rect.right >= WIDTH:
                        ion.rect.right = WIDTH - 1
                        ion.vx = -abs(ion.base_speed) * pressure_multiplier
                        ion.vy += random.uniform(-1.5, 1.5)

                    if ion.rect.top <= 0:
                        ion.rect.top = 1
                        ion.vy = abs(ion.base_speed) * pressure_multiplier
                        ion.vx += random.uniform(-3.5, 3.5)

                    # Clamp velocity
                    max_v = 14
                    ion.vx = max(-max_v, min(max_v, ion.vx))
                    ion.vy = max(-max_v, min(max_v, ion.vy))

                    if MEMBRANE_Y <= ion.rect.bottom <= MEMBRANE_Y + (MEMBRANE_THICKNESS / 2):
                        leaked = False
                        for p in pores:
                            if (p.x - p.current_gap / 2) < ion.rect.centerx < (p.x + p.current_gap / 2):
                                if p.current_gap > ion.size:
                                    leaked = True
                        if leaked:
                            ion.has_passed, leaked_out = False, leaked_out + 1
                            intracellular_count, ion.vy = intracellular_count - 1, 5
                        else:
                            ion.vy, ion.rect.bottom = -abs(ion.vy), MEMBRANE_Y - 1

                if ion.rect.top > HEIGHT:
                    ions.remove(ion)

            # --- UI ---
            draw_text(
                screen,
                f"Intracellular Count: {intracellular_count} | Pressure: {pressure_multiplier:.2f}x | Efflux (Leaked): {leaked_out}",
                18,
                300,
                30,
                (255, 255, 255),
            )
            draw_text(screen, f"Blocked: {missed_shots} | Total Fired: {total_fired}", 18, 174, 60, (255, 255, 255))
            draw_text(
                screen, f"Ion: {player.current_ion.upper()}", 14, player.rect.centerx, player.rect.bottom + 10, (255, 255, 255)
            )

        pygame.display.flip()
        clock.tick(FPS)


asyncio.run(game())
