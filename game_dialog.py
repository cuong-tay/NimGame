import pygame
import sys

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HOVER_COLOR = (150, 150, 255)

def show_rules_dialog(screen):
    """Hiển thị hộp thoại luật chơi"""
    WIDTH, HEIGHT = screen.get_size()
    dialog_width, dialog_height = 500, 400
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2

    dialog = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    close_btn = pygame.Rect(dialog_x + dialog_width - 80, dialog_y + dialog_height - 50, 70, 40)

    rules_title = "LUAT CHOI NIM"
    rules_text = [
        "1. Moi luot chon mot cot va lay di it nhat mot vien da.",
        "2. Nguoi choi chi duoc lay da tu mot cot trong luot cua minh.",
        "3. Nguoi lay vien da cuoi cung la nguoi thang cuoc.",
        "4. Moi nguoi choi co gioi han thoi gian 20 giay cho moi luot.",
        "5. Het thoi gian se mat luot va chuyen qua doi thu."
    ]

    title_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 24)

    dialog_active = True
    while dialog_active:
        mouse_pos = pygame.mouse.get_pos()

        # Vẽ hộp thoại
        pygame.draw.rect(screen, WHITE, dialog)
        pygame.draw.rect(screen, BLACK, dialog, 2)

        # Vẽ tiêu đề
        title_surface = title_font.render(rules_title, True, BLACK)
        screen.blit(title_surface, (dialog_x + (dialog_width - title_surface.get_width()) // 2, dialog_y + 20))

        # Vẽ nội dung luật chơi
        y_offset = dialog_y + 70
        for line in rules_text:
            text_surface = text_font.render(line, True, BLACK)
            screen.blit(text_surface, (dialog_x + 20, y_offset))
            y_offset += 40

        # Vẽ nút đóng
        close_color = HOVER_COLOR if close_btn.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, close_color, close_btn)
        pygame.draw.rect(screen, BLACK, close_btn, 2)
        close_text = text_font.render("Đóng", True, BLACK)
        screen.blit(close_text, (close_btn.x + (close_btn.width - close_text.get_width()) // 2,
                                close_btn.y + (close_btn.height - close_text.get_height()) // 2))

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_btn.collidepoint(event.pos):
                    dialog_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    dialog_active = False

        pygame.display.flip()