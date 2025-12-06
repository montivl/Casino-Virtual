# blackjack_multi.py
from typing import List, Tuple
from casino_virtual.fair_random import FairFunction

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

Card = Tuple[str, str]


def create_deck() -> List[Card]:
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def shuffle_deck(deck: List[Card], rng: FairFunction) -> None:
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
            value += 11
            aces += 1
        else:
            value += int(rank)

    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def format_hand(hand: List[Card]) -> str:
    return " ".join(f"{r}{s}" for r, s in hand)


class BlackjackPlayer:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.standing = False
        self.busted = False

    def add_card(self, card: Card):
        self.hand.append(card)
        if hand_value(self.hand) > 21:
            self.busted = True


class BlackjackGameMulti:
    """
    Blackjack multijugador de hasta 4 jugadores usando un mazo provably fair.
    """

    def __init__(self, rng: FairFunction, num_players: int):
        if not (1 <= num_players <= 4):
            raise ValueError("num_players debe estar entre 1 y 4.")

        self.rng = rng
        self.deck = create_deck()
        shuffle_deck(self.deck, self.rng)

        self.players = [BlackjackPlayer(f"Jugador {i+1}") for i in range(num_players)]
        self.dealer = BlackjackPlayer("Dealer")

        self.used_cards: List[Card] = []  # Para el log y verificación

    def deal_card(self) -> Card:
        if not self.deck:
            raise RuntimeError("El mazo se quedó sin cartas.")
        return self.deck.pop()

    def initial_deal(self):
        # Cada jugador recibe 2 cartas
        for player in self.players:
            c1 = self.deal_card()
            c2 = self.deal_card()
            player.add_card(c1)
            player.add_card(c2)
            self.used_cards.extend([c1, c2])

        # Dealer recibe 2 cartas
        d1 = self.deal_card()
        d2 = self.deal_card()
        self.dealer.add_card(d1)
        self.dealer.add_card(d2)
        self.used_cards.extend([d1, d2])

    def show_state(self, hide_dealer=True):
        print("\n--- Estado actual ---")
        for player in self.players:
            print(f"{player.name}: {format_hand(player.hand)} (valor={hand_value(player.hand)})")
        if hide_dealer:
            print(f"Dealer: {self.dealer.hand[0][0]}{self.dealer.hand[0][1]} ?? (segunda oculta)")
        else:
            print(f"Dealer: {format_hand(self.dealer.hand)} (valor={hand_value(self.dealer.hand)})")

    def player_turns(self):
        """
        Cada jugador juega en orden.
        """
        for player in self.players:
            while not player.standing and not player.busted:
                print(f"\nTurno de {player.name}")
                print(f"Mano actual: {format_hand(player.hand)} (valor={hand_value(player.hand)})")
                action = input("¿Pedir carta (h) o quedarse (s)? ").lower().strip()

                if action == "h":
                    card = self.deal_card()
                    player.add_card(card)
                    self.used_cards.append(card)
                    print(f"{player.name} recibe: {card[0]}{card[1]}")
                elif action == "s":
                    player.standing = True
                else:
                    print("Opción inválida")

                if player.busted:
                    print(f"{player.name} se pasó de 21.")

    def dealer_turn(self):
        """
        El dealer actúa solo después de todos los jugadores.
        """
        print("\nTurno del Dealer")
        while hand_value(self.dealer.hand) < 17:
            card = self.deal_card()
            self.dealer.add_card(card)
            self.used_cards.append(card)
            print(f"Dealer recibe: {card[0]}{card[1]}")

    def results(self) -> List[str]:
        """
        Retorna una lista de strings mostrando el resultado vs el dealer para cada jugador.
        """
        dealer_val = hand_value(self.dealer.hand)
        results = []

        for player in self.players:
            pv = hand_value(player.hand)

            if player.busted:
                results.append(f"{player.name} pierde (se pasó).")
            elif dealer_val > 21:
                results.append(f"{player.name} gana (dealer se pasó).")
            elif pv > dealer_val:
                results.append(f"{player.name} gana.")
            elif pv < dealer_val:
                results.append(f"{player.name} pierde.")
            else:
                results.append(f"{player.name} empata.")

        return results
