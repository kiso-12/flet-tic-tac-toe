import flet as ft
import math
import random

# Color palette
BG = "#0f0f1a"
SURFACE = "#1a1a2e"
CARD = "#16213e"
ACCENT_X = "#e94560"
ACCENT_O_LIGHT = "#4fc3f7"
TEXT_PRIMARY = "#eaeaea"
TEXT_DIM = "#6b7280"
BORDER = "#2a2a4a"

SIZE = 5
WIN = 4  # 4連で勝利


# ── ゲームロジック ─────────────────────────────────────────────
def get_win_lines(size: int, win: int) -> list[list[int]]:
    lines = []
    for r in range(size):
        for c in range(size - win + 1):
            lines.append([r * size + c + k for k in range(win)])
    for c in range(size):
        for r in range(size - win + 1):
            lines.append([(r + k) * size + c for k in range(win)])
    for r in range(size - win + 1):
        for c in range(size - win + 1):
            lines.append([(r + k) * size + c + k for k in range(win)])
    for r in range(size - win + 1):
        for c in range(win - 1, size):
            lines.append([(r + k) * size + c - k for k in range(win)])
    return lines


WIN_LINES = get_win_lines(SIZE, WIN)


def calculate_winner(squares: list[str]) -> str | None:
    for line in WIN_LINES:
        vals = [squares[i] for i in line]
        if vals[0] and all(v == vals[0] for v in vals):
            return vals[0]
    return None


def minimax(squares: list[str], is_maximizing: bool, depth: int = 0, max_depth: int = 3) -> int:
    winner = calculate_winner(squares)
    if winner == "X": return -10 + depth
    if winner == "O": return 10 - depth
    if all(squares) or depth >= max_depth: return 0
    scores = []
    for i in range(SIZE * SIZE):
        if squares[i]: continue
        sq = squares[:]
        sq[i] = "O" if is_maximizing else "X"
        scores.append(minimax(sq, not is_maximizing, depth + 1, max_depth))
    return (max if is_maximizing else min)(scores)


def best_ai_move(squares: list[str], difficulty: str) -> int:
    empty = [i for i in range(SIZE * SIZE) if not squares[i]]
    if difficulty == "Easy":
        return random.choice(empty)
    if difficulty == "Medium" and random.random() < 0.5:
        return random.choice(empty)
    best_score, best_i = -math.inf, -1
    for i in empty:
        sq = squares[:]
        sq[i] = "O"
        score = minimax(sq, False)
        if score > best_score:
            best_score, best_i = score, i
    return best_i


# ── Square ────────────────────────────────────────────────────
@ft.component
def Square(value: str, on_click, control_key=None):
    if value == "X":
        color, bgcolor, border_color = ACCENT_X, "#1e0a10", ACCENT_X
    elif value == "O":
        color, bgcolor, border_color = ACCENT_O_LIGHT, "#051520", ACCENT_O_LIGHT
    else:
        color, bgcolor, border_color = TEXT_DIM, CARD, BORDER

    return ft.Container(
        content=ft.Container(
            ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
            alignment=ft.Alignment(0, 0),
        ),
        key=control_key,
        width=62, height=62,
        bgcolor=bgcolor,
        border=ft.Border.all(2, border_color),
        border_radius=10,
        on_click=on_click,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        ink=True,
    )


# ── Scoreboard ────────────────────────────────────────────────
@ft.component
def Scoreboard(score_x: int, score_o: int, round_num: int, ai_mode: bool,
               difficulty: str, on_toggle_mode, on_change_difficulty):
    x_label = "X (You)" if ai_mode else "X"
    o_label = f"O (AI·{difficulty})" if ai_mode else "O"

    diff_btns = ft.Row(
        [
            ft.TextButton(
                content=ft.Text(d, size=11,
                    color=ACCENT_O_LIGHT if d == difficulty else TEXT_DIM,
                    weight=ft.FontWeight.BOLD if d == difficulty else ft.FontWeight.NORMAL),
                on_click=lambda e, d=d: on_change_difficulty(d),
            )
            for d in ["Easy", "Medium", "Hard"]
        ],
        spacing=0,
        visible=ai_mode,
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(f"Round {round_num}", size=13, color=TEXT_DIM, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.TextButton(
                    content=ft.Text("vs AI" if not ai_mode else "vs Human", size=12, color=ACCENT_O_LIGHT),
                    on_click=on_toggle_mode,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            diff_btns,
            ft.Row([
                ft.Column([
                    ft.Text(x_label, size=12, color=ACCENT_X, weight=ft.FontWeight.BOLD),
                    ft.Text(str(score_x), size=28, weight=ft.FontWeight.BOLD, color=ACCENT_X),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Text("—", size=18, color=TEXT_DIM),
                ft.Column([
                    ft.Text(o_label, size=12, color=ACCENT_O_LIGHT, weight=ft.FontWeight.BOLD),
                    ft.Text(str(score_o), size=28, weight=ft.FontWeight.BOLD, color=ACCENT_O_LIGHT),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ], spacing=4),
        bgcolor=SURFACE, border_radius=16, padding=16,
        border=ft.Border.all(1, BORDER),
    )


# ── Board ─────────────────────────────────────────────────────
@ft.component
def Board(x_is_next: bool, squares: list[str], on_play,
          score_x: int, score_o: int, round_num: int,
          ai_mode: bool, difficulty: str,
          on_toggle_mode, on_change_difficulty, on_new_round):

    winner = calculate_winner(squares)
    is_draw = not winner and all(squares)

    def handle_click(e, i: int):
        if squares[i] or winner or is_draw:
            return
        sq = squares[:]
        sq[i] = "X" if x_is_next else "O"
        if ai_mode and not calculate_winner(sq) and not all(sq):
            sq[best_ai_move(sq, difficulty)] = "O"
        on_play(sq)

    if winner:
        status_text, status_color = f"🏆  {winner} wins!", ACCENT_X if winner == "X" else ACCENT_O_LIGHT
    elif is_draw:
        status_text, status_color = "Draw!", TEXT_DIM
    else:
        player = "X" if x_is_next else "O"
        status_text = f"{'●' if x_is_next else '○'}  {player}'s turn  (4連で勝利)"
        status_color = ACCENT_X if x_is_next else ACCENT_O_LIGHT

    grid = ft.Column(
        [
            ft.Row(
                [Square(squares[r*SIZE+c], lambda e,i=r*SIZE+c: handle_click(e,i), control_key=f"sq_{r*SIZE+c}")
                 for c in range(SIZE)],
                spacing=6,
            )
            for r in range(SIZE)
        ],
        spacing=6,
    )

    return ft.Column([
        Scoreboard(score_x, score_o, round_num, ai_mode, difficulty, on_toggle_mode, on_change_difficulty),
        ft.Container(height=10),
        ft.Container(
            content=ft.Text(status_text, size=14, color=status_color, weight=ft.FontWeight.W_500),
            bgcolor=SURFACE, border_radius=8,
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            border=ft.Border.all(1, BORDER),
        ),
        ft.Container(height=8),
        ft.Container(content=grid, bgcolor=SURFACE, border_radius=16, padding=14,
                     border=ft.Border.all(1, BORDER)),
        ft.Container(height=6),
        ft.ElevatedButton(
            "Next Round →",
            on_click=lambda e: on_new_round(),
            style=ft.ButtonStyle(
                bgcolor=ACCENT_X if winner == "X" else ACCENT_O_LIGHT if winner else SURFACE,
                color=TEXT_PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            visible=bool(winner or is_draw),
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)


# ── Game ──────────────────────────────────────────────────────
@ft.component
def Game():
    squares, set_squares = ft.use_state([""] * (SIZE * SIZE))
    x_is_next, set_x_is_next = ft.use_state(True)
    score_x, set_score_x = ft.use_state(0)
    score_o, set_score_o = ft.use_state(0)
    round_num, set_round_num = ft.use_state(1)
    ai_mode, set_ai_mode = ft.use_state(False)
    difficulty, set_difficulty = ft.use_state("Medium")

    def handle_play(sq):
        winner = calculate_winner(sq)
        set_squares(sq)
        set_x_is_next(sq.count("X") == sq.count("O"))
        if winner == "X": set_score_x(score_x + 1)
        elif winner == "O": set_score_o(score_o + 1)

    def new_round():
        set_squares([""] * (SIZE * SIZE))
        set_x_is_next(True)
        set_round_num(round_num + 1)

    def toggle_mode(e):
        set_ai_mode(not ai_mode)
        set_squares([""] * (SIZE * SIZE))
        set_x_is_next(True)

    def change_difficulty(d):
        set_difficulty(d)
        set_squares([""] * (SIZE * SIZE))
        set_x_is_next(True)

    return ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("TIC TAC TOE", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Container(height=8),
                Board(x_is_next, squares, handle_play,
                      score_x, score_o, round_num,
                      ai_mode, difficulty,
                      toggle_mode, change_difficulty, new_round),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0, expand=True),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True),
        bgcolor=BG, expand=True,
    )


def main():
    def setup(page: ft.Page):
        page.bgcolor = BG
        page.title = "Tic Tac Toe"
        page.padding = 0
        page.render(Game)
    ft.run(setup)


if __name__ == "__main__":
    main()
