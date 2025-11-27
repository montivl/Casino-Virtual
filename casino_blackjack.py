
import hashlib
import secrets
from typing import List, Tuple

class FairFunction:
    """
    f determinista basado en SHA-256.
    Genera una secuencia de bytes a partir de:
    server_seed, client_seed, nonce y un contador interno.
    El jugador puede reproducir esta secuencia y verificar el juego.
    """

    def __init__(self, server_seed: str, client_seed: str, nonce: int):
        self.server_seed = server_seed
        self.client_seed = client_seed
        self.nonce = nonce
        self.counter = 0
        self.buffer = b""
        self.index = 0

    def _refill(self) -> None:
        """
        Genera nuevos 32 bytes pseudoaleatorios y los concatena al buffer.
        """
        # state_input es totalmente público, o prefieres como con llave ública y priv? esto me lo sugirió el gepeto
        state_input = (
            f"{self.server_seed}|{self.client_seed}|{self.nonce}|{self.counter}"
        ).encode()
        digest = hashlib.sha256(state_input).digest()
        self.buffer += digest
        self.counter += 1

    def _next_bytes(self, n: int) -> bytes:
        """
        Devuelve n bytes pseudoaleatorios.
        """
        while len(self.buffer) - self.index < n:
            self._refill()
        out = self.buffer[self.index : self.index + n]
        self.index += n
        return out
    
    def randint(self, a: int, b: int) -> int:
        """
        Devuelve un entero uniforme entre a y b (incluidos) usando rejection sampling.
        """
        if a > b:
            raise ValueError("a debe ser <= b")

        range_size = b - a + 1
        # Usamos 4 bytes = 32 bits
        while True:
            chunk = self._next_bytes(4)
            value = int.from_bytes(chunk, "big")
            max_acceptable = (2 ** 32 // range_size) * range_size - 1
            if value <= max_acceptable:
                return a + (value % range_size)


# =========================
#  Cartas y Blackjack
# =========================

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

Card = Tuple[str, str]  # (rank, suit)


def create_deck() -> List[Card]:
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def shuffle_deck(deck: List[Card], rng: FairFunction) -> None:
    """
    Baraja el mazo in-place usando Fisher-Yates y el RNG provably fair.
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

    # Ajustar ases de 11 a 1 si nos pasamos de 21
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


def format_hand(hand: List[Card]) -> str:
    return " ".join(f"{r}{s}" for r, s in hand)


class BlackjackGame:
    def __init__(self, rng: FairFunction):
        self.rng = rng
        self.deck = create_deck()
        shuffle_deck(self.deck, self.rng)
        self.player_hand: List[Card] = []
        self.dealer_hand: List[Card] = []

    def deal_card(self) -> Card:
        if not self.deck:
            raise RuntimeError("El mazo se quedó sin cartas")
        return self.deck.pop()

    def initial_deal(self) -> None:
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

    def player_hit(self) -> None:
        self.player_hand.append(self.deal_card())

    def dealer_play(self) -> None:
        # El dealer pide carta hasta tener 17 o más
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())

    def result(self) -> str:
        player_val = hand_value(self.player_hand)
        dealer_val = hand_value(self.dealer_hand)

        if player_val > 21:
            return "Jugador se pasa. Dealer gana."
        if dealer_val > 21:
            return "Dealer se pasa. Jugador gana."
        if player_val > dealer_val:
            return "Jugador gana."
        elif player_val < dealer_val:
            return "Dealer gana."
        else:
            return "Empate."

    def show_state(self, hide_dealer_second_card: bool = True) -> None:
        print("\n--- Estado actual ---")
        print(f"Jugador: {format_hand(self.player_hand)} (valor = {hand_value(self.player_hand)})")
        if hide_dealer_second_card:
            if len(self.dealer_hand) >= 2:
                visible = [self.dealer_hand[0], ("??", "??")]
                print(f"Dealer:  {format_hand(visible)} (segunda carta oculta)")
            else:
                print(f"Dealer:  {format_hand(self.dealer_hand)}")
        else:
            print(f"Dealer:  {format_hand(self.dealer_hand)} (valor = {hand_value(self.dealer_hand)})")


# =========================
#  Funciones de compromiso
# =========================

def generate_server_seed() -> str:
    # 32 bytes aleatorios → 64 hex chars
    return secrets.token_hex(32)


def generate_client_seed() -> str:
    return secrets.token_hex(32)


def commitment(server_seed: str) -> str:
    return hashlib.sha256(server_seed.encode()).hexdigest()


# =========================
#  Flujo simple de una ronda
# =========================

def run_one_round() -> None:
    print("=== Casino Virtual Provably Fair: Blackjack (MVP) ===\n")

    # 1. Servidor genera semilla y compromiso
    server_seed = generate_server_seed()
    commit = commitment(server_seed)
    nonce = 0  # en un sistema real, este valor aumentaría por ronda

    print(f"[Servidor] Commit publicado al jugador (SHA-256 de server_seed):\n{commit}\n")

    # 2. Jugador define su semilla
    choice = input("¿Quieres ingresar tu propia client_seed? (s/n) [n]: ").strip().lower()
    if choice == "s":
        client_seed = input("Ingresa tu client_seed (cualquier string): ").strip()
        if not client_seed:
            print("Vacío, se generará una client_seed aleatoria.")
            client_seed = generate_client_seed()
    else:
        client_seed = generate_client_seed()

    print(f"[Jugador] client_seed usada:\n{client_seed}\n")

    # 3. Se crea el RNG provably fair y se juega blackjack
    rng = FairFunction(server_seed=server_seed, client_seed=client_seed, nonce=nonce)
    game = BlackjackGame(rng)
    game.initial_deal()
    game.show_state(hide_dealer_second_card=True)

    # Turno del jugador
    while True:
        if hand_value(game.player_hand) >= 21:
            break
        action = input("\n¿Pedir carta (h) o quedarse (s)? [h/s]: ").strip().lower()
        if action == "h":
            game.player_hit()
            game.show_state(hide_dealer_second_card=True)
        elif action == "s":
            break
        else:
            print("Opción inválida, escribe 'h' o 's'.")

    # Turno del dealer
    game.dealer_play()
    game.show_state(hide_dealer_second_card=False)

    print("\n>>> Resultado:", game.result())

    # 4. Servidor revela su semilla
    print("\n[Servidor] Revelando server_seed para verificación:")
    print(server_seed)
    print("\nCon esto puedes verificar tú mismo:")
    print("  1) Que SHA-256(server_seed) == commit mostrado al inicio.")
    print("  2) Que si recreas el RNG con (server_seed, client_seed, nonce)")
    print("     y barajas el mazo, obtienes el mismo orden de cartas.\n")
    print("Fin de la ronda.\n")


if __name__ == "__main__":
    run_one_round()
