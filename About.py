import pygame
import sys
import textwrap

def wrap_text(text, font, max_width):
    """Ngat dong van ban theo chieu rong toi da"""
    words = text.split()
    wrapped_lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        text_surface = font.render(test_line, True, (0, 0, 0))

        if text_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            wrapped_lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        wrapped_lines.append(' '.join(current_line))

    return wrapped_lines

def about_screen(screen):
    # Mau sac
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    HOVER_COLOR = (180, 180, 180)

    # Khoi tao font
    pygame.font.init()

    # Chon font phu hop
    try:
        title_font = pygame.font.Font(None, 50)  # Font he thong mac dinh
        text_font = pygame.font.Font(None, 36)
    except:
        title_font = pygame.font.SysFont("Arial", 50)
        text_font = pygame.font.SysFont("Arial", 36)

    # Kich thuoc man hinh
    WIDTH, HEIGHT = screen.get_size()
    MAX_TEXT_WIDTH = WIDTH - 100  # De tao le

    # Nut "Back" can giua
    button_width, button_height = 150, 50
    back_button = pygame.Rect((WIDTH - button_width) // 2, HEIGHT - 100, button_width, button_height)

    # Noi dung chi tiet va mo rong
    rules = [
        "1. Tro choi bat dau voi mot so luong gay duoc xac dinh truoc.",
        "2. Hai nguoi choi se luan phien lay gay tu cac dong.",
        "3. Moi luot, nguoi choi duoc phep lay bat ky so gay nao tu mot dong duy nhat.",
        "4. Nguoi lay duoc cay gay cuoi cung se la nguoi chien thang.",
        "5. Chien luoc va tinh toan la yeu to then chot de gianh chien thang."
    ]

    # Tai anh nen
    background_image = pygame.image.load("Image/background.png")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    running = True
    while running:
        # Vẽ nền ảnh
        screen.blit(background_image, (0, 0))

        # Hien thi tieu de
        title_text = title_font.render("About - Luat Choi", True, BLACK)
        title_rect = title_text.get_rect(centerx=WIDTH // 2, top=20)
        screen.blit(title_text, title_rect)

        # Hien thi luat choi voi ngat dong
        y_offset = 80
        for rule in rules:
            # Ngat dong van ban
            wrapped_lines = wrap_text(rule, text_font, MAX_TEXT_WIDTH)

            for line in wrapped_lines:
                rule_text = text_font.render(line, True, BLACK)
                rule_rect = rule_text.get_rect(centerx=WIDTH // 2, top=y_offset)
                screen.blit(rule_text, rule_rect)
                y_offset += 30  # Khoang cach giua cac dong

        # Lay vi tri chuot
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Kiem tra hover
        button_color = HOVER_COLOR if back_button.collidepoint(mouse_x, mouse_y) else GRAY

        # Ve nut "Back"
        pygame.draw.rect(screen, button_color, back_button)
        pygame.draw.rect(screen, BLACK, back_button, 2)

        back_text = text_font.render("Quay Lai", True, BLACK)
        back_rect = back_text.get_rect(centerx=back_button.centerx, centery=back_button.centery)
        screen.blit(back_text, back_rect)

        # Xu ly su kien
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if back_button.collidepoint((mouse_x, mouse_y)):
                    running = False  # Quay lai menu

        pygame.display.flip()

# Luu y: Ham nay duoc goi tu main game
# about_screen(screen)
