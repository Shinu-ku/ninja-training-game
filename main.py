import pygame
import random
import cairosvg

pygame.init()

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Set up the game window
display_width = 1000
display_height = 646
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('NINJA TRAINING')

# Set up the game clock
clock = pygame.time.Clock()

# Load the background images
background_image = pygame.image.load('background.png')
background_image = pygame.transform.scale(background_image, (1000, 646))

night_background_image = pygame.image.load('night_background.png')
night_background_image = pygame.transform.scale(night_background_image, (1000, 646))

# Convert SVG to PNG for pygame compatibility
cairosvg.svg2png(url='player_right.svg', write_to='player_right.png', output_width=128, output_height=186)
cairosvg.svg2png(url='player_left.svg', write_to='player_left.png', output_width=128, output_height=186)
cairosvg.svg2png(url='enemy.svg', write_to='enemy.png', output_width=32, output_height=30)
cairosvg.svg2png(url='play_button.svg', write_to='play_button.png', output_width=256, output_height=256)
cairosvg.svg2png(url='life.svg', write_to='life.png', output_width=40, output_height=40)

# Load the player images
player_image_right = pygame.image.load('player_right.png')
player_image_left = pygame.image.load('player_left.png')
player_width = 128
player_height = 186

# Load enemy image
enemy_image = pygame.image.load('enemy.png')
enemy_width = 32
enemy_height = 30

# Load play button image
play_button_image = pygame.image.load('play_button.png')
play_button_width = 128
play_button_height = 128
play_button_image = pygame.transform.scale(play_button_image, (play_button_width, play_button_height))

# Load life images
life_image = pygame.image.load('life.png')
life_size = 36  # Size of life images

# Load sounds
bgsound = pygame.mixer.Sound('bgsound.mp3')
bgsound.set_volume(0.8)
heart = pygame.mixer.Sound('heart.wav')
hit = pygame.mixer.Sound('hit.wav')
looose = pygame.mixer.Sound('looose.wav')
dodge = pygame.mixer.Sound('dodge.wav')

# Load font
font = pygame.font.SysFont(None, 30)

# High score file
high_score_file = "high_score.txt"

def read_high_score():
    try:
        with open(high_score_file, 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

def write_high_score(high_score):
    with open(high_score_file, 'w') as file:
        file.write(str(high_score))

def game_loop():
    game_exit = False
    game_over = True
    played_loose_sound = False
    
    player_x = (display_width / 2) - (player_width / 2)
    player_y = display_height - player_height - 50
    player_life = 5
    player_speed = 18
    moving_left = False
    moving_right = False
    player_image = player_image_right

    enemy_x = random.randint(0, display_width - enemy_width)
    enemy_y = -enemy_height
    enemy_speed = 36
    score = 0
    high_score = read_high_score()
    night_mode = False
    rotation_angle = 0

    while not game_exit:
        game_display.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    moving_left = True
                    player_image = player_image_left
                elif event.key == pygame.K_RIGHT:
                    moving_right = True
                    player_image = player_image_right
                elif event.key == pygame.K_n:
                    night_mode = not night_mode
                elif event.key == pygame.K_RETURN and game_over:
                    game_over = False
                    player_life = 5
                    score = 0
                    enemy_speed = 26
                    played_loose_sound = False
                    enemy_x = random.randint(0, display_width - enemy_width)
                    enemy_y = -enemy_height
                    bgsound.play(-1)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    moving_left = False
                elif event.key == pygame.K_RIGHT:
                    moving_right = False
        
        if moving_left and player_x > 0:
            player_x -= player_speed
        if moving_right and player_x < display_width - player_width:
            player_x += player_speed

        game_display.blit(night_background_image if night_mode else background_image, (0, 0))

        if not game_over:
            enemy_y += enemy_speed
            if enemy_y > display_height:
                enemy_x = random.randint(0, display_width - enemy_width)
                enemy_y = -enemy_height
                enemy_speed = min(enemy_speed + 1, 15)
                score += 1
                dodge.play()

            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)

            if player_rect.colliderect(enemy_rect):
                hit.play()
                player_life -= 1
                enemy_y = -enemy_height
                enemy_x = random.randint(0, display_width - enemy_width)
                if player_life <= 0:
                    game_over = True
                    bgsound.stop()
                    looose.play()
                    if score > high_score:
                        write_high_score(score)
                        high_score = score

            rotated_enemy = pygame.transform.rotate(enemy_image, rotation_angle)
            enemy_rect = rotated_enemy.get_rect(center=(enemy_x + enemy_width / 2, enemy_y + enemy_height / 2))
            rotation_angle = (rotation_angle + 36) % 360
            game_display.blit(rotated_enemy, enemy_rect.topleft)
            game_display.blit(player_image, (player_x, player_y))

            for i in range(player_life):
                game_display.blit(life_image, (10 + i * (life_size + 5), display_height - life_size - 10))

            score_text = font.render(f"Score: {score}", True, black)
            game_display.blit(score_text, (10, 10))

            high_score_text = font.render(f"High Score: {high_score}", True, black)
            game_display.blit(high_score_text, (display_width - high_score_text.get_width() - 10, 10))
        else:
            game_display.blit(play_button_image, ((display_width / 2) - (play_button_width / 2), (display_height / 2) - (play_button_height / 2)))
            restart_text = font.render("Press ENTER to Restart", True, red)
            game_display.blit(restart_text, (display_width / 2 - 100, display_height / 2 + 100))
        
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    quit()

game_loop()
