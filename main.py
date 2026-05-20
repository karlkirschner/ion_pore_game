import asyncio
import pygame
import math
import random


pygame.init()

async def game():
    # --- Configuration ---
    ## Game Window
    WIDTH, HEIGHT = 800, 600 ## Original appoach

    ## New approach to dynamically size the window based on the user's screen resolution.
    # info = pygame.display.Info()
    # screen_width = info.current_w
    # screen_height = info.current_h
    # # Set the window to be a safe 80% of their screen size
    # WIDTH = int(screen_width * 0.8)
    # HEIGHT = int(screen_height * 0.8)

    PLAYER_SPEED = 7
    FPS = 60
    MEMBRANE_Y = 250
    MEMBRANE_THICKNESS = 30
    LEAFLET_GAP = 5
    LEAFLET_THICKNESS = (MEMBRANE_THICKNESS - LEAFLET_GAP) // 2

    # Colors
    HBRSblue = (0, 158, 224)
    HBRSred = (199, 51, 38)
    HBRSlightgray = (240, 240, 240)
    ORANGE = (255, 165, 0)
    EXTRACELLULAR_BG = HBRSblue
    MEMBRANE_COLOR = ORANGE
    PORE_COLOR = HBRSlightgray
    LEAFLET_GAP_COLOR = (100, 100, 100)

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
        def __init__(self, x, speed, ext_len=5, int_len=5):
            self.x = x
            self.timer = random.uniform(0, 5)
            self.speed = speed
            self.base_gap = 45
            self.amplitude = 35
            self.current_gap = 45

            # Control for differeing protein pore shapes.
            self.ext_len = ext_len 
            self.int_len = int_len

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

    pores = [Pore(200, 0.12, ext_len=5, int_len=5), 
             Pore(400, 0.08, ext_len=20, int_len=5), 
             Pore(600, 0.05, ext_len=10, int_len=20)]

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
                    if event.key == pygame.K_ESCAPE:
                        ions.clear()
                        
                        intracellular_count = 0
                        missed_shots = 0
                        leaked_out = 0
                        total_fired = 0

                        game_state = "MENU" # 
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

            pygame.draw.rect(screen, (40, 40, 60), (WIDTH // 2 - 150, HEIGHT // 2 + 5, 300, 140), border_radius=10) # Made slightly taller
            draw_text(screen, "CONTROLS", 24, WIDTH // 2, HEIGHT // 2 + 25, HBRSblue)
            draw_text(screen, "ARROWS: Move Launcher", 18, WIDTH // 2, HEIGHT // 2 + 55)
            draw_text(screen, "SPACE: Launch Ion", 18, WIDTH // 2, HEIGHT // 2 + 80)
            draw_text(screen, "1, 2, 3 & 4: Ion Types", 18, WIDTH // 2, HEIGHT // 2 + 105)
            draw_text(screen, "ESC: Return to Menu", 18, WIDTH // 2, HEIGHT // 2 + 130)

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
                    width = gap_left - current_x
                    # Gap between leaflets
                    pygame.draw.rect(screen, LEAFLET_GAP_COLOR, (current_x, MEMBRANE_Y, width, MEMBRANE_THICKNESS))
                    # Top leaflet
                    pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y, width, LEAFLET_THICKNESS))
                    # Bottom leaflet
                    pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y + LEAFLET_THICKNESS + LEAFLET_GAP, width, LEAFLET_THICKNESS))
                
                current_x = p.x + p.current_gap / 2

            if current_x < WIDTH:
                width = WIDTH - current_x
                pygame.draw.rect(screen, LEAFLET_GAP_COLOR, (current_x, MEMBRANE_Y, width, MEMBRANE_THICKNESS)) # gap between leaflets
                pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y, width, LEAFLET_THICKNESS))
                pygame.draw.rect(screen, MEMBRANE_COLOR, (current_x, MEMBRANE_Y + LEAFLET_THICKNESS + LEAFLET_GAP, width, LEAFLET_THICKNESS))

            # --- PROTEIN WEDGES ---
            lip_y_top, lip_y_bottom = MEMBRANE_Y, MEMBRANE_Y + MEMBRANE_THICKNESS
            taper_amount = 6
            protein_width = 15
            for p in pores:
                gl, gr = p.x - p.current_gap / 2, p.x + p.current_gap / 2
                
                # Calculate the Y boundaries for THIS specific protein
                # Top edge (extends into extracellular space)
                p_top = MEMBRANE_Y - p.ext_len
                # Bottom edge (extends into intracellular space)
                p_bottom = MEMBRANE_Y + MEMBRANE_THICKNESS + p.int_len
                
                # Left Wedge
                l_wedge = [(gl, p_bottom),                   # Bottom-inner
                           (gl - protein_width, p_bottom),   # Bottom-outer
                           (gl - protein_width, p_top),      # Top-outer
                           (gl + taper_amount, p_top)]       # Top-inner (tapered)
                
                # Right Wedge
                r_wedge = [(gr, p_bottom),
                           (gr + protein_width, p_bottom),
                           (gr + protein_width, p_top),
                           (gr - taper_amount, p_top)]

                pygame.draw.polygon(screen, PORE_COLOR, l_wedge)
                pygame.draw.polygon(screen, PORE_COLOR, r_wedge)

            # --- PHYSICS & COLLISION ---
            pressure_multiplier = 1.0 + (intracellular_count / 25.0)

            for ion in ions[:]:
                ion.update()
                
                # Draw the ion body and glow (keep your existing draw code here)
                pygame.draw.circle(screen, ion.color, ion.rect.center, ion.size // 2)
                glow_color = [min(255, int(c + (255 - c) * 0.5)) for c in ion.color]
                glow_radius = max(1, ion.size // 5)
                glow_pos = (ion.rect.centerx - ion.size // 6, ion.rect.centery - ion.size // 6)
                pygame.draw.circle(screen, tuple(glow_color), glow_pos, glow_radius)

                if not ion.has_passed:
                    collision_occurred = False
                    in_pore_zone = False
                    
                    # 1. Check if the ion is within the horizontal bounds of ANY pore first
                    for p in pores:
                        taper_buffer = 6
                        gl = p.x - p.current_gap / 2 + taper_buffer
                        gr = p.x + p.current_gap / 2 - taper_buffer
                        
                        if gl < ion.rect.centerx < gr:
                            in_pore_zone = True
                            # 2. Check if it's vertically inside THIS specific protein
                            p_top = MEMBRANE_Y - p.ext_len
                            if ion.rect.top <= MEMBRANE_Y + MEMBRANE_THICKNESS and ion.rect.bottom >= p_top:
                                # Steric Hindrance (Size check)
                                if ion.size > p.current_gap:
                                    collision_occurred = True
                            break 

                    # 3. If NOT in a pore zone, check if it hit the membrane wall
                    if not in_pore_zone:
                        if ion.rect.top <= MEMBRANE_Y + MEMBRANE_THICKNESS and ion.rect.bottom >= MEMBRANE_Y:
                            collision_occurred = True

                    # 4. Handle successful passing
                    if not collision_occurred and ion.rect.bottom < MEMBRANE_Y - 5: # Small offset to ensure it's clear
                        ion.has_passed = True
                        intracellular_count += 1
                    
                    # 5. Handle the Bounce
                    if collision_occurred and ion.vy < 0:
                        missed_shots += 1
                        ion.vy = abs(ion.vy) * 0.8 
                        ion.vx += random.uniform(-3, 3)
                        # Nudge safely below the membrane
                        ion.rect.top = MEMBRANE_Y + MEMBRANE_THICKNESS + 5

                else:
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
                        ion.vx += random.uniform(-4.5, 4.5)

                    # 3. Apply the Pressure Multiplier to the current velocity
                    # This makes them zip around faster as the concentration increases
                    ion.vx *= (1.0 + (intracellular_count * 0.001)) 
                    ion.vy *= (1.0 + (intracellular_count * 0.001))

                    # 4. Speed Limit (Clamping)
                    max_v = 5
                    ion.vx = max(-max_v, min(max_v, ion.vx))
                    ion.vy = max(-max_v, min(max_v, ion.vy))

                    # 5. Intracellular Interaction (Inside the Cell)
                    if ion.rect.bottom >= (MEMBRANE_Y - 20): # Check slightly above membrane
                        in_pore_zone = False
                        current_p = None
                        
                        for p in pores:
                            # Define the "mouth" of the protein pore
                            p_top = MEMBRANE_Y - p.ext_len
                            # We use a slightly wider check for the protein structure
                            if (p.x - p.current_gap/2 - 15) < ion.rect.centerx < (p.x + p.current_gap/2 + 15):
                                in_pore_zone = True
                                current_p = p
                                break

                        if in_pore_zone:
                            # 1. Check for Vertical Steric Hindrance (Too fat to enter)
                            if ion.size > current_p.current_gap:
                                if ion.rect.bottom >= MEMBRANE_Y:
                                    ion.vy = -abs(ion.vy) * 0.8
                                    ion.rect.bottom = MEMBRANE_Y - 1
                            
                            # 2. Check for Protein "Wall" Collisions (The White Wedges)
                            # Left wall of the pore
                            if ion.rect.centerx < (current_p.x - current_p.current_gap / 2):
                                ion.vx = -abs(ion.vx) # Bounce Left
                                ion.rect.right = int(current_p.x - current_p.current_gap / 2)
                            
                            # Right wall of the pore
                            elif ion.rect.centerx > (current_p.x + current_p.current_gap / 2):
                                ion.vx = abs(ion.vx) # Bounce Right
                                ion.rect.left = int(current_p.x + current_p.current_gap / 2)
                                
                            # 3. Successful Leakage (Only if it clears the bottom)
                            if ion.rect.top > MEMBRANE_Y + MEMBRANE_THICKNESS:
                                ion.has_passed = False
                                leaked_out += 1
                                intracellular_count -= 1
                                ion.vy = 5 
                        else:
                            # Hit the Lipid Bilayer (The Orange Part)
                            if ion.rect.bottom >= MEMBRANE_Y:
                                ion.vy = -abs(ion.vy)
                                ion.rect.bottom = MEMBRANE_Y - 1

                # Clean up ions that fall off screen
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
