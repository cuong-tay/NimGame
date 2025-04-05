import pygame
import sys
from About import about_screen  # Import hàm about_screen từ about.py
from player_input import player_input_screen
from gamevscom import game_vs_com
from game2p import game_2p

# Khởi tạo Pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NIM GAME")
background_image = pygame.image.load("Image/background.png")

# Thu nhỏ và căn giữa ảnh nền
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
HOVER_COLOR = (255, 140, 0)  # Màu khi di chuột vào nút

# Khởi tạo font chữ
custom_font = pygame.font.Font("DynaPuff/DynaPuff-VariableFont_wdth,wght.ttf", 76)
button_font = pygame.font.Font("DynaPuff/DynaPuff-VariableFont_wdth,wght.ttf", 25)


# Định nghĩa kích thước nút
button_width, button_height = 230, 70
button_spacing = 30  # Khoảng cách giữa các nút

# Tính toán vị trí X để căn giữa
button_x = (WIDTH - button_width) // 2

# Tính toán vị trí Y cho từng nút
play_com_button = pygame.Rect(button_x, 200, button_width, button_height)
play_2p_button = pygame.Rect(button_x, play_com_button.bottom + button_spacing, button_width, button_height)
about_button = pygame.Rect(button_x, play_2p_button.bottom + button_spacing, button_width, button_height)
sound_button = pygame.Rect(WIDTH - 100, HEIGHT - 100, 40, 40)

# Tải nhạc và chuẩn bị pygame.mixer
pygame.mixer.init()
music_playing = False

# Tải icon loa
try:
    speaker_on_icon = pygame.image.load("Image/loabat.png")
    speaker_on_icon = pygame.transform.scale(speaker_on_icon, (30, 30))

    speaker_off_icon = pygame.image.load("Image/loatat.png")  # Thêm icon loa tắt
    speaker_off_icon = pygame.transform.scale(speaker_off_icon, (30, 30))
except pygame.error as e:
    print(f"Không thể tải icon loa: {e}")
    speaker_on_icon = None
    speaker_off_icon = None
# Hàm vẽ nút với hiệu ứng hover
def draw_button(button, text, mouse_pos, radius=15):
    color = HOVER_COLOR if button.collidepoint(mouse_pos) else ORANGE
    pygame.draw.rect(screen, color, button, border_radius=radius)
    pygame.draw.rect(screen, BLACK, button, 2, border_radius=radius)

    # Căn giữa chữ trong nút
    text_surface = button_font.render(text, True, BLACK)
    text_x = button.centerx - text_surface.get_width() // 2
    text_y = button.y + (button_height - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))

def draw_sound_button(mouse_pos):
    """Vẽ nút loa với icon phù hợp dựa trên trạng thái nhạc"""
    color = HOVER_COLOR if sound_button.collidepoint(mouse_pos) else GRAY

    # Vẽ hình tròn
    pygame.draw.circle(screen, WHITE, sound_button.center, sound_button.width // 2)
    pygame.draw.circle(screen, color, sound_button.center, sound_button.width // 2, 0)

    # Hiển thị icon loa phù hợp dựa trên trạng thái nhạc
    if music_playing and speaker_on_icon:
        icon_rect = speaker_on_icon.get_rect(center=sound_button.center)
        screen.blit(speaker_on_icon, icon_rect)
    elif not music_playing and speaker_off_icon:
        icon_rect = speaker_off_icon.get_rect(center=sound_button.center)
        screen.blit(speaker_off_icon, icon_rect)

def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.stop()
    else:
        pygame.mixer.music.load("Image/MatKetNoi-DuongDomic-16783113.mp3")  # Thay đổi tên tệp nhạc của bạn
        pygame.mixer.music.play(-1)  # Phát nhạc lặp lại mãi mãi
    music_playing = not music_playing

    # Hàm hiển thị giao diện chính
def main_menu():
    running = True
    while running:
        screen.blit(background_image, (0, 0))

        # Hiển thị tiêu đề
        title_text = custom_font.render("NIM GAME", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Lấy vị trí chuột
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Vẽ các nút với hiệu ứng hover
        draw_button(play_com_button, "PLAY WITH COM", (mouse_x, mouse_y))
        draw_button(play_2p_button, "2 PLAYER", (mouse_x, mouse_y))
        draw_button(about_button, "ABOUT", (mouse_x, mouse_y))
        draw_sound_button((mouse_x, mouse_y))
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:  # Kiểm tra khi nhả chuột
                if about_button.collidepoint((mouse_x, mouse_y)):
                    about_screen(screen)  # Gọi màn hình About khi nhấn
                elif play_com_button.collidepoint(event.pos):
                    result = player_input_screen(screen, mode="single")
                    if result:
                        game_vs_com(screen, result[0])  # Mở game với tên 1 người chơi
                elif play_2p_button.collidepoint(event.pos):
                    result = player_input_screen(screen, mode="multi")
                    if result:
                        game_2p(screen, result[0], result[1])  # Mở game với 2 người chơi
                elif sound_button.collidepoint(event.pos):  # Kiểm tra khi nhấn nút loa
                    toggle_music()
        pygame.display.flip()  # Cập nhật màn hình

# Chạy chương trình
main_menu()
