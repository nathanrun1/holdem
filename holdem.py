from cards import *
import random
import numpy as np
import time

default_rules = {
    "DEFAULT_BANKROLL": 1000,
    "BIG_BLIND": 10,
    "SMALL_BLIND": 5,
    "MAX_PLAYERS": 6
}

POKER_HANDS = {
    10: "Royal Flush",
    9: "Straight Flush",
    8: "Four of a Kind",
    7: "Full House",
    6: "Flush",
    5: "Straight",
    4: "Three of a Kind",
    3: "Two Pair",
    2: "Pair",
    1: "High Card"
}

class Player:
    def __init__(self, **kwargs):
        name = kwargs.get("name")
        id = kwargs.get("id") # for hashing
        initial_bankroll = kwargs.get("bankroll")
        if name is None:
            self.name = f"Player{random.randint(0, 100)}"
        else:
            self.name = name
        if initial_bankroll is None:
            self.bankroll = default_rules["DEFAULT_BANKROLL"]
        else:
            self.bankroll = initial_bankroll

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name, self.id)


class Board:
    def __init__(self, deck, showall=False):
        self.cards = [deck.draw() for i in range(5)]
        self.flop = False
        self.turn = False
        self.turn_card = False
        self.river = False
        self.river_card = False
        if showall:
            self.deal_flop()
            self.deal_turn()
            self.deal_river()

    def deal_flop(self):
        self.flop = [self.cards[0], self.cards[1], self.cards[2]]
        return self.flop

    def deal_turn(self):
        self.turn = self.flop + [self.cards[3]]
        self.turn_card = self.cards[3]
        return self.turn_card

    def deal_river(self):
        self.river = self.cards
        self.river_card = self.cards[4]
        return self.river_card


    def __str__(self):
        return (f"Board: {(" ".join(map(lambda card: card.sec_display_str, self.flop)) + " "
                           if self.flop else "? ? ? ")}"
                f"{str(self.turn_card) + " " if self.turn else "? "}{str(self.river_card) + " " if self.river else "?"}")



class Hole:
    def __init__(self, deck, player=None):
        self.cards = [deck.draw(), deck.draw()]
        self.player = player

    def __str__(self):
        return " ".join(map(lambda card: card.sec_display_str, self.cards))


class Hand:
    def __init__(self, **kwargs):
        hole = kwargs.get("hole")
        board = kwargs.get("board")
        cards = kwargs.get("cards")
        if cards:
            self.cards = cards
            self.player = None
        elif board and hole:
            self.cards = hole.cards + board.cards
            self.player = hole.player
        calc_hand = get_hand(self.cards)
        self.hand = calc_hand[0]
        self.rank = calc_hand[1]
        self.high_card = self.hand[0]
        self.rank_str = calc_hand[2]

    def __str__(self):
        return " ".join(map(lambda card : card.sec_display_str, self.hand)) + ", " + self.rank_str

    def __cmp__(self, other):
        if self.rank > other.rank or (self.rank == other.rank and self.high_card > other.high_card):
            return 1
        elif self.rank < other.rank or (self.rank == other.rank and self.high_card < other.high_card):
            return -1
        elif self.rank == other.rank and self.high_card == other.high_card:
            return 0

    def __eq__(self, other):
        if self.rank == other.rank:
            for i in range(5):
                if self.hand[i] != other.hand[i]:
                    return False
            return True
        else:
            return False


    def __gt__(self, other):
        if self.rank == other.rank:
            for i in range(5):
                if self.hand[i] != other.hand[i]:
                    return self.hand[i] > other.hand[i]
            return False
        else:
            return self.rank > other.rank

    def __lt__(self, other):
        if self.rank == other.rank:
            for i in range(5):
                if self.hand[i] != other.hand[i]:
                    return self.hand[i] < other.hand[i]
            return False
        else:
            return self.rank < other.rank

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    def __ne__(self, other):
        return not self.__eq__(other)



# sort_cards(cards) sorts a list of cards in descending order by rank
def sort_cards(cards):
    return np.flip(np.sort(cards))

# get_straight(cards) gets the highest straight in a list of cards and returns it,
#   if no straight exists, returns False
def get_straight(cards):
    cards = sort_cards(cards)
    straight = []
    for card in cards:
        straight.append(card)
        card_rank = card.rank_val()
        if card_rank == 1:
            card_rank = 14
        for i in range(4):
            if any((c for c in cards.copy() if c.rank_val() == (card_rank - 1 - i))):
                straight.append(next(c for c in cards.copy() if c.rank_val() == (card_rank - 1 - i)))
            else:
                straight = []
                break
        if len(straight) == 5:
            return np.flip(straight).tolist()
        else:
            continue
    return False

# get_cards_of_suit(cards, suit) returns a sorted list of all cards in provided list of cards that are of
#   provided suit, returns False if none
def get_cards_of_suit(cards, suit):
    cards_of_suit = []
    for card in cards:
        if card.suit == suit:
            cards_of_suit.append(card)
    if not cards_of_suit:
        return False
    else:
        return sort_cards(cards_of_suit)

# get_flush(cards) gets the highest flush in a list of cards and returns it,
#   if no flush, returns False
def get_flush(cards):
    h = 0
    s = 0
    c = 0
    d = 0
    flush_suit = False
    for card in cards:
        if card.suit == "h":
            h += 1
            if h >= 5:
                flush_suit = "h"
                break
        elif card.suit == "s":
            s += 1
            if s >= 5:
                flush_suit = "s"
                break
        elif card.suit == "c":
            c += 1
            if c >= 5:
                flush_suit = "c"
                break
        else:
            d += 1
            if d >= 5:
                flush_suit = "d"
                break
    if flush_suit:
        return get_cards_of_suit(cards, flush_suit).tolist()[:5]

# get_straight_flush(cards) returns the highest straight flush that can be made with provided cards, returns
#   False if none
def get_straight_flush(cards):
    flush = get_flush(cards)
    if flush:
        flush_suit = flush[0].suit
        straight_flush = get_straight(get_cards_of_suit(cards, flush_suit)) # assumes only one suit can make flush
        return straight_flush

# get_pair(cards) returns the highest pair that can be made with provided cards, returns False if none
def get_pair(cards):
    cards = sort_cards(cards)
    index = 0
    for card in cards:
        if (len(cards) - 1) > index: # at least one position after
            next_card = cards[index + 1]
            high_cards = np.delete(cards, np.where(cards == card))[:3]
            if next_card == card:
                return np.concatenate([[card, next_card], high_cards]).tolist()
        index += 1
    return False

# get_two_pair(cards) returns the highest two pair that can be made with provided cards, returns False if none
def get_two_pair(cards):
    first_pair = get_pair(cards)
    if first_pair:
        first_pair = first_pair[:2]
        cards = np.array(cards)
        second_pair = get_pair(np.delete(cards, np.where(cards == first_pair[0])))
        if second_pair:
            second_pair = second_pair[:3]
        if first_pair and second_pair:
            return first_pair + second_pair
        else:
            return False


# get_three_of_kind(cards) returns the highest three of a kind that can be made with provided cards,
#   returns False if none
def get_three_of_kind(cards):
    cards = sort_cards(cards)
    index = 0
    for card in cards:
        if (len(cards) - 1) > (index + 1):  # at least two positions after
            test_cards = cards[index:(index + 3)]
            if np.all(test_cards == test_cards[0]):
                high_cards = np.delete(cards, np.where(cards == card))[:2]
                return np.concatenate([test_cards, high_cards]).tolist()
        index += 1
    return False

# get_full_house(cards) returns the highest full house that can be made with provided cards,
#   returns False if none
def get_full_house(cards):
    cards = np.array(cards)
    three_of_kind = get_three_of_kind(cards)
    if three_of_kind:
        three_of_kind = three_of_kind[:3]
        pair = get_pair(np.delete(cards, np.where(cards == three_of_kind[0])))
        if pair:
            pair = pair[:2]
        if pair:
            return three_of_kind + pair
        else:
            return False
    else:
        return False

# get_four_of_kind(cards) returns the highest four of a kind that can be made with provided cards,
#   returns False if none
def get_four_of_kind(cards):
    cards = sort_cards(cards)
    index = 0
    for card in cards:
        if (len(cards) - 1) > (index + 2):  # at least three positions after
            test_cards = cards[index:(index + 4)]
            if np.all(test_cards == test_cards[0]):
                high_cards = np.delete(cards, np.where(cards == card))[:1]
                return np.concatenate([test_cards, high_cards]).tolist()
        index += 1
    return False





# get_hand(cards) gets the best poker hand that can be made using given list of cards
def get_hand(cards):
    sf = get_straight_flush(cards)
    if sf:
        if sf[4] == Card(rank="A"):
            return (sf, 10, "Royal Flush")
        else:
            return (sf, 9, f"Straight Flush, {sf[4].rank_name} high")
    fk = get_four_of_kind(cards)
    if fk:
        return (fk, 8, f"Four of a Kind, {fk[0].rank_name}s")
    fh = get_full_house(cards)
    if fh:
        return (fh, 7, f"Full House, {fh[0].rank_name}s full of {fh[3].rank_name}s")
    fl = get_flush(cards)
    if fl:
        return (fl, 6, f"Flush, {fl[0].rank_name} high")
    str = get_straight(cards)
    if str:
        return (str, 5, f"Straight, {str[4].rank_name} high")
    tk = get_three_of_kind(cards)
    if tk:
        return (tk, 4, f"Three of a kind, {tk[0].rank_name}s")
    tp = get_two_pair(cards)
    if tp:
        return (tp, 3, f"Two Pair, {tp[0].rank_name}s and {tp[2].rank_name}s")
    pr = get_pair(cards)
    if pr:
        return (pr, 2, f"Pair of {pr[0].rank_name}s")
    hk = sort_cards(cards)[:5]
    return (hk, 1, f"{hk[0].rank_name} high")






sorted = sort_cards(Board(Deck()).cards)
royal_flush = False
cooler = False
round = 0
while not cooler:
    round += 1
    deck = Deck()
    hole_cards = [Hole(deck, Player(name=f"Player{i}")) for i in range(8)]
    board = Board(deck, showall=True)
    print(board)
    for plr in hole_cards:
        print(f"{plr.player}: {plr}")
    hands = [Hand(hole=hole, board=board) for hole in hole_cards]
    if any(hand.rank == 10 for hand in hands):
        cooler = True
        print(f"COOLER ON ROUND {round}")
    print("\n".join(f"{hand.player}: " + hand.__str__() for hand in hands))
    print(f"Winner: {max(hands).player}")