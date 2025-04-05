import pygame
import sys
import random
import functools
from datetime import datetime
from game_dialog import show_rules_dialog
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
HOVER_COLOR = (150, 150, 255)
GRAY = (200, 200, 200)
HISTORY_BG = (240, 240, 240)
SCROLL_BAR_COLOR = (120, 120, 120)
HINT_COLOR = (0, 255, 0, 180)  # More visible hint color
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


def calculate_nim_sum(columns):
    return functools.reduce(lambda x, y: x ^ y, [len(col) for col in columns], 0)


def ai_move(columns):
    nim_sum = calculate_nim_sum(columns)
    if nim_sum == 0:
        valid_columns = [col for col in columns if col]
        if valid_columns:
            chosen_column = random.choice(valid_columns)
            chosen_column.pop()
            return len(valid_columns[0]), 1
    else:
        for col_idx, col in enumerate(columns):
            for remove_count in range(1, len(col) + 1):
                new_nim_sum = calculate_nim_sum(columns) ^ len(col) ^ (len(col) - remove_count)
                if new_nim_sum == 0:
                    del col[-remove_count:]
                    return col_idx, remove_count
    return None, 0


def get_hint_move(columns):
    """Calculate the optimal move to suggest to the player"""
    nim_sum = calculate_nim_sum(columns)

    # If no winning move, suggest a random valid move
    if nim_sum == 0:
        valid_columns = [i for i, col in enumerate(columns) if col]
        if not valid_columns:
            return None
        col_idx = random.choice(valid_columns)
        return (col_idx, len(columns[col_idx]) - 1)

    # Find a move that makes nim sum zero
    for col_idx, col in enumerate(columns):
        if not col:
            continue
        for remove_count in range(1, len(col) + 1):
            new_nim_sum = nim_sum ^ len(col) ^ (len(col) - remove_count)
            if new_nim_sum == 0:
                return (col_idx, len(col) - remove_count)

    return None


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


def game_vs_com(screen, player1):
    WIDTH, HEIGHT = screen.get_size()
    GAME_AREA = pygame.Rect(0, 0, WIDTH - 200, HEIGHT)
    CONTROL_PANEL = pygame.Rect(WIDTH - 200, 0, 200, HEIGHT)

    try:
        stone_sound = pygame.mixer.Sound("Image/mouse-click.mp3")
    except:
         print("Không thể tải âm thanh")
         stone_sound = None
    # Thêm biến đếm thời gian
    timer_start = pygame.time.get_ticks()
    timer_duration = 20000  # 30 giây
    timer_font = pygame.font.Font(None, 60)
    try:
     clock_icon = pygame.image.load("Image/time.png")  # Thay bằng đường dẫn thực tế
     clock_icon = pygame.transform.scale(clock_icon, (30, 30))
    except:

     clock_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
     pygame.draw.circle(clock_icon, BLACK, (15, 15), 14, 2)
     pygame.draw.line(clock_icon, BLACK, (15, 15), (15, 8), 2)
     pygame.draw.line(clock_icon, BLACK, (15, 15), (20, 15), 2)
    # UI Elements
    player_name_btn = pygame.Rect(WIDTH - 180, 20, 160, 40)
    rules_btn = pygame.Rect(WIDTH - 180, 80, 160, 40)
    suggest_btn = pygame.Rect(WIDTH - 180, 140, 160, 40)
    undo_btn = pygame.Rect(WIDTH - 180, 200, 160, 40)
    history_panel = pygame.Rect(WIDTH - 190, 260, 180, HEIGHT - 420)
    replay_btn = pygame.Rect(WIDTH - 180, HEIGHT - 120, 160, 40)
    back_btn = pygame.Rect(WIDTH - 180, HEIGHT - 60, 160, 40)

    # Scroll bar variables
    scroll_pos = 0
    scroll_drag = False
    scroll_offset = 0
    scroll_bar_height = 30
    scroll_bar_width = 8
    scroll_bar_x = history_panel.right - 10

    # Hint variables
    show_hint = False
    hint_move = None
    hint_start_time = 0
    hint_duration = 3000  # 3 seconds

    def generate_columns():
        num_columns = random.randint(3, 6)
        column_width = (GAME_AREA.width - 100) // num_columns
        return [[(50 + i * column_width + column_width // 2, HEIGHT - 50 - j * 40) for j in range(random.randint(1, 7))]
                for i in range(num_columns)]

    columns = generate_columns()
    player_turn = True
    winner = None
    ai_should_move = False
    last_player_move = None
    animation_start_time = 0
    animation_duration = 800
    ai_delay = 500

    move_history = []

    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Tính toán thời gian còn lại
        if player_turn and not winner and not ai_should_move:
            time_left = max(0, timer_duration - (current_time - timer_start))
            seconds_left = time_left // 1000

            # Kiểm tra nếu hết thời gian
            if time_left == 0 and not winner:
                winner = "COM"
                last_player = "COM"
        else:
            # Reset đồng hồ khi không phải lượt người chơi
            timer_start = current_time
            seconds_left = timer_duration // 1000

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

        # Drawing
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, GAME_AREA, 2)
        pygame.draw.rect(screen, BLACK, CONTROL_PANEL, 2)

        # Draw buttons
        draw_button(screen, player_name_btn, WHITE, f"{player1}", (mouse_x, mouse_y), hover_effect=False)
        draw_button(screen, rules_btn, YELLOW, "RULES", (mouse_x, mouse_y))
        draw_button(screen, suggest_btn, GREEN, "HINT", (mouse_x, mouse_y))
        draw_button(screen, undo_btn, RED, "UNDO", (mouse_x, mouse_y))
        draw_button(screen, replay_btn, BLUE, "REPLAY", (mouse_x, mouse_y))
        draw_button(screen, back_btn, BLUE, "BACK", (mouse_x, mouse_y))

        # Draw history panel
        pygame.draw.rect(screen, HISTORY_BG, history_panel)
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
            text = f"{move['time']} {move['player']}: Col {move['col'] + 1}, Remove {move['count']}"
            lines = wrap_text(text, history_font, history_panel.width - 20)

            for line in lines:
                if y_offset + 20 > 0 and y_offset < history_panel.height:
                    color = BLUE if move['player'] == "COM" else BLACK
                    text_surface = history_font.render(line, True, color)
                    history_surface.blit(text_surface, (10, y_offset))
                y_offset += 20

        screen.blit(history_surface, (history_panel.x + 5, history_panel.y + 10))

        # Draw stones with animation and hint effects
        for col_idx, stones in enumerate(columns):
            hover_index = None
            if player_turn:
                for i, (x, y) in enumerate(stones):
                    if (x - 20 < mouse_x < x + 20) and (y - 20 < mouse_y < y + 20):
                        hover_index = i

            # Draw hint highlight first (so stones appear on top)
            if show_hint and hint_move and current_time - hint_start_time < hint_duration:
                hint_col, hint_stone_idx = hint_move
                if col_idx == hint_col and stones:
                    for i, (x, y) in enumerate(stones):
                        if i >= hint_stone_idx:
                            # Draw semi-transparent green highlight
                            s = pygame.Surface((40, 40), pygame.SRCALPHA)
                            pygame.draw.circle(s, HINT_COLOR, (20, 20), 20)
                            pygame.draw.circle(s, (255, 255, 255, 180), (20, 20), 18, 2)
                            screen.blit(s, (x - 20, y - 20))
                            # Draw outline for better visibility
                            pygame.draw.circle(screen, (0, 200, 0), (x, y), 22, 2)

            # Then draw the stones
            for i, (x, y) in enumerate(stones):
                if last_player_move and col_idx == last_player_move[0] and i >= last_player_move[1]:
                    if current_time - animation_start_time < animation_duration:
                        alpha = int(255 * (1 - (current_time - animation_start_time) / animation_duration))
                        color = (GRAY[0], GRAY[1], GRAY[2], alpha)
                        s = pygame.Surface((40, 40), pygame.SRCALPHA)
                        pygame.draw.circle(s, color, (20, 20), 20)
                        pygame.draw.circle(s, (255, 255, 255, alpha), (20, 20), 18, 2)
                        screen.blit(s, (x - 20, y - 20))
                        continue
                    else:
                        continue

                color = HOVER_COLOR if hover_index is not None and i >= hover_index else BLACK
                pygame.draw.circle(screen, color, (x, y), 20)
                pygame.draw.circle(screen, WHITE, (x, y), 18, 2)

        # Check if hint time has expired
        if show_hint and current_time - hint_start_time >= hint_duration:
            show_hint = False
            hint_move = None

        # # Winner check
        # if all(len(stones) == 0 for stones in columns) and winner is None:
        #      winner = player1 if  player_turn else 'COM'
        if all(len(stones) == 0 for stones in columns) and winner is None:
            if last_player == "COM":
                winner = "COM"
            else:
                winner = f"{player1}"


        if winner:
            winner_text = f"{winner} WINS!"
            text_surface = font.render(winner_text, True, RED)
            text_x = GAME_AREA.centerx - text_surface.get_width() // 2
            text_y = GAME_AREA.centery - 20
            pygame.draw.rect(screen, WHITE, (text_x - 10, text_y - 5, text_surface.get_width() + 20, 30))
            pygame.draw.rect(screen, BLACK, (text_x - 10, text_y - 5, text_surface.get_width() + 20, 30), 2)
            screen.blit(text_surface, (text_x, text_y))

        # Hiển thị đồng hồ đếm ngược
        if player_turn and not winner and not ai_should_move:
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


        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
                elif replay_btn.collidepoint(event.pos):
                    columns = generate_columns()
                    player_turn = True
                    winner = None
                    ai_should_move = False
                    last_player_move = None
                    move_history = []
                    scroll_pos = 0
                    show_hint = False
                    hint_move = None
                elif rules_btn.collidepoint(event.pos):
                    show_rules_dialog(screen)
                    timer_start = pygame.time.get_ticks()
                elif undo_btn.collidepoint(event.pos) and move_history:
                          # Trước tiên, hủy bỏ mọi animation đang chạy
                        if last_player_move:
                              col_idx, stone_idx = last_player_move
                              columns[col_idx][stone_idx:] = []  # Xóa đá ngay lập tức
                              last_player_move = None

                          # Tiếp tục logic undo bình thường
                          # Case 1: Số nước đi lẻ (người chơi vừa đi)
                        if len(move_history) % 2 == 1:
                              # Chỉ hoàn lại nước đi cuối của người chơi
                              last_move = move_history.pop()
                              col_idx = last_move['col']
                              count = last_move['count']

                              # Tính toán vị trí cho đá được hoàn lại
                              column_width = (GAME_AREA.width - 100) // len(columns)
                              base_x = 50 + col_idx * column_width + column_width // 2
                              current_height = len(columns[col_idx])

                              # Khôi phục đá với vị trí chính xác
                              for i in range(count):
                                  y = HEIGHT - 50 - (current_height + i) * 40
                                  columns[col_idx].append((base_x, y))

                              # Tiếp tục lượt người chơi
                              player_turn = True
                              ai_should_move = False

                          # Tiếp tục với trường hợp số nước đi chẵn...

                        # Case 2: Even number of moves (both player and COM have moved)
                        else:

                            com_move = move_history.pop()
                            col_idx = com_move['col']
                            count = com_move['count']

                            column_width = (GAME_AREA.width - 100) // len(columns)
                            base_x = 50 + col_idx * column_width + column_width // 2
                            current_height = len(columns[col_idx])

                            for i in range(count):
                                y = HEIGHT - 50 - (current_height + i) * 40
                                columns[col_idx].append((base_x, y))

                            # Then, undo player's move
                            player_move = move_history.pop()
                            col_idx = player_move['col']
                            count = player_move['count']

                            column_width = (GAME_AREA.width - 100) // len(columns)
                            base_x = 50 + col_idx * column_width + column_width // 2
                            current_height = len(columns[col_idx])

                            for i in range(count):
                                y = HEIGHT - 50 - (current_height + i) * 40
                                columns[col_idx].append((base_x, y))

                            player_turn = True
                            ai_should_move = False

                        # Update last player and reset state variables
                        if move_history:
                            last_player = move_history[-1]['player']
                        else:
                            last_player = None

                        last_player_move = None
                        animation_start_time = 0
                        show_hint = False
                        winner = None
                elif suggest_btn.collidepoint(event.pos) and player_turn and not winner:
                    hint_move = get_hint_move(columns)
                    if hint_move:  # Only show hint if valid move exists
                        show_hint = True
                        hint_start_time = current_time
                elif scroll_bar.collidepoint(event.pos) and content_height > visible_area:
                    scroll_drag = True
                    scroll_offset = mouse_y - scroll_bar.y
                elif player_turn and not winner and not ai_should_move:
                    for col_idx, stones in enumerate(columns):
                        for i, (x, y) in enumerate(stones):
                            if (x - 20 < event.pos[0] < x + 20) and (y - 20 < event.pos[1] < y + 20):
                                if stone_sound:
                                  stone_sound.play()
                                stones_removed = len(stones) - i
                                move_history.append({
                                    'time': datetime.now().strftime("%H:%M:%S"),
                                    'player': player1,
                                    'col': col_idx,
                                    'count': stones_removed
                                })
                                last_player_move = (col_idx, i)
                                last_player = player1  # Cập nhật người chơi vừa đi
                                player_turn = False
                                ai_should_move = True
                                animation_start_time = current_time
                                timer_start = current_time
                                show_hint = False
                                scroll_pos = max(0, content_height - visible_area)
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

        # AI move handling
        if (ai_should_move and last_player_move and current_time - animation_start_time >= animation_duration + ai_delay):
            col_idx, stone_idx = last_player_move
            columns[col_idx][stone_idx:] = []  # Xóa số viên đã chọn
            last_player_move = None

            ai_col, ai_count = ai_move(columns)
            if ai_col is not None:
                move_history.append({
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'player': "COM",
                    'col': ai_col,
                    'count': ai_count
                })
                last_player = "COM"  # Cập nhật AI là người vừa đi
                content_height = sum(25 * len(
                    wrap_text(f"{move['time']} {move['player']}: Col {move['col'] + 1}, Remove {move['count']}",
                              history_font, history_panel.width - 20))
                                     for move in move_history)
                visible_area = history_panel.height - 20
                scroll_pos = max(0, content_height - visible_area)

            player_turn = True
            ai_should_move = False

        pygame.display.flip()
        clock.tick(60)