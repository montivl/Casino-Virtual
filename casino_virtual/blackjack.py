from typing import List, Tuple
from casino_virtual.fair_random import FairFunction

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

Card = Tuple[str, str]


def create_deck() -> List[Card]:
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def shuffle_deck(deck: List[Card], rng: FairFunction) -> None:
    """
    Baraja el mazo usando Fisher-Yates + FairFunction.
    """
    n = len(deck)
    for i in range(n - 1, 0, -1):
        j = rng.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]


def hand_value(hand: List[Card]) -> int:
    value = 0
    aces = 0
    for rank, _ in hand:
        if rank in ["J", "Q", "K"]:
            value += 10
        elif rank == "A":
            aces += 1
            value += 11
        else:
            value += int(rank)

    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def format_hand(hand: List[Card]) -> str:
    return " ".join(f"{r}{s}" for r, s in hand)


class BlackjackGame:
    """
    Representa una ronda de Blackjack usando un mazo provably fair.
    """
    def __init__(self, rng: FairFunction):
        self.rng = rng
        self.deck = create_deck()
        shuffle_deck(self.deck, self.rng)
        self.player_hand: List[Card] = []
        self.dealer_hand: List[Card] = []
        self.used_cards: List[Card] = []

    def deal_card(self) -> Card:
        if not self.deck:
            raise RuntimeError("El mazo se quedó sin cartas.")
        card = self.deck.pop()
        self.used_cards.append(card) 
        return card


    def initial_deal(self) -> None:
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

    def player_hit(self) -> None:
        self.player_hand.append(self.deal_card())

    def dealer_play(self) -> None:
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())

    def result(self) -> str:
        pv = hand_value(self.player_hand)
        dv = hand_value(self.dealer_hand)

        if pv > 21:
            return "Jugador se pasa. Dealer gana."
        if dv > 21:
            return "Dealer se pasa. Jugador gana."
        if pv > dv:
            return "Jugador gana."
        if pv < dv:
            return "Dealer gana."
        return "Empate."

    def show_state(self, hide_dealer_second_card: bool = True):
        print("\n--- Estado actual ---")
        print(f"Jugador: {format_hand(self.player_hand)} (valor = {hand_value(self.player_hand)})")

        if hide_dealer_second_card:
            # Sólo mostrar la primera carta del dealer
            if len(self.dealer_hand) >= 2:
                visible = [self.dealer_hand[0], ("??", "??")]
                print(f"Dealer:  {format_hand(visible)} (segunda carta oculta)")
            else:
                print(f"Dealer:  {format_hand(self.dealer_hand)}")
        else:
            print(f"Dealer:  {format_hand(self.dealer_hand)} (valor = {hand_value(self.dealer_hand)})")
