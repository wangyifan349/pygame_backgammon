import random
from enum import Enum, unique
from collections import Counter

# 初始化牌组
def init_deck():
    suits = ['♠', '♥', '♣', '♦']
    ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
    deck = ['大王', '小王'] + [rank + suit for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

# 发牌
def deal_cards(deck):
    landlord_cards = deck[:20]
    farmer1_cards = deck[20:37]
    farmer2_cards = deck[37:54]
    bottom_cards = deck[54:]
    return landlord_cards, farmer1_cards, farmer2_cards, bottom_cards

# 叫地主（简化为随机选择地主）
def bid_landlord(players):
    return random.choice(players)

# 定义牌的大小
card_value_dict = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                   'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17}

# 获取牌的大小
def get_card_value(card):
    if card in ['大王', '小王']:
        return card_value_dict[card]
    else:
        # 对于 '10♠' 这样的牌，我们需要提取前两个字符作为牌的大小
        return card_value_dict[card[:-1]]

@unique
class CardType(Enum):
    INVALID = 0
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    TRIPLE_WITH_SINGLE = 4
    TRIPLE_WITH_PAIR = 5
    STRAIGHT = 6
    CONSECUTIVE_PAIRS = 7
    PLANE = 8
    PLANE_WITH_WINGS = 9
    FOUR_WITH_TWO = 10
    FOUR_WITH_TWO_PAIRS = 11
    BOMB = 12
    ROCKET = 13

# 基本牌型检测函数
def check_card_type(cards):
    cards = sorted(cards, key=lambda x: get_card_value(x))
    card_counts = Counter(cards)
    values_count = list(card_counts.values())

    # 王炸
    if '小王' in cards and '大王' in cards and len(cards) == 2:
        return CardType.ROCKET, get_card_value('小王')
    # 炸弹
    elif values_count.count(4) == 1 and len(cards) == 4:
        bomb_value = get_card_value(card_counts.most_common(1)[0][0])
        return CardType.BOMB, bomb_value
    # 单张
    elif len(cards) == 1:
        return CardType.SINGLE, get_card_value(cards[0])
    # 对子
    elif len(cards) == 2 and values_count.count(2) == 1:
        return CardType.PAIR, get_card_value(cards[0])
    # 三不带
    elif len(cards) == 3 and values_count.count(3) == 1:
        return CardType.TRIPLE, get_card_value(cards[0])
    # 三带一
    elif len(cards) == 4 and values_count.count(3) == 1:
        triple_value = get_card_value(card_counts.most_common(1)[0][0])
        return CardType.TRIPLE_WITH_SINGLE, triple_value
    # 三带对
    elif len(cards) == 5 and values_count.count(3) == 1 and values_count.count(2) == 1:
        triple_pair_value = get_card_value(card_counts.most_common(1)[0][0])
        return CardType.TRIPLE_WITH_PAIR, triple_pair_value
    # 连对
    elif len(set(values_count)) == 1 and values_count[0] == 2 and len(cards) >= 6 and get_card_value(cards[-1]) - get_card_value(cards[0]) == len(cards) / 2 - 1:
        return CardType.CONSECUTIVE_PAIRS, get_card_value(cards[0])
    # 顺子
    elif len(set(values_count)) == 1 and values_count[0] == 1 and len(cards) >= 5 and get_card_value(cards[-1]) - get_card_value(cards[0]) == len(cards) - 1:
        return CardType.STRAIGHT, get_card_value(cards[0])
    # 四带二
    elif len(cards) == 6 and values_count.count(4) == 1 and values_count.count(1) == 2:
        four_value = get_card_value(card_counts.most_common(1)[0][0])
        return CardType.FOUR_WITH_TWO, four_value
    # 四带两对
    elif len(cards) == 8 and values_count.count(4) == 1 and values_count.count(2) == 2:
        four_pair_value = get_card_value(card_counts.most_common(1)[0][0])
        return CardType.FOUR_WITH_TWO_PAIRS, four_pair_value
    # 飞机不带翅膀
    elif len(set(values_count)) == 1 and values_count[0] == 3 and len(cards) >= 6 and get_card_value(cards[-1]) - get_card_value(cards[0]) == len(cards) / 3 - 1:
        return CardType.PLANE, get_card_value(cards[0])
    # 飞机带小翅膀
    elif len(cards) > 5 and values_count.count(3) > 1 and sorted(values_count)[-2] == 3:
        sorted_cards = sorted(cards, key=lambda x: (get_card_value(x), -values_count[x]))
        plane_values = [get_card_value(card) for card in sorted_cards if values_count[card] == 3]
        if len(plane_values) >= 2 and all(b - a == 1 for a, b in zip(plane_values, plane_values[1:])):
            return CardType.PLANE_WITH_WINGS, plane_values[0]
    # 飞机带大翅膀
    elif len(cards) > 9 and values_count.count(3) > 1 and sorted(values_count)[-2] == 3 and values_count.count(1) == 0 and values_count.count(2) == values_count.count(3):
        sorted_cards = sorted(cards, key=lambda x: (get_card_value(x), -values_count[x]))
        plane_values = [get_card_value(card) for card in sorted_cards if values_count[card] == 3]
        if len(plane_values) >= 2 and all(b - a == 1 for a, b in zip(plane_values, plane_values[1:])):
            return CardType.PLANE_WITH_WINGS, plane_values[0]
    # 其他牌型待补充...

    return CardType.INVALID, 0

# 比较牌型大小的函数需要修改炸弹之间的比较逻辑
def compare_cards(last_cards, current_cards):
    last_type, last_value = check_card_type(last_cards)
    current_type, current_value = check_card_type(current_cards)

    # 如果一方出的是无效牌型，另一方只要是有效牌型即可大过
    if last_type == CardType.INVALID and current_type != CardType.INVALID:
        return True
    # 如果一方出的是王炸，另一方无论出什么都小于王炸
    if current_type == CardType.ROCKET:
        return True
    # 如果一方出的是炸弹，而另一方不是炸弹或王炸，则大于另一方
    if current_type == CardType.BOMB:
        if last_type != CardType.BOMB:
            return True
        else:
            # 两个炸弹相比较，大的炸弹赢
            return current_value > last_value
    # 如果两方出的牌型相同，则比较牌型的大小
    if current_type == last_type and len(current_cards) == len(last_cards):
        return current_value > last_value
    return False
def main():
    players = ['玩家A', '玩家B', '玩家C']
    pass_count = 0  # 用于跟踪连续过牌的次数
    deck = init_deck()
    landlord_cards, farmer1_cards, farmer2_cards, bottom_cards = deal_cards(deck)
    landlord = bid_landlord(players)
    if landlord:
        print(f"{landlord} 成为地主！")
        # 分发底牌给地主
        if landlord == '玩家A':
            landlord_cards += bottom_cards
        elif landlord == '玩家B':
            farmer1_cards += bottom_cards
        else:
            farmer2_cards += bottom_cards

    # 初始化玩家手牌
    player_hands = {
        '玩家A': landlord_cards,
        '玩家B': farmer1_cards,
        '玩家C': farmer2_cards
    }

    # 打印玩家手牌
    for player, cards in player_hands.items():
        print(f"{player}的手牌：{cards}")

    # 游戏开始
    turn = landlord  # 地主先出牌
    last_played_cards = []
    while True:
        # 对手牌排序
        hand.sort(key=lambda x: get_card_value(x))
        print(f"你的手牌：{' '.join(hand)}")
        card_input = input("请选择出牌（输入牌的字符串，用空格分隔），或输入'pass'过牌：").strip()
        # 检查玩家是否选择过牌
        if card_input.lower() == 'pass':
            if pass_count < 2:  # 如果前两个玩家没有都过牌，可以过牌
                pass_count += 1
                print(f"{turn}选择过牌。")
            else:
                print("连续两个玩家已经过牌，您必须出牌。")
                continue
        else:
            try:
                current_cards = card_input.split()
                # 验证选择的牌是否在手牌中
                if all(hand.count(card) >= current_cards.count(card) for card in current_cards):
                    # 验证出牌是否符合规则
                    if (not last_played_cards or compare_cards(last_played_cards, current_cards)):
                        # 出牌有效，移除手牌
                        for card in current_cards:
                            hand.remove(card)
                        last_played_cards = current_cards
                        pass_count = 0  # 重置过牌计数
                        print(f"{turn}出牌：{' '.join(current_cards)}")
                        # 检查是否有玩家赢了游戏
                        if not hand:
                            print(f"{turn}赢得了游戏！")
                            break
                    else:
                        print("无效的出牌，请重新选择！")
                        continue
                else:
                    print("选择的牌不在你的手牌中，请重新选择！")
                    continue
            except Exception as e:
                print("出现错误：", e)
                print("请按正确格式输入牌！")
                continue
        # 轮到下一个玩家
        turn = players[(players.index(turn) + 1) % 3]
if __name__ == "__main__":
    main()
