import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
from collections import Counter
import itertools

class PokerHandSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("德州扑克手牌选择")

        self.suits = ["♠", "♥", "♣", "♦"]
        self.suit_colors = {"♠": "black", "♥": "red", "♣": "blue", "♦": "green"}
        self.ranks = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.rank_values = {r: i for i, r in enumerate(self.ranks, start=1)}

        self.selected_suit = None
        self.selected_rank = None

        self.hand1 = []
        self.hand2 = []
        self.community_cards = []
        self.tie_hands = []  # 用于存储平局的手牌和描述

        self.create_ui()

    def create_ui(self):
        suit_frame = tk.Frame(self.root)
        suit_frame.pack()
        tk.Label(suit_frame, text="选择花色:").pack()

        for suit in self.suits:
            tk.Button(suit_frame, text=suit, fg=self.suit_colors[suit],
                      command=lambda s=suit: self.select_suit(s)).pack(side=tk.LEFT)

        rank_frame = tk.Frame(self.root)
        rank_frame.pack()
        tk.Label(rank_frame, text="选择点数:").pack()

        for rank in self.ranks[1:]:
            tk.Button(rank_frame, text=rank, command=lambda r=rank: self.select_rank(r)).pack(side=tk.LEFT)

        self.info_label = tk.Label(self.root, text="请选择玩家 1 的第一张牌")
        self.info_label.pack()

        self.progress_bar = ttk.Progressbar(self.root, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.hand_label = tk.Label(self.root, text="玩家 1: [] | 玩家 2: []")
        self.hand_label.pack()

        self.community_label = tk.Label(self.root, text="公共牌: []")
        self.community_label.pack()

        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack()

        self.reset_button = tk.Button(self.root, text="重置", command=self.reset_game)
        self.reset_button.pack()

        self.redeal_button = tk.Button(self.root, text="重发公共牌", command=self.redeal_community_cards)
        self.redeal_button.pack()

    def redeal_community_cards(self):
        if len(self.hand1) == 2 and len(self.hand2) == 2:
            self.deal_community_cards()

    def select_suit(self, suit):
        self.selected_suit = suit
        self.check_selection()

    def select_rank(self, rank):
        self.selected_rank = rank
        self.check_selection()

    def check_selection(self):
        if self.selected_suit and self.selected_rank:
            card = f"{self.selected_suit}{self.selected_rank}"
            if card in self.hand1 or card in self.hand2 or card in self.community_cards:
                messagebox.showerror("错误", "该牌已被选择！")
            else:
                self.add_card(card)

            self.selected_suit = None
            self.selected_rank = None

    def add_card(self, card):
        if len(self.hand1) < 2:
            self.hand1.append(card)
            self.info_label.config(text="请选择玩家 1 的第二张牌")
        elif len(self.hand2) < 2:
            self.hand2.append(card)
            if len(self.hand2) == 2:
                self.info_label.config(text="玩家手牌选择完成，开始计算胜率！")

                # 生成完整的扑克牌牌堆
                deck = [suit + rank for suit in self.suits for rank in self.ranks]
                used_cards = set(self.hand1 + self.hand2)  # 已选牌
                available_cards = [card for card in deck if card not in used_cards and card[1:] != "1"]

                # 使用蒙特卡罗模拟随机选择一部分公共牌组合
                num_simulations = 10000  # 模拟次数
                player1_wins, player2_wins, ties = 0, 0, 0
                for _ in range(num_simulations):
                    board = random.sample(available_cards, 5)
                    self.community_cards = list(board)
                    result = self.determine_winner()
                    if result == 1:
                        player1_wins += 1
                    elif result == 2:
                        player2_wins += 1
                    else:
                        ties += 1
                        self.tie_hands.append((self.hand1, self.hand2, self.community_cards))  # 存储平局的手牌和公共牌

                # 计算胜率
                p1_win_rate = player1_wins / num_simulations * 100
                p2_win_rate = player2_wins / num_simulations * 100
                tie_rate = ties / num_simulations * 100

                # 更新 UI 显示胜率
                self.info_label.config(
                    text=f"计算完成！玩家1胜率: {p1_win_rate:.2f}%, 玩家2胜率: {p2_win_rate:.2f}%, 平局概率: {tie_rate:.2f}%")

                # 将平局的手牌和描述写入文件
                with open('tie_hands.txt', 'w', encoding='utf-8') as file:
                    for hand1, hand2, community in self.tie_hands:
                        file.write(f"玩家1: {hand1}, 玩家2: {hand2}, 公共牌: {community}\n")

        self.update_labels()

    def add_card1(self, card):
        if len(self.hand1) < 2:
            self.hand1.append(card)
            self.info_label.config(text="请选择玩家 1 的第二张牌")
        elif len(self.hand2) < 2:
            self.hand2.append(card)
            if len(self.hand2) == 2:
                self.info_label.config(text="玩家手牌选择完成，开始计算胜率！")

                # 生成完整的扑克牌牌堆
                deck = [suit + rank for suit in self.suits for rank in self.ranks]
                used_cards = set(self.hand1 + self.hand2)  # 已选牌
                available_cards = [card for card in deck if card not in used_cards and card[1:] != "1"]

                # 遍历所有可能的5张公共牌组合
                possible_boards = list(itertools.combinations(available_cards, 5))
                total_games = len(possible_boards)
                self.progress_bar['maximum'] = total_games
                self.progress_bar['value'] = 0

                player1_wins, player2_wins, ties = 0, 0, 0
                for idx, board in enumerate(possible_boards):
                    self.community_cards = list(board)
                    result = self.determine_winner()
                    if result == 1:
                        player1_wins += 1
                    elif result == 2:
                        player2_wins += 1
                    else:
                        ties += 1
                        # self.tie_hands.append((self.hand1, self.hand2, self.community_cards))  # 存储平局的手牌和公共牌
                    self.progress_bar['value'] = idx + 1
                    self.root.update_idletasks()  # 刷新界面，更新进度条

                # 计算胜率
                p1_win_rate = player1_wins / total_games * 100
                p2_win_rate = player2_wins / total_games * 100
                tie_rate = ties / total_games * 100

                # 更新 UI 显示胜率
                self.info_label.config(
                    text=f"计算完成！玩家1胜率: {p1_win_rate:.2f}%, 玩家2胜率: {p2_win_rate:.2f}%, 平局概率: {tie_rate:.2f}%")

                # # 将平局的手牌和描述写入文件
                # with open('tie_hands.txt', 'w', encoding='utf-8') as file:
                #     for hand1, hand2, community in self.tie_hands:
                #         file.write(f"玩家1: {hand1}, 玩家2: {hand2}, 公共牌: {community}\n")

        self.update_labels()

    def update_labels(self):
        self.hand_label.config(text=f"玩家 1: {self.hand1} | 玩家 2: {self.hand2}")
        self.community_label.config(text=f"公共牌: {self.community_cards}")

    def determine_winner(self):
        lv1, head1, kicker1_1, kicker1_2, kicker1_3, kicker1_4, description1 = self.evaluate_hand(
            self.hand1 + self.community_cards)
        lv2, head2, kicker2_1, kicker2_2, kicker2_3, kicker2_4, description2 = self.evaluate_hand(
            self.hand2 + self.community_cards)

        for i, (card1, card2) in enumerate(zip([lv1, head1, kicker1_1, kicker1_2, kicker1_3, kicker1_4],
                                               [lv2, head2, kicker2_1, kicker2_2, kicker2_3, kicker2_4])):
            if card1 > card2:
                return 1
            elif card1 < card2:
                return 2
        else:
            return 0

    def is_straight(self, cards, sorted_ranks):
        is_straight = False
        is_straight_flush = False
        head = 0
        if len(sorted_ranks) < 5:
            return False, False, head
        for suit in self.suits:
            if f"{suit}A" in cards:
                cards.append(f"{suit}1")
        if 14 in sorted_ranks:
            sorted_ranks.append(1)
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i] - sorted_ranks[i + 4] == 4:
                if not is_straight:
                    head = sorted_ranks[i]
                is_straight = True
                is_straight_flush = self.is_straight_flush(cards, head)
                if is_straight_flush:
                    head = sorted_ranks[i]
                    break
        return is_straight, is_straight_flush, head

    def is_straight_flush(self, cards, head):
        suits = ["♠", "♥", "♣", "♦"]
        for suit in suits:
            suit_cards = [card for card in cards if card[0] == suit]
            suit_ranks = sorted([self.rank_values[card[1:]] for card in suit_cards], reverse=True)
            if head in suit_ranks \
                    and head - 1 in suit_ranks \
                    and head - 2 in suit_ranks \
                    and head - 3 in suit_ranks \
                    and head - 4 in suit_ranks:
                return True
        return False

    def evaluate_hand(self, cards):
        ranks = sorted([self.rank_values[card[1:]] for card in cards], reverse=True)
        rank_counts = Counter(ranks)
        suits = [card[0] for card in cards]

        sorted_ranks = sorted(set(ranks), reverse=True)
        is_flush = any(suits.count(suit) >= 5 for suit in self.suits)

        lv = 0
        kicker1 = 0
        kicker2 = 0
        kicker3 = 0
        kicker4 = 0
        description = ""

        is_straight, is_straight_flush, head = self.is_straight(cards, sorted_ranks)

        if is_straight_flush and head == 14:
            lv = 9
            description = "皇家同花顺"

        elif is_straight_flush:
            lv = 8
            description = f"同花顺 {head - 4} 到 {head}"

        elif 4 in rank_counts.values():
            lv = 7
            head = next(rank for rank, count in rank_counts.items() if count == 4)
            remaining_ranks = {rank: count for rank, count in rank_counts.items() if rank != head}
            kicker1 = max(remaining_ranks, key=remaining_ranks.get)
            description = f"四条 {head} 带踢脚 {kicker1}"

        elif (3 in rank_counts.values() and 2 in rank_counts.values()) or list(rank_counts.values()).count(3) >= 2:
            lv = 6
            three_of_a_kinds = sorted([rank for rank, count in rank_counts.items() if count == 3], reverse=True)
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)

            if len(three_of_a_kinds) >= 2:
                head = three_of_a_kinds[0]
                kicker1 = three_of_a_kinds[1]
            else:
                head = three_of_a_kinds[0]
                kicker1 = pairs[0]

            description = f"葫芦 {head} 带一对 {kicker1}"

        elif is_flush:
            lv = 5
            suit_counts = {suit: sum(1 for card in cards if card[0] == suit) for suit in self.suits}
            max_suit = max(suit_counts, key=suit_counts.get)
            suit_cards = [card for card in cards if card[0] == max_suit]
            sorted_suit_cards = sorted(suit_cards, key=lambda card: self.rank_values[card[1:]], reverse=True)
            top_5_cards = sorted_suit_cards[:5]
            sorted_ranks = [self.rank_values[card[1:]] for card in top_5_cards]
            head = sorted_ranks[0]
            kicker1 = sorted_ranks[1]
            kicker2 = sorted_ranks[2]
            kicker3 = sorted_ranks[3]
            kicker4 = sorted_ranks[4]
            description = f"同花 {sorted_ranks[:5]}"

        elif is_straight:
            lv = 4
            description = f"顺子 {head - 4} 到 {head}"

        elif max(rank_counts.values()) == 3:
            lv = 3
            head = next(rank for rank, count in rank_counts.items() if count == 3)
            kickers = [rank for rank, count in rank_counts.items() if count == 1]
            kickers.sort(reverse=True)
            kicker1 = kickers[0]
            kicker2 = kickers[1]
            description = f"三条 {head} 带踢脚 {kicker1}{kicker2}"

        elif sorted(rank_counts.values(), reverse=True)[:2] == [2, 2]:
            lv = 2
            pairs = [rank for rank, count in rank_counts.items() if count == 2]
            pairs.sort(reverse=True)
            head = pairs[0]
            kicker1 = pairs[1]
            kicker2 = next(rank for rank, count in rank_counts.items() if count == 1)
            description = f"两对 {head} 和 {kicker1} 带踢脚 {kicker2}"

        elif 2 in rank_counts.values():
            lv = 1
            head = next(rank for rank, count in rank_counts.items() if count == 2)
            kickers = [rank for rank, count in rank_counts.items() if count == 1]
            kickers.sort(reverse=True)
            kicker1 = kickers[0]
            kicker2 = kickers[1]
            kicker3 = kickers[2]
            description = f"一对 {head} 带踢脚 {kicker1}{kicker2}{kicker3}"

        else:
            lv = 0
            kickers = [rank for rank, count in rank_counts.items() if count == 1]
            kickers.sort(reverse=True)
            head = kickers[0]
            kicker1 = kickers[1]
            kicker2 = kickers[2]
            kicker3 = kickers[3]
            kicker4 = kickers[4]
            description = f"高牌 {head} 带踢脚 {kicker1}{kicker2}{kicker3}{kicker4}"

        return lv, head, kicker1, kicker2, kicker3, kicker4, description

    def reset_game(self):
        self.hand1.clear()
        self.hand2.clear()
        self.community_cards.clear()
        self.info_label.config(text="请选择玩家 1 的第一张牌")
        self.update_labels()
        self.result_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerHandSelector(root)
    root.mainloop()