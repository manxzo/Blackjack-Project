import random
import copy

# Class for Cards
class Cards:
    """
    Represents a single playing card.
    Each card has a suit (e.g., Diamonds, Hearts), a rank (e.g., Ace, 2, 3), and a value (e.g., 10, [1, 11] for Ace).
    """
    def __init__(self, suit, rank, value):
        self.suit = suit      # The suit of the card (Diamonds, Spades, etc.)
        self.value = value    # The value of the card (e.g., 10 for a King, [1, 11] for an Ace)
        self.rank = rank      # The rank of the card (e.g., Ace, King, 2, 3, etc.)

    def __repr__(self):
        """
        Defines how the card is represented as a string.
        For example: "Ace of Spades (Value of [1, 11])"
        """
        return "{} of {} (Value of {})".format(self.rank, self.suit, self.value)

# Class for Deck
class Deck:
    """
    Represents a deck of cards. Manages operations like shuffling, dealing, and adding additional decks.
    """
    def __init__(self):
        """
        Initializes a deck of 52 cards (4 suits * 13 ranks per suit).
        Also keeps an original copy for resetting the deck if needed.
        """
        self.suits = ["Diamonds", "Spades", "Clubs", "Hearts"]  # List of all possible suits
        self.ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': [1, 11]}  # Rank to value mapping
        self.cards = self._create_deck()  # Generates the initial deck of cards
        self.original_cards = copy.deepcopy(self.cards)  # Saves a copy of the original deck for reset

    def _create_deck(self):
        """
        Creates a deck of 52 cards based on the ranks and suits.
        """
        return [Cards(suit, rank, value) for suit in self.suits for rank, value in self.ranks.items()]

    def shuffle(self):
        """
        Shuffles the deck using the random module.
        """
        random.shuffle(self.cards)

    def dealcards(self):
        """
        Deals one card from the deck (removes the card from the deck).
        Raises an error if the deck is empty.
        """
        if len(self.cards) == 0:
            raise ValueError("Deck is empty, cannot deal any more cards.")
        return self.cards.pop()

    def add_additional_deck(self):
        """
        Adds a new deck of 52 cards to the existing deck and shuffles it.
        """
        additional_cards = self._create_deck()
        self.cards.extend(additional_cards)  # Adds additional cards to the existing deck
        self.original_cards.extend(additional_cards)  # Updates the original card list
        print(f"Added an additional deck. Total cards now: {len(self.cards)}")
        self.shuffle()  # Shuffle the deck after adding new cards

    def __len__(self):
        """
        Returns the number of cards left in the deck.
        """
        return len(self.cards)

    def __repr__(self):
        """
        Represents the deck by showing how many cards are remaining.
        """
        return f"Cards Remaining in Deck: {len(self.cards)}"

# Class for Money
class Money:
    """
    Handles the player's money, including placing bets, winning or losing bets.
    """
    def __init__(self, balance):
        self.balance = balance  # The player's starting balance

    def bet_amount(self, amount):
        """
        Deducts the bet amount from the player's balance.
        Ensures the player has enough balance to place the bet.
        """
        if amount > self.balance:
            raise ValueError("Not enough balance to place this bet!")
        self.balance -= amount
        return amount

    def win_bet(self, amount):
        """
        Adds twice the bet amount to the player's balance when they win.
        """
        self.balance += amount * 2

    def lose_bet(self):
        """
        Does nothing when the player loses the bet, as the money is already deducted when the bet is placed.
        """
        pass

    def __repr__(self):
        """
        Shows the current balance of the player.
        """
        return f"Balance: ${self.balance}"

# Class for Player
class Player:
    """
    Represents a player in the game, either a regular player or the dealer.
    Handles actions such as placing bets, managing hand, and calculating total card values.
    """
    def __init__(self, name, is_dealer=False, balance=10000):
        self.name = name
        self.is_dealer = is_dealer  # Whether the player is the dealer or not
        self.money = Money(balance)  # Player's balance for betting
        self.hand = []  # Player's hand (list of cards)
        self.total = 0  # Total value of cards in hand
        self.current_bet = 0  # The current bet placed by the player
        self.insurance_bet = 0  # Insurance bet (if applicable)
        self.side_bets = {}  # Dictionary for storing side bets

    def add_card(self, card):
        """
        Adds a card to the player's hand and recalculates the total value of the hand.
        """
        self.hand.append(card)
        self.calculate_total()

    def calculate_total(self):
        """
        Calculates the total value of the player's hand.
        Properly handles the value of Aces (either 1 or 11 depending on the total).
        """
        total = 0
        aces = 0  # Count of Aces in the hand
        for card in self.hand:
            if isinstance(card.value, list):  # If the card is an Ace
                aces += 1
                total += 11  # Assume Ace is 11 at first
            else:
                total += card.value
        while total > 21 and aces > 0:
            total -= 10  # Convert an Ace from 11 to 1 if necessary
            aces -= 1
        self.total = total
        return self.total

    def show_hand(self):
        """
        Displays the player's hand and their total card value.
        If the player is the dealer, only the first card is shown until their turn.
        """
        if self.is_dealer:
            visible_hand = f"{self.hand[0]}" if len(self.hand) == 2 else ', '.join(str(card) for card in self.hand)
            print(f"Dealer's visible card: {visible_hand}")
        else:
            hand_str = ', '.join([str(card) for card in self.hand])
            print(f"{self.name}'s hand: {hand_str}. Total: {self.total}")

    def place_bet(self, amount):
        """
        Places a bet by deducting the amount from the player's balance.
        """
        self.current_bet = self.money.bet_amount(amount)

    def win_bet(self):
        """
        Player wins the bet and doubles their bet amount.
        """
        self.money.win_bet(self.current_bet)

    def lose_bet(self):
        """
        Player loses the bet, no money is refunded.
        """
        self.money.lose_bet()

class Game:
    """
    Main class that runs the Blackjack game.
    Handles player turns, dealer logic, and determining the winner.
    Now includes functionality for splitting, doubling down, and better input validation.
    """
    def __init__(self):
        self.deck = Deck()  # Initialize a single deck of cards
        self.players = []  # List of players
        self.dealer = Player("Dealer", is_dealer=True)  # The dealer as a player
        self.deck.shuffle()  # Shuffle the deck at the start of the game

    def add_players(self, num_players):
        """
        Adds the specified number of players to the game by asking for their names.
        """
        for i in range(num_players):
            name = input(f"Enter name for Player {i + 1}: ")
            player = Player(name, balance=10000)  # Each player starts with $10,000
            self.players.append(player)

    def check_deck_size(self):
        """
        Checks if the deck size is too small based on the number of players.
        If fewer cards are available than remaining_players * 2 + 15, a new deck is added.
        """
        remaining_players = len(self.players) + 1  # Including dealer
        if len(self.deck) < remaining_players * 2 + 15:
            print(f"Adding an additional deck due to low card count ({len(self.deck)} cards left)...")
            self.deck.add_additional_deck()

    def request_side_bets(self, player):
        """
        Prompts the player to place side bets and explains the rules and payout ratios.
        """
        print(f"\n{player.name}, you can place the following side bets:")

        # Dealer Bust Bet
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

        # Mixed Pair Bet
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

        # Same Pair Bet
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
        """
        Evaluates whether the player wins any side bets based on their hand and the dealer's hand.
        """
        card1, card2 = player.hand[:2]  # The player's first two cards

        # Dealer Bust Bet
        if player.side_bets.get('dealer_bust') and self.dealer.total > 21:
            print(f"{player.name} wins the 'Dealer Bust' side bet!")
            player.money.win_bet(player.side_bets['dealer_bust'] * 3)

        # Mixed Pair Bet
        if player.side_bets.get('mixed_pair') and card1.rank == card2.rank and card1.suit != card2.suit:
            print(f"{player.name} wins the 'Mixed Pair' side bet!")
            player.money.win_bet(player.side_bets['mixed_pair'] * 5)

        # Same Pair Bet
        if player.side_bets.get('same_pair') and card1.rank == card2.rank and card1.suit == card2.suit:
            print(f"{player.name} wins the 'Same Pair' side bet!")
            player.money.win_bet(player.side_bets['same_pair'] * 12)

    def start_round(self):
        """
        Starts a new round by dealing two cards to each player and the dealer.
        Also checks deck size before dealing.
        """
        self.check_deck_size()  # Check if deck needs to be expanded
        for player in self.players:
            player.add_card(self.deck.dealcards())
            player.add_card(self.deck.dealcards())
            player.show_hand()  # Show each player's hand
        self.dealer.add_card(self.deck.dealcards())
        self.dealer.add_card(self.deck.dealcards())
        self.dealer.show_hand()  # Show dealer's hand

    def player_turn(self, player):
        """
        Manages a player's turn where they can choose to hit, stand, double down, or split (if allowed).
        Returns False if the player busts (exceeds 21), otherwise True.
        """
        while True:
            action = input(f"{player.name}, do you want to [H]it, [S]tand, [D]ouble Down, or [SP]lit (if allowed)? ").lower()

            # Doubling down
            if action == 'd' and len(player.hand) == 2:
                # Player doubles the bet
                try:
                    player.place_bet(player.current_bet)  # Double the current bet
                    print(f"{player.name} doubles down!")
                    player.add_card(self.deck.dealcards())
                    player.show_hand()
                    return True  # Player automatically stands after doubling down
                except ValueError as e:
                    print(e)
                    continue  # If not enough balance, continue with the turn

            # Splitting hands
            elif action == 'sp' and len(player.hand) == 2 and player.hand[0].rank == player.hand[1].rank:
                print(f"{player.name} splits the hand!")
                self.split_hand(player)
                return True

            # Hit action
            elif action == 'h':
                player.add_card(self.deck.dealcards())
                player.show_hand()
                if player.total > 21:
                    print(f"{player.name} busted!")
                    return False  # Player has busted

            # Stand action
            elif action == 's':
                print(f"{player.name} stands with a total of {player.total}.")
                return True

            else:
                print("Invalid input, please choose [H]it, [S]tand, [D]ouble Down, or [SP]lit.")

    def split_hand(self, player):
        """
        Handles the logic for splitting a hand. The player splits their pair into two separate hands.
        """
        card1, card2 = player.hand
        split_hands = [[card1], [card2]]  # Two hands after splitting

        # Play each hand independently
        for i, hand in enumerate(split_hands, start=1):
            print(f"Playing hand {i} for {player.name}:")
            player.hand = hand  # Play with the current hand
            player.add_card(self.deck.dealcards())  # Deal a second card for each hand
            player.show_hand()

            # Player continues their turn with the current hand
            if not self.player_turn(player):
                print(f"Hand {i} busted for {player.name}.")

    def dealer_turn(self):
        """
        Manages the dealer's turn.
        Dealer will hit until their total is 17 or more, and then stand.
        """
        print("Dealer's turn...")
        self.dealer.show_hand()
        while self.dealer.total < 17:
            self.dealer.add_card(self.deck.dealcards())
            self.dealer.show_hand()

    def check_winner(self, player):
        """
        Checks who won between the player and the dealer after all turns are complete.
        Compares player total and dealer total to determine the result.
        """
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
            player.money.balance += player.current_bet  # Return bet in case of a tie

    def eliminate_players(self):
        """
        Eliminates players who are out of money from the game.
        """
        self.players = [player for player in self.players if player.money.balance > 0]
        if len(self.players) == 0:
            print("All players are out of money. Game over!")

    def play(self):
        """
        Main loop of the game. Handles multiple rounds and betting until all players are eliminated or choose to quit.
        """
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

                # Ask the player if they want to place side bets
                self.request_side_bets(player)

            self.start_round()

            for player in self.players:
                if not self.player_turn(player):
                    continue  # Move on if player busts

            self.dealer_turn()

            for player in self.players:
                self.check_winner(player)
                self.evaluate_side_bets(player)  # Evaluate side bets for the player

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



