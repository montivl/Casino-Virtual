import json
import hashlib

from casino_virtual.fair_random import FairFunction
from casino_virtual.blackjack import create_deck, shuffle_deck
from casino_virtual.mac_utils import load_or_create_mac_key, verify_mac


LOG_PATH = "logs/last_round.json"


def verify_commit(server_seed: str, commit: str) -> bool:
    return hashlib.sha256(server_seed.encode()).hexdigest() == commit


def verify_round():
    print("=== Verificación de última ronda ===\n")

    # 1. Cargar log
    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No hay rondas registradas para verificar.")
        return

    server_seed = data["server_seed"]
    client_seed = data["client_seed"]
    client_seed_mac_hex = data.get("client_seed_mac")
    mac_message = data.get("mac_message", f"{client_seed}:{data['nonce']}")
    commit = data["commit"]
    nonce = data["nonce"]

    # Convertir ["A","♠"] → ("A","♠")
    real_cards = [tuple(card) for card in data["used_cards"]]

    print("Datos cargados correctamente.\n")

    # 2. Verificar MAC sobre client_seed
    print("Verificando MAC de client_seed...")
    mac_key = load_or_create_mac_key()

    if client_seed_mac_hex is None:
        print(" No hay MAC almacenado para client_seed (ronda antigua o log corrupto).")
    else:
        mac_bytes = bytes.fromhex(client_seed_mac_hex)

        if verify_mac(mac_message, mac_key, mac_bytes):
            print(" MAC válido: la client_seed no fue modificada.")
        else:
            print(" MAC inválido: la client_seed fue modificada o el log fue alterado.")
            return

    # 3. Verificar commit
    print("\nVerificando commit...")
    if verify_commit(server_seed, commit):
        print("Commit válido.")
    else:
        print("ALERTA: Commit inválido — el servidor cambió su server_seed.")
        return

    # 4. Reproducir mazo
    print("\nReconstruyendo mazo...")
    rng = FairFunction(server_seed, client_seed, nonce)
    deck = create_deck()
    shuffle_deck(deck, rng)

    # pop() entrega al revés — simulamos el orden real
    regenerated_cards = deck[::-1][:len(real_cards)]

    # 5. Comparar secuencias
    print("Comparando cartas entregadas...")
    if regenerated_cards == real_cards:
        print("\n >>> VERIFICACIÓN EXITOSA: El servidor no hizo trampa.\n")
    else:
        print("\n >>> ALERTA: Las cartas no coinciden — posible manipulación.\n")
        for i, (a, b) in enumerate(zip(real_cards, regenerated_cards)):
            if a != b:
                print(f"Diferencia en carta {i+1}: real={a}, regenerada={b}")
                break

    # 6. Mostrar resultados guardados
    print("\nResultado registrado en el log:")
    print(data.get("result"))


if __name__ == "__main__":
    verify_round()
