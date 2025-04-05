import random
import sys
from datetime import datetime
from game_dialog import show_rules_dialog
import pygame

# Các màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
HOVER_COLOR = (150, 150, 255)
SCROLL_BAR_COLOR = (120, 120, 120)
last_player = None

pygame.init()
font = pygame.font.Font(None, 30)
history_font = pygame.font.Font(None, 20)

def draw_button(screen, rect, color, text, mouse_pos, hover_effect=True):
    if hover_effect and rect.collidepoint(mouse_pos):
        color = HOVER_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + 10))

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def game_2p(screen, player1, player2):
    WIDTH, HEIGHT = screen.get_size()
    GAME_AREA = pygame.Rect(0, 0, WIDTH - 200, HEIGHT)
    CONTROL_PANEL = pygame.Rect(WIDTH - 200, 0, 200, HEIGHT)

    last_player = None

    try:
        stone_sound = pygame.mixer.Sound("Image/mouse-click.mp3")
    except:
        print("Không thể tải âm thanh")
        stone_sound = None
    # Thêm biến đếm thời gian
    timer_start = pygame.time.get_ticks()
    timer_duration = 20000  # 20 giây
    timer_font = pygame.font.Font(None, 60)

    # Tạo biểu tượng đồng hồ
    try:
        clock_icon = pygame.image.load("Image/time.png")
        clock_icon = pygame.transform.scale(clock_icon, (30, 30))
    except:
        # Tạo icon đơn giản nếu không tìm thấy hình ảnh
        clock_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(clock_icon, BLACK, (15, 15), 14, 2)
        pygame.draw.line(clock_icon, BLACK, (15, 15), (15, 8), 2)
        pygame.draw.line(clock_icon, BLACK, (15, 15), (20, 15), 2)


    # kích thước các khung
    player1_col = pygame.Rect(WIDTH - 180, 25, 160, 40)
    player2_col = pygame.Rect(WIDTH - 180, 90, 160, 40)
    rules_btn = pygame.Rect(WIDTH - 180, 160, 160, 40)
    replay_btn = pygame.Rect(WIDTH - 180, HEIGHT - 120, 160, 40)
    back_btn = pygame.Rect(WIDTH - 180, HEIGHT - 60, 160, 40)
    history_panel = pygame.Rect(WIDTH - 190, 260, 180, HEIGHT - 420)

    # Scroll bar variables
    scroll_drag = False
    scroll_pos = 0
    scroll_offset = 0
    scroll_bar_height = 30
    scroll_bar_width = 8
    scroll_bar_x = history_panel.right - 10

    def generate_columns():
        num_columns = random.randint(3, 6)
        column_width = (GAME_AREA.width - 100) // num_columns
        return [[(50 + i * column_width + column_width // 2, HEIGHT - 50 - j * 40) for j in range(random.randint(1, 7))] for i in range(num_columns)]

    columns = generate_columns()
    player_turn = player1
    winner = None
    move_history = []
    last_player_move = None

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate content height for scrolling
        content_height = sum(
            25 * len(wrap_text(f"{move['time']} {move['player']}: Col {move['col'] + 1}, Remove {move['count']}",
                               history_font, history_panel.width - 20))
            for move in move_history)
        visible_area = history_panel.height - 20

        # Update scroll bar position and size
        if content_height > visible_area:
            scroll_ratio = visible_area / content_height
            scroll_bar_height = max(30, int(visible_area * scroll_ratio))
            scroll_bar_y = history_panel.y + 5 + (scroll_pos / (content_height - visible_area)) * (
                    visible_area - scroll_bar_height - 10)
        else:
            scroll_pos = 0
            scroll_bar_y = history_panel.y + 5

        # Create scroll bar rect
        scroll_bar = pygame.Rect(scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height)

        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, GAME_AREA, 2)
        pygame.draw.rect(screen, BLACK, CONTROL_PANEL, 2)

        # Tính thời gian còn lại
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - timer_start
        remaining_time = max(0, timer_duration - elapsed_time)
        seconds_left = remaining_time // 1000

        # Hiển thị đồng hồ đếm ngược
        if not winner:
            timer_color = RED if seconds_left <= 5 else BLACK
            timer_font_small = pygame.font.Font(None, 36)  # Font nhỏ hơn
            timer_text = f"{seconds_left:02d}"
            timer_surface = timer_font_small.render(timer_text, True, timer_color)

            # Vị trí mới ở góc trên bên phải
            timer_x = GAME_AREA.width - 80
            timer_y = 20

            # Vẽ nền cho đồng hồ
            pygame.draw.rect(screen, WHITE, (timer_x - 5, timer_y - 5,
                             timer_surface.get_width() + 10, timer_surface.get_height() + 10))

            # Vẽ icon đồng hồ bên cạnh
            screen.blit(clock_icon, (timer_x - 40, timer_y))

            # Vẽ số đồng hồ
            screen.blit(timer_surface, (timer_x, timer_y+4))

        # Hiển thị các nút chức năng
        draw_button(screen, rules_btn, YELLOW, "RULES", (mouse_x, mouse_y))
        draw_button(screen, replay_btn, BLUE, "REPLAY", (mouse_x, mouse_y))
        draw_button(screen, back_btn, BLUE, "BACK", (mouse_x, mouse_y))

        if player_turn == player1:
            draw_button(screen, player1_col, GREEN, f" {player1}", (mouse_x, mouse_y))
            draw_button(screen, player2_col, WHITE, f" {player2}", (mouse_x, mouse_y))
        else:
            draw_button(screen, player1_col, WHITE, f" {player1}", (mouse_x, mouse_y))
            draw_button(screen, player2_col, RED, f" {player2}", (mouse_x, mouse_y))

        # Vẽ khung lịch sử
        pygame.draw.rect(screen, WHITE, history_panel)
        pygame.draw.rect(screen, BLACK, history_panel, 2)

        # Draw scroll bar
        if content_height > visible_area:
            pygame.draw.rect(screen, SCROLL_BAR_COLOR, scroll_bar, border_radius=4)
            pygame.draw.rect(screen, (80, 80, 80), scroll_bar, 1, border_radius=4)

        # Draw history content with clipping
        history_surface = pygame.Surface((history_panel.width - 15, history_panel.height - 20), pygame.SRCALPHA)
        history_surface.fill((240, 240, 240, 0))

        y_offset = 10 - scroll_pos
        for move in move_history:
            text = f"{move['time']} {move['player']}: Cot {move['col'] + 1}, lay {move['count']} đá "
            lines = wrap_text(text, history_font, history_panel.width - 20)

            for line in lines:
                if y_offset + 20 > 0 and y_offset < history_panel.height:
                    color = BLUE if move['player'] == "COM" else BLACK
                    text_surface = history_font.render(line, True, color)
                    history_surface.blit(text_surface, (10, y_offset))
                y_offset += 20

        screen.blit(history_surface, (history_panel.x + 5, history_panel.y + 10))


        # Vẽ cột đá
        for col_idx, stones in enumerate(columns):
            hover_index = None
            if player_turn:
                for i, (x, y) in enumerate(stones):
                    if (x - 20 < mouse_x < x + 20) and (y - 20 < mouse_y < y + 20):
                        hover_index = i

            # Then draw the stones
            for i, (x, y) in enumerate(stones):
                color = HOVER_COLOR if hover_index is not None and i >= hover_index else BLACK
                pygame.draw.circle(screen, color, (x, y), 20)
                pygame.draw.circle(screen, WHITE, (x, y), 18, 2)

        if all(len(stones) == 0 for stones in columns) and winner is None:
            if last_player == f"{player1}":
                winner = f"{player1}"
            else:
                winner = f"{player2}"

        if winner:
            winner_text = f"{winner} WINS!"
            text_surface = font.render(winner_text, True, BLUE)
            text_x = GAME_AREA.centerx - text_surface.get_width() // 2
            text_y = GAME_AREA.centery - 20
            pygame.draw.rect(screen, WHITE, (text_x - 10, text_y - 5, text_surface.get_width() + 20, 30))
            pygame.draw.rect(screen, BLACK, (text_x - 10, text_y - 5, text_surface.get_width() + 20, 30), 2)
            screen.blit(text_surface, (text_x, text_y))

        # Kiểm tra hết thời gian
        if seconds_left == 0 and not winner:
            winner = player2 if player_turn == player1 else player1
            last_player = player_turn


        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
                elif replay_btn.collidepoint(event.pos):
                    columns = generate_columns()
                    player_turn = player1
                    winner = None
                    move_history = []
                    scroll_offset = 0  # Reset cuộn
                    timer_start = pygame.time.get_ticks()
                elif rules_btn.collidepoint(event.pos):
                    show_rules_dialog(screen)
                    timer_start = pygame.time.get_ticks()
                elif scroll_bar.collidepoint(event.pos) and content_height > visible_area:
                    scroll_drag = True
                    scroll_offset = mouse_y - scroll_bar_y
                elif not winner:
                    # Kiểm tra nếu người chơi chọn đúng vị trí đá
                    for col_idx, stones in enumerate(columns):
                        for i, (x, y) in enumerate(stones):
                            if (x - 20 < event.pos[0] < x + 20) and (y - 20 < event.pos[1] < y + 20):
                                if stone_sound:
                                     stone_sound.play()
                                stones_removed = len(stones) - i
                                # Thêm lịch sử di chuyển vào move_history
                                move_history.insert(0, {  # Thêm nước đi vào đầu danh sách
                                    'time': datetime.now().strftime("%H:%M:%S"),
                                    'player': player_turn,
                                    'col': col_idx,
                                    'count': stones_removed
                                })
                                # Cập nhật trạng thái cột sau khi bỏ đá
                                del stones[i:]
                                last_player = player_turn
                                # Chuyển lượt cho người chơi khác
                                player_turn = player1 if player_turn == player2 else player2
                                timer_start = pygame.time.get_ticks()
                                scroll_offset = 0  # Reset cuộn khi có nước đi mới
                                break
            elif event.type == pygame.MOUSEBUTTONUP:
                scroll_drag = False
            elif event.type == pygame.MOUSEMOTION:
                if scroll_drag and content_height > visible_area:
                    new_y = mouse_y - scroll_offset
                    scroll_bar.y = max(history_panel.y + 5,
                                       min(new_y, history_panel.y + history_panel.height - scroll_bar.height - 5))
                    scroll_pos = (scroll_bar.y - history_panel.y - 5) / (
                            history_panel.height - scroll_bar.height - 10) * max(0, content_height - visible_area)
            elif event.type == pygame.MOUSEWHEEL:
                if history_panel.collidepoint(mouse_x, mouse_y):
                    scroll_pos = max(0, min(scroll_pos - event.y * 20,
                                            content_height - visible_area))

        pygame.display.flip()
        clock.tick(60)
