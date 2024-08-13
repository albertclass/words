import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Phonetic Symbols with Pygame")

# Choose a font and size
# Make sure the font file supports phonetic symbols and is available on your system
font_path = [
    pygame.font.match_font('Arial Unicode MS'),  # Change to a specific font path if necessary
    pygame.font.match_font('Calibri'),
    pygame.font.match_font('Cambria'),
    pygame.font.match_font('Times New Roman'),
    pygame.font.match_font('Segoe UI'),
    pygame.font.match_font('Lucida Sans Unicode'),
    pygame.font.match_font('DejaVu Sans'),
]

font_size = 48
fonts = [pygame.font.Font(path, font_size) for path in font_path]

# Phonetic symbols to display
phonetic_symbols = "'sistә"

# Render the text
text_surfaces = [font.render(phonetic_symbols, True, (255, 255, 255)) for font in fonts]

g = pygame.sprite.Group()
for i, text_surface in enumerate(text_surfaces):
    g.add(pygame.sprite.Sprite())
    g.sprites()[-1].image = text_surface
    g.sprites()[-1].rect = text_surface.get_rect(topleft=(100, 100 + i * 50))
    
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Draw the text
    # screen.blit(g, (100, 100))
    g.draw(screen)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
