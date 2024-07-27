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
font_path = pygame.font.match_font('dejavusans')  # Change to a specific font path if necessary
font_size = 48
font = pygame.font.Font(font_path, font_size)

# Phonetic symbols to display
phonetic_symbols = "ˈaɪ ˈpiː ˈeɪ"

# Render the text
text_surface = font.render(phonetic_symbols, True, (255, 255, 255))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Draw the text
    screen.blit(text_surface, (100, 100))
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
