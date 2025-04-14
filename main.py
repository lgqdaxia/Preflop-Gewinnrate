import tkinter as tk
import random

suits = ["♠", "♥", "♦", "♣"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
rank_values = {r: i for i, r in enumerate(ranks, start=2)}

# 玩家初始筹码
player1_chips = 100
player2_chips = 100
pot = 1  # 底池（盲注）
player1_chips -= 0.5
player2_chips -= 0.5

# 当前玩家（1 表示玩家1，2 表示玩家2，None 表示游戏结束）
current_player = 1

# 玩家下注
player1_bet = 0
player2_bet = 0


# 生成随机牌
def get_random_card():
    return f"{random.choice(suits)}{random.choice(ranks)}"


# 计算牌型权重
def get_hand_value(hand):
    hand_ranks = sorted([rank_values[card[1:]] for card in hand], reverse=True)
    is_flush = len(set(card[0] for card in hand)) == 1
    is_straight = hand_ranks == list(range(hand_ranks[0], hand_ranks[0] - 3, -1))
    rank_counts = {r: hand_ranks.count(r) for r in hand_ranks}

    if len(rank_counts) == 1:
        return (6, hand_ranks)
    if is_straight and is_flush:
        return (5, hand_ranks)
    if is_flush:
        return (4, hand_ranks)
    if is_straight:
        return (3, hand_ranks)
    if 2 in rank_counts.values():
        return (2, hand_ranks)
    return (1, hand_ranks)


# 判断赢家
def determine_winner():
    global player1_chips, player2_chips, pot
    value1, value2 = get_hand_value(player1_hand), get_hand_value(player2_hand)
    if value1 > value2:
        result.set("玩家 1 胜!")
        player1_chips += pot
    elif value1 < value2:
        result.set("玩家 2 胜!")
        player2_chips += pot
    else:
        result.set("平局！")
        player1_chips += pot // 2
        player2_chips += pot // 2
    pot = 1
    update_ui()


# 处理玩家行动
def player_action(action):
    global pot, player1_chips, player2_chips, current_player, player1_bet, player2_bet
    if action == "过牌":
        result.set(f"玩家 {current_player} 过牌")
        if current_player == 1:
            current_player = 2  # 轮到玩家 2
        else:
            current_player = 1  # 轮到玩家 1
    elif action == "加注":
        bet = pot // 2
        if current_player == 1:
            if bet > player1_chips:
                bet = player1_chips  # 如果筹码不足，则只能全下
            player1_chips -= bet
            pot += bet
            player1_bet += bet
            result.set(f"玩家 1 加注，轮到玩家 2")
            current_player = 2  # 轮到玩家 2
        elif current_player == 2:
            if bet > player2_chips:
                bet = player2_chips  # 如果筹码不足，则只能全下
            player2_chips -= bet
            pot += bet
            player2_bet += bet
            result.set(f"玩家 2 加注，轮到玩家 1")
            current_player = 1  # 轮到玩家 1
    elif action == "全下":
        if current_player == 1:
            pot += player1_chips
            player1_chips = 0
            player1_bet += pot
            result.set("玩家 1 全下，轮到玩家 2")
            current_player = 2
        elif current_player == 2:
            pot += player2_chips
            player2_chips = 0
            player2_bet += pot
            result.set("玩家 2 全下，轮到玩家 1")
            current_player = 1
    elif action == "跟注":
        if current_player == 1:
            bet = player2_bet - player1_bet
            player1_chips -= bet
            pot += bet
            player1_bet = player2_bet
            result.set(f"玩家 1 跟注，轮到玩家 2")
            current_player = 2
        elif current_player == 2:
            bet = player1_bet - player2_bet
            player2_chips -= bet
            pot += bet
            player2_bet = player1_bet
            result.set(f"玩家 2 跟注，轮到玩家 1")
            current_player = 1
    elif action == "弃牌":
        if current_player == 1:
            result.set("玩家 2 获胜！")
            player2_chips += pot
            pot = 1
            current_player = None  # 游戏结束
        elif current_player == 2:
            result.set("玩家 1 获胜！")
            player1_chips += pot
            pot = 1
            current_player = None  # 游戏结束

    update_ui()


# 发牌
def deal_cards():
    global player1_hand, player2_hand, player1_bet, player2_bet, pot, current_player
    player1_hand = [get_random_card() for _ in range(3)]
    player2_hand = [get_random_card() for _ in range(3)]
    player1_cards.set(" ".join(player1_hand))
    player2_cards.set(" ".join(player2_hand))

    # 重置游戏状态
    player1_bet = player2_bet = 0
    pot = 1  # 初始化底池（盲注）
    player1_chips -= 0.5
    player2_chips -= 0.5
    current_player = 1  # 玩家1先行动

    update_ui()


# 更新 UI
def update_ui():
    # 更新筹码和底池显示
    player1_chip_display.set(f"玩家 1 筹码: {player1_chips} BB")
    player2_chip_display.set(f"玩家 2 筹码: {player2_chips} BB")
    pot_display.set(f"底池: {pot} BB")

    # 更新操作按钮状态
    if current_player == 1:
        # 玩家1的操作按钮
        check_button.config(state="normal" if player1_bet == 0 else "disabled")
        raise_button.config(state="normal" if player1_bet == 0 else "disabled")
        allin_button.config(state="normal" if player1_bet == 0 else "disabled")
        call_button.config(state="disabled")
        fold_button.config(state="normal")
    elif current_player == 2:
        # 玩家2的操作按钮
        check_button.config(state="normal" if player2_bet == 0 else "disabled")
        raise_button.config(state="normal" if player2_bet == 0 else "disabled")
        allin_button.config(state="normal" if player2_bet == 0 else "disabled")
        call_button.config(state="disabled")
        fold_button.config(state="normal")
    elif current_player is None:
        # 游戏结束时，禁用所有按钮
        check_button.config(state="disabled")
        raise_button.config(state="disabled")
        allin_button.config(state="disabled")
        call_button.config(state="disabled")
        fold_button.config(state="disabled")


# 创建窗口
root = tk.Tk()
root.title("扎金花 - 发牌 & 比牌")
root.geometry("1600x1400")
root.resizable(False, False)

# 玩家 1 信息 (左侧)
frame1 = tk.Frame(root)
frame1.grid(row=0, column=0, padx=20, pady=20)
tk.Label(frame1, text="玩家 1", font=("Arial", 12)).pack()
player1_cards = tk.StringVar()
tk.Label(frame1, textvariable=player1_cards, font=("Arial", 14)).pack()
player1_chip_display = tk.StringVar()
tk.Label(frame1, textvariable=player1_chip_display).pack()
player1_bet_display = tk.StringVar()
tk.Label(frame1, textvariable=player1_bet_display).pack()

# 玩家 2 信息 (右侧)
frame2 = tk.Frame(root)
frame2.grid(row=0, column=2, padx=20, pady=20)
tk.Label(frame2, text="玩家 2", font=("Arial", 12)).pack()
player2_cards = tk.StringVar()
tk.Label(frame2, textvariable=player2_cards, font=("Arial", 14)).pack()
player2_chip_display = tk.StringVar()
tk.Label(frame2, textvariable=player2_chip_display).pack()
player2_bet_display = tk.StringVar()
tk.Label(frame2, textvariable=player2_bet_display).pack()

# 底池信息 (中央)
pot_display = tk.StringVar()
pot_label = tk.Label(root, textvariable=pot_display, font=("Arial", 12, "bold"))
pot_label.grid(row=0, column=1, padx=20, pady=20)

# 游戏状态（中央）
result = tk.StringVar()
result_label = tk.Label(root, textvariable=result, font=("Arial", 12))
result_label.grid(row=1, column=1, padx=20, pady=20)

# 操作按钮
check_button = tk.Button(root, text="过牌", command=lambda: player_action("过牌"))
check_button.grid(row=2, column=1, padx=20, pady=10)
raise_button = tk.Button(root, text="加注", command=lambda: player_action("加注"))
raise_button.grid(row=3, column=1, padx=20, pady=10)
allin_button = tk.Button(root, text="全下", command=lambda: player_action("全下"))
allin_button.grid(row=4, column=1, padx=20, pady=10)
call_button = tk.Button(root, text="跟注", command=lambda: player_action("跟注"))
call_button.grid(row=5, column=1, padx=20, pady=10)
fold_button = tk.Button(root, text="弃牌", command=lambda: player_action("弃牌"))
fold_button.grid(row=6, column=1, padx=20, pady=10)

# 重新发牌按钮
deal_button = tk.Button(root, text="重新发牌", command=deal_cards)
deal_button.grid(row=7, column=1, padx=20, pady=20)

root.mainloop()
