import pygame
import sys
HOVER_COLOR = (255, 140, 0)
# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 100, 100)
WIDTH, HEIGHT = 800, 600
pygame.init()
font = pygame.font.Font(None, 40)

background_image = pygame.image.load("Image/nenplayer.png")

background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
def draw_text(text, center_x, y, screen):
    """Hàm hiển thị văn bản lên màn hình và căn giữa"""
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(center_x, y))
    screen.blit(text_surface, text_rect)

def draw_rounded_rect(screen, color, rect, radius=10, border_thickness=2):
    """Hàm vẽ hình chữ nhật bo tròn với viền"""
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, BLACK, rect, border_thickness, border_radius=radius)

def player_input_screen(screen, mode="single"):
    """Giao diện nhập tên người chơi"""
    WIDTH, HEIGHT = screen.get_size()
    center_x = WIDTH // 2  # Tính vị trí chính giữa màn hình

    # Điều chỉnh vị trí để tránh chồng lên nhau
    title_y = HEIGHT // 2 - 180
    input1_y = title_y + 50
    label2_y = input1_y + 80
    input2_y = label2_y + 30
    play_y = input2_y + 80
    back_y = play_y + 70

    # Căn giữa các thành phần
    input_box1 = pygame.Rect(center_x - 150, input1_y, 300, 50)
    input_box2 = pygame.Rect(center_x - 150, input2_y, 300, 50)
    play_button = pygame.Rect(center_x - 100, play_y, 200, 50)
    back_button = pygame.Rect(center_x - 50, back_y, 100, 40)

    text1, text2 = "", ""
    active_box = None
    running = True

    while running:
        screen.blit(background_image, (0, 0))

        # Hiển thị tiêu đề
        if mode == "single":
            draw_text("ENTER PLAYER NAME", center_x, title_y, screen)
            draw_rounded_rect(screen, WHITE, input_box1, radius=10)
            draw_text(text1, center_x, input_box1.y + 25, screen)
        else:
            draw_text("ENTER PLAYER 1 NAME", center_x, title_y, screen)
            draw_rounded_rect(screen, WHITE, input_box1, radius=10)
            draw_text(text1, center_x, input_box1.y + 25, screen)

            draw_text("ENTER PLAYER 2 NAME", center_x, label2_y, screen)  # Đẩy tiêu đề lên trên
            draw_rounded_rect(screen, WHITE, input_box2, radius=10)
            draw_text(text2, center_x, input_box2.y + 25, screen)


        # Vẽ nút Play với hiệu ứng hover
        play_color = HOVER_COLOR if play_button.collidepoint(pygame.mouse.get_pos()) else RED
        pygame.draw.rect(screen, play_color, play_button)
        pygame.draw.rect(screen, BLACK, play_button, 2)
        draw_text("PLAY", center_x, play_button.y + 25, screen)

        # Vẽ nút Back với hiệu ứng hover
        back_color = HOVER_COLOR if back_button.collidepoint(pygame.mouse.get_pos()) else GRAY
        pygame.draw.rect(screen, back_color, back_button)
        pygame.draw.rect(screen, BLACK, back_button, 2)
        draw_text("Back", center_x, back_button.y + 20, screen)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if active_box == "input1":
                    if event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    elif len(text1) < 10:  # Giới hạn tối đa 10 ký tự
                        text1 += event.unicode
                elif active_box == "input2":
                    if event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    elif len(text2) < 10:  # Giới hạn tối đa 10 ký tự
                        text2 += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active_box = "input1"
                elif input_box2.collidepoint(event.pos) and mode == "multi":
                    active_box = "input2"
                elif play_button.collidepoint(event.pos):
                    return (text1,) if mode == "single" else (text1, text2)  # Trả về tên khi nhấn Play
                elif back_button.collidepoint(event.pos):
                    return None

            elif event.type == pygame.KEYDOWN:
                if active_box == "input1":
                    if event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                elif active_box == "input2":
                    if event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode

        pygame.display.flip()
