import random
import copy

# Class for Cards
class Cards:
    """
    Represents a single playing card.
    Each card has a suit (e.g., Diamonds, Hearts), a rank (e.g., Ace, 2, 3), and a value (e.g., 10, [1, 11] for Ace).
    """
    def __init__(self, suit, rank, value):
        self.suit = suit
        self.value = value
        self.rank = rank

    def __repr__(self):
        """
        Defines how the card is represented as a string.
        For example: "Ace of Spades (Value of [1, 11])"
        """
        return "{} of {} (Value of {})".format(self.rank, self.suit, self.value)

    def get_card_display(self):
        """
        Returns the ASCII representation of the card.
        """
        suit_symbols = {"Diamonds": "♦", "Spades": "♠", "Clubs": "♣", "Hearts": "♥"}
        rank = self.rank if len(self.rank) == 2 else self.rank + " "
        suit = suit_symbols[self.suit]

        top = f"┌───────┐"
        mid_top = f"| {rank}    |"
        middle = f"|   {suit}   |"
        mid_bottom = f"|     {rank}|"
        bottom = f"└───────┘"
        return [top, mid_top, middle, mid_bottom, bottom]

# Class for Deck
class Deck:
    """
    Represents a deck of cards. Manages operations like shuffling, dealing, and adding additional decks.
    """
    def __init__(self):
        self.suits = ["Diamonds", "Spades", "Clubs", "Hearts"]
        self.ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': [1, 11]}
        self.cards = self._create_deck()
        self.original_cards = copy.deepcopy(self.cards)

    def _create_deck(self):
        """
        Creates a deck of 52 cards based on the ranks and suits.
        """
        return [Cards(suit, rank, value) for suit in self.suits for rank, value in self.ranks.items()]

    def shuffle(self):
        random.shuffle(self.cards)

    def dealcards(self):
        if len(self.cards) == 0:
            raise ValueError("Deck is empty, cannot deal any more cards.")
        return self.cards.pop()

    def add_additional_deck(self):
        additional_cards = self._create_deck()
        self.cards.extend(additional_cards)
        self.original_cards.extend(additional_cards)
        print(f"Added an additional deck. Total cards now: {len(self.cards)}")
        self.shuffle()

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Cards Remaining in Deck: {len(self.cards)}"

# Class for Money
class Money:
    """
    Handles the player's money, including placing bets, winning or losing bets.
    """
    def __init__(self, balance):
        self.balance = balance

    def bet_amount(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough balance to place this bet!")
        self.balance -= amount
        return amount

    def win_bet(self, amount):
        self.balance += amount * 2

    def lose_bet(self):
        pass

    def __repr__(self):
        return f"Balance: ${self.balance}"

# Class for Player
class Player:
    """
    Represents a player in the game, either a regular player or the dealer.
    Handles actions such as placing bets, managing hand, and calculating total card values.
    """
    def __init__(self, name, is_dealer=False, balance=10000):
        self.name = name
        self.is_dealer = is_dealer
        self.money = Money(balance)
        self.hand = []
        self.total = 0
        self.current_bet = 0
        self.insurance_bet = 0
        self.side_bets = {}
        self.split_hands = []  # To store split hands

    def add_card(self, card):
        self.hand.append(card)
        self.calculate_total()

    def calculate_total(self):
        total = 0
        aces = 0
        for card in self.hand:
            if isinstance(card.value, list):  # If the card is an Ace
                aces += 1
                total += 11
            else:
                total += card.value
        while total > 21 and aces > 0:
            total -= 10  # Convert an Ace from 11 to 1 if necessary
            aces -= 1
        self.total = total
        return self.total

    def show_hand(self, reveal_all=False):
        """
        Displays the player's hand as ASCII cards.
        If the player is the dealer and it's not their turn yet, only show the first card.
        """
        if self.is_dealer and not reveal_all:
            first_card = self.hand[0].get_card_display()
            hidden_card = [
                "┌───────┐",
                "| ***** |",
                "| ***** |",
                "| ***** |",
                "└───────┘"
            ]
            hand_lines = [first_card, hidden_card]
        else:
            hand_lines = [card.get_card_display() for card in self.hand]

        for row in zip(*hand_lines):
            print('  '.join(row))
        if not self.is_dealer or reveal_all:
            print(f"{self.name}'s total: {self.total}")

    def place_bet(self, amount):
        self.current_bet = self.money.bet_amount(amount)

    def win_bet(self):
        self.money.win_bet(self.current_bet)

    def lose_bet(self):
        self.money.lose_bet()

# Class for the Game
class Game:
    """
    Main class that runs the Blackjack game.
    Handles player turns, dealer logic, determining the winner, side bets, splitting, doubling down, and insurance.
    """
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.dealer = Player("Dealer", is_dealer=True)
        self.deck.shuffle()

    def add_players(self, num_players):
        for i in range(num_players):
            name = input(f"Enter name for Player {i + 1}: ")
            player = Player(name, balance=10000)
            self.players.append(player)

    def check_deck_size(self):
        remaining_players = len(self.players) + 1
        if len(self.deck) < remaining_players * 2 + 15:
            print(f"Adding an additional deck due to low card count ({len(self.deck)} cards left)...")
            self.deck.add_additional_deck()

    def offer_insurance(self):
        if self.dealer.hand[0].rank == "Ace":
            print("Dealer shows an Ace! Offering insurance.")
            for player in self.players:
                while True:
                    insurance = input(f"{player.name}, do you want insurance? (Y/N): ").lower()
                    if insurance in ['y', 'n']:
                        break
                    print("Invalid input, please enter Y or N.")
                if insurance == 'y':
                    insurance_bet = min(player.current_bet // 2, player.money.balance)
                    print(f"{player.name} places an insurance bet of ${insurance_bet}.")
                    player.money.bet_amount(insurance_bet)
                    player.insurance_bet = insurance_bet
                else:
                    player.insurance_bet = 0

    def check_insurance(self):
        if self.dealer.total == 21:
            print("Dealer has Blackjack!")
            for player in self.players:
                if player.insurance_bet > 0:
                    print(f"{player.name} wins the insurance bet.")
                    player.money.win_bet(player.insurance_bet // 2)
        else:
            print("Dealer does not have Blackjack.")
            for player in self.players:
                if player.insurance_bet > 0:
                    print(f"{player.name} loses the insurance bet.")

    def request_side_bets(self, player):
        print(f"\n{player.name}, you can place the following side bets:")

        if input("Do you want to place a 'Dealer Bust' bet? (3:1 payout) (Y/N): ").lower() == 'y':
            while True:
                try:
                    amount = int(input("Enter the amount to bet on Dealer Bust: "))
                    player.money.bet_amount(amount)
                    player.side_bets['dealer_bust'] = amount
                    print(f"{player.name} placed a Dealer Bust bet of ${amount}.")
                    break
                except ValueError as e:
                    print(e)
        else:
            player.side_bets['dealer_bust'] = 0

        if input("Do you want to place a 'Mixed Pair' bet? (5:1 payout) (Y/N): ").lower() == 'y':
            while True:
                try:
                    amount = int(input("Enter the amount to bet on Mixed Pair: "))
                    player.money.bet_amount(amount)
                    player.side_bets['mixed_pair'] = amount
                    print(f"{player.name} placed a Mixed Pair bet of ${amount}.")
                    break
                except ValueError as e:
                    print(e)
        else:
            player.side_bets['mixed_pair'] = 0

        if input("Do you want to place a 'Same Pair' bet? (12:1 payout) (Y/N): ").lower() == 'y':
            while True:
                try:
                    amount = int(input("Enter the amount to bet on Same Pair: "))
                    player.money.bet_amount(amount)
                    player.side_bets['same_pair'] = amount
                    print(f"{player.name} placed a Same Pair bet of ${amount}.")
                    break
                except ValueError as e:
                    print(e)
        else:
            player.side_bets['same_pair'] = 0

    def evaluate_side_bets(self, player):
        card1, card2 = player.hand[:2]

        if player.side_bets.get('dealer_bust') and self.dealer.total > 21:
            print(f"{player.name} wins the 'Dealer Bust' side bet!")
            player.money.win_bet(player.side_bets['dealer_bust'] * 3)

        if player.side_bets.get('mixed_pair') and card1.rank == card2.rank and card1.suit != card2.suit:
            print(f"{player.name} wins the 'Mixed Pair' side bet!")
            player.money.win_bet(player.side_bets['mixed_pair'] * 5)

        if player.side_bets.get('same_pair') and card1.rank == card2.rank and card1.suit == card2.suit:
            print(f"{player.name} wins the 'Same Pair' side bet!")
            player.money.win_bet(player.side_bets['same_pair'] * 12)

    def start_round(self):
        self.check_deck_size()
        for player in self.players:
            player.add_card(self.deck.dealcards())
            player.add_card(self.deck.dealcards())
            player.show_hand()
        self.dealer.add_card(self.deck.dealcards())
        self.dealer.add_card(self.deck.dealcards())
        self.dealer.show_hand()

        self.offer_insurance()

    def player_turn(self, player):
        while True:
            action = input(f"{player.name}, do you want to [H]it, [S]tand, [D]ouble Down, or [SP]lit (if allowed)? ").lower()

            if action not in ['h', 's', 'd', 'sp']:
                print("Invalid input. Please enter [H], [S], [D], or [SP].")
                continue

            if action == 'd' and len(player.hand) == 2:
                try:
                    player.place_bet(player.current_bet)
                    print(f"{player.name} doubles down!")
                    player.add_card(self.deck.dealcards())
                    player.show_hand()
                    return True
                except ValueError as e:
                    print(e)
                    continue

            elif action == 'sp' and len(player.hand) == 2 and player.hand[0].rank == player.hand[1].rank:
                print(f"{player.name} splits the hand!")
                self.split_hand(player)
                return True

            elif action == 'h':
                player.add_card(self.deck.dealcards())
                player.show_hand()
                if player.total > 21:
                    print(f"{player.name} busted!")
                    return False

            elif action == 's':
                print(f"{player.name} stands with a total of {player.total}.")
                return True

    def split_hand(self, player):
        card1, card2 = player.hand
        split_hands = [[card1], [card2]]

        for i, hand in enumerate(split_hands, start=1):
            print(f"Playing hand {i} for {player.name}:")
            player.hand = hand
            player.add_card(self.deck.dealcards())
            player.show_hand()

            if not self.player_turn(player):
                print(f"Hand {i} busted for {player.name}.")

    def dealer_turn(self):
        print("Dealer's turn...")
        self.dealer.show_hand(reveal_all=True)
        while self.dealer.total < 17:
            self.dealer.add_card(self.deck.dealcards())
            self.dealer.show_hand(reveal_all=True)

        self.check_insurance()

    def check_winner(self, player):
        if player.total > 21:
            print(f"{player.name} busted. Dealer wins!")
            player.lose_bet()
        elif self.dealer.total > 21 or player.total > self.dealer.total:
            print(f"{player.name} wins against the dealer!")
            player.win_bet()
        elif player.total < self.dealer.total:
            print(f"Dealer wins against {player.name}.")
            player.lose_bet()
        else:
            print(f"{player.name} ties with the dealer. Bet returned.")
            player.money.balance += player.current_bet

    def eliminate_players(self):
        self.players = [player for player in self.players if player.money.balance > 0]
        if len(self.players) == 0:
            print("All players are out of money. Game over!")

    def play(self):
        num_players = int(input("How many players are playing? "))
        self.add_players(num_players)

        while any(player.money.balance > 0 for player in self.players):
            self.eliminate_players()

            for player in self.players:
                print(f"{player.name}, your current balance: ${player.money.balance}")
                while True:
                    try:
                        bet_amount = int(input(f"{player.name}, how much would you like to bet? "))
                        player.place_bet(bet_amount)
                        break
                    except ValueError as e:
                        print(e)

                self.request_side_bets(player)

            self.start_round()

            for player in self.players:
                if not self.player_turn(player):
                    continue

            self.dealer_turn()

            for player in self.players:
                self.check_winner(player)
                self.evaluate_side_bets(player)

            if input("Do you want to play another round? [Y/N] ").lower() != 'y':
                print("Thanks for playing!")
                break

        self.eliminate_players()
        if len(self.players) == 0:
            print("All players are out of money. Game over!")

# Start the game
if __name__ == "__main__":
    game = Game()
    game.play()
