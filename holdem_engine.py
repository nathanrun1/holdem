from holdem import *
from cards import *

class Pot:
    def __init__(self, players, rules):
        if rules is None:
            self.rules = default_rules
        else:
            self.rules = rules
        self.value = 0
        self.bets = {}
        self.history = []
        self.players = players
        self.side_pots = []
        self.highest_bet = 0
        self.recent_raise = 0

    def action(self, player):
        if player.bankroll > 0:
            print(f"{player}'s action\nPot: ${self.value}\nCurrent bet: ${self.highest_bet}")
            plr_bet = 0
            if player in self.bets:
                plr_bet = self.bets[player]
                print(f"Your bet: ${plr_bet}")
            min_raise = 0
            if self.highest_bet == 0:
                min_raise = self.rules["BIG_BLIND"]
            else:
                min_raise = self.recent_raise + self.highest_bet
            to_call = self.highest_bet - plr_bet
            min_to_raise = min_raise - plr_bet
            max_raise = player.bankroll + plr_bet
            options = []
            plr_action = None
            if self.highest_bet == 0:
                # Checks to player
                if plr.bankroll < min_to_raise: # in this case, player has less than one BB
                    options = ["C", "A"]
                    plr_action = input(f"Action? (C)heck or (A)ll in for ${plr.bankroll}")
                else:
                    options = ["C", "B"]
                    plr_action = input(f"Action? (C)heck or (B)et")
            else:
                # Someone has bet
                if plr.bankroll < to_call: # player must jam to call
                    options = ["F", "A"]
                    plr_action = input(f"Action? (F)old or (A)ll in for ${plr.bankroll} to call")
                elif plr.bankroll < min_to_raise: # player must jam to raise, or can call
                    options = ["F", "C", "A"]
                    plr_action = input(f"Action? (F)old, (C)all for ${to_call}, or raise (A)ll in for ${plr.bankroll}")
                else:
                    options = ["F", "C", "R"]
                    plr_action = input(f"Action? (F)old, (C)all for ${to_call}, or (R)aise")
            if plr_action == "F" and "F" in options:
                self.players.remove(player)
                print(f"{player} folds")
                self.history.append((player, "F", 0))
            elif plr_action == "C" and "C" in options:
                if self.highest_bet == 0:
                    print(f"{player} checks")
                    self.history.append((player, "Ch", 0))
                else:
                    player.bankroll -= to_call
                    self.value += to_call
                    if to_call == self.highest_bet:
                        print(f"{player} calls ${to_call}")
                    else:
                        print(f"{player} calls for additional ${to_call}")
                    self.bets[player] = self.highest_bet
                    self.history.append((player, "C", self.highest_bet))
            elif plr_action == "R" and "R" in options:
                plr_raise = None
                while plr_raise == None:
                    amnt = input(f"Raise to? (Min: ${min_raise}, Max: All in ${max_raise})\n$")
                    if amnt.replace(".","").isnumeric():
                        amnt = float(amnt)
                        if min_raise <= amnt <= max_raise:
                            if amnt == max_raise:
                                print(f"{player} moves All In to ${amnt}")
                                self.history.append((player, "A", amnt))
                            else:
                                print(f"{player} raises to ${amnt}")
                                self.history.append((player, "R", amnt))
                            plr_raise = amnt
                            self.bets[player] = amnt
                            self.recent_raise = amnt - self.highest_bet
                            self.highest_bet = amnt
                        else:
                            print("Invalid Amount")
                    else:
                        print("Invalid Amount")
                player.bankroll -= (plr_raise - plr_bet)
                self.value += (plr_raise - plr_bet)
            elif plr_action == "B" and "B" in options:
                bet = None
                while bet == None:
                    amnt = input(f"Bet amount? (Min: ${min_raise}, Max: All in ${max_raise})\n$")
                    if amnt.replace(".","").isnumeric():
                        amnt = float(amnt)
                        if min_raise <= amnt <= max_raise:
                            if amnt == max_raise:
                                print(f"{player} moves All In to ${amnt}")
                                self.history.append((player, "A", amnt))
                            else:
                                print(f"{player} bets ${amnt}")
                                self.history.append((player, "B", amnt))
                            bet = amnt
                            self.recent_raise = amnt
                            self.bets[player] = amnt
                            self.highest_bet = amnt
                            if self.side_pots:
                                print("do sum")
                        else:
                            print("Invalid Amount")
                    else:
                        print("Invalid Amount")
                player.bankroll -= bet
                self.value += bet
            elif plr_action == "A" and "A" in options:
                amnt = plr.bankroll + plr_bet
                print(f"{player} moves All in to ${amnt}")
                if amnt >= min_raise:
                    self.recent_raise = amnt - self.highest_bet
                if amnt > self.highest_bet:
                    self.highest_bet = amnt
                self.history.append((player, "A", amnt))
                self.bets[player] = amnt
                player.bankroll = 0
                self.value += player.bankroll
                amnt_dist_value = amnt # variable to subtract from for each sidepot
                for sp in sorted(self.side_pots):
                    sp_bet_min = sp[0] # Amount of total all in needed to enter sidepot
                    sp_total_value = sp[1] # Total value of sidepot (winnings)
                    sp_bet_value = sp[2] # Amount of money needed per player in sidepot
                    sp_players = sp[3] # Players in sidepot
                    # Sidepot: (sp_bet_min, sp_total_value, sp_bet_value, players)
                    if player in sp_players:
                        continue
                    if amnt >= sp_bet_min:
                        sp_total_value += sp_bet_value
                        amnt_dist_value -= sp_bet_value
                        sp_players.append(player)
                        self.side_pots[self.side_pots.index(sp)] =(
                            sp_bet_min, sp_total_value, sp_bet_value, sp_players)
                    elif amnt_dist_value > 0:
                        # split sidepot into two new ones
                        amnt_dist_value = 0
                        new_sp_1 = (sp_bet_min, sp_total_value - (amnt_dist_value * len(sp_players)),
                                    sp_bet_value - amnt_dist_value, sp_players)
                        new_sp_2 = (amnt, amnt_dist_value * (len(sp_players) + 1), amnt_dist_value,
                                    sp_players.append(player))
                        self.side_pots[self.side_pots.index(sp)] = new_sp_1
                        self.side_pots.append(new_sp_2)
                if amnt_dist_value > 0:
                    self.side_pots.append((amnt, amnt_dist_value, amnt_dist_value, [player]))
            else:
                print("Invalid Action")
                self.action(player)


















class THoldem:
    def __init__(self, players=None, rules=None, bot_game=False):
        if rules is None:
            self.rules = default_rules
        else:
            self.rules = rules
        if players is None:
            self.get_players()
        else:
            self.players = players


    def get_players(self):
        self.players = []
        for i in range(self.rules["MAX_PLAYERS"]):
            player_name = input("Input first player name:\n")
            self.players.append(Player(name=player_name,bankroll=self.rules["DEFAULT_BANKROLL"]))
            if 1 <= i < (self.rules["MAX_PLAYERS"] - 1):
                if input("Add another player (y/n)?\n") == "y":
                    continue
                else:
                    break
            elif i >= (self.rules["MAX_PLAYERS"] - 1):
                break
        print("All players have joined")
        return

    def round(self, button_pos):
        deck = Deck()
        hands = {}
        bets = {}
        pot = 0
        for plr in self.players:
            hands[plr] = Hand(deck)
        board = Board(deck)
        button = self.players[button_pos]
        players_amount = len(self.players)
        if len(self.players) == 2:
            small_blind = button
            big_blind = self.players[(button_pos + 1) % players_amount]
            print(f"{button} is on the button, and is SB")
            print(f"{big_blind} is BB")
        else:
            small_blind = self.players[(button_pos + 1) % players_amount]
            big_blind = self.players[(button_pos + 2) % players_amount]
            print(f"{button} is on the button")
            print(f"{small_blind} is SB")
            print(f"{big_blind} is BB")
        if small_blind.ba
        small_blind.bankroll -= self.rules["SMALL_BLIND"]
        big_blind.bankroll -= self.rules["BIG_BLIND"]






THoldem()
