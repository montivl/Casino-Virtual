import json
import os
from datetime import datetime

from casino_virtual.fair_random import FairFunction
from casino_virtual.blackjack import BlackjackGame, hand_value
from casino_virtual.blackjack_multi import BlackjackGameMulti
from casino_virtual.seeds import generate_server_seed, generate_client_seed, load_nonce, save_nonce
from casino_virtual.commitments import commitment
from casino_virtual.mac_utils import load_or_create_mac_key, compute_mac 


LOG_PATH = "logs/last_round.json"


def save_round_log(data: dict):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=4)


def run_round() -> None:
    print("=== Casino Virtual Provably Fair ===\n")

    nonce = load_nonce()
    print(f"[Sistema] Nonce actual: {nonce}")

    server_seed = generate_server_seed()
    commit = commitment(server_seed)

    print(f"[Servidor] Commit publicado (SHA-256 de server_seed):\n{commit}\n")

    # Pedir client_seed
    choice = input("¿Quieres ingresar tu propia client_seed? (s/n) [n]: ").strip().lower()

    if choice == "s":
        client_seed = input("Ingresa tu client_seed (string): ").strip()
        if not client_seed:
            client_seed = generate_client_seed()
    else:
        client_seed = generate_client_seed()

    print(f"[Jugador] client_seed usada:\n{client_seed}\n")

    # =========================
    # MAC sobre client_seed
    # =========================
    mac_key = load_or_create_mac_key()
    mac_message = f"{client_seed}:{nonce}"
    client_seed_mac = compute_mac(mac_message, mac_key)

    rng = FairFunction(server_seed, client_seed, nonce)

    print("\n=== Selección de modo de juego ===")
    print("1) Blackjack Individual (1 jugador)")
    print("2) Blackjack Multijugador (hasta 4 jugadores)")

    while True:
        mode = input("Elige modo (1 o 2): ").strip()
        if mode in ["1", "2"]:
            break
        print("Opción inválida. Elige 1 o 2.")

    # ======================================================
    # MODO INDIVIDUAL
    # ======================================================
    if mode == "1":
        print("\nModo seleccionado: Blackjack Individual")
        game = BlackjackGame(rng)
        game.initial_deal()
        game.show_state(hide_dealer_second_card=True)

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
                print("Opción inválida.")

        game.dealer_play()
        game.show_state(hide_dealer_second_card=False)

        used_cards = game.used_cards
        result_data = game.result()

    # ======================================================
    # MODO MULTIJUGADOR
    # ======================================================
    else:
        print("\nModo seleccionado: Blackjack Multijugador")

        while True:
            try:
                num_players = int(input("¿Cuántos jugadores jugarán? (1–4): "))
                if 1 <= num_players <= 4:
                    break
                print("Número inválido.")
            except:
                print("Ingresa un número válido.")

        game = BlackjackGameMulti(rng, num_players)
        game.initial_deal()
        game.show_state(hide_dealer=True)

        game.player_turns()
        game.dealer_turn()
        game.show_state(hide_dealer=False)

        used_cards = game.used_cards
        result_data = game.results()

    # ======================================================
    # ÚNICA impresión final del resultado
    # ======================================================
    print("\n=== Resultados finales ===")
    if mode == "1":
        print(result_data)
    else:
        for r in result_data:
            print(" -", r)

    # ======================================================
    # Revelar seed del servidor
    # ======================================================
    print("\n[Servidor] Revelando server_seed para verificación:")
    print(server_seed)
    print("\nVerifica tú mismo o usa verify.py.")

    # ======================================================
    # Guardar log
    # ======================================================
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "server_seed": server_seed,
        "client_seed": client_seed,
        "client_seed_mac": client_seed_mac.hex(),    
        "mac_message": mac_message,
        "commit": commit,
        "nonce": nonce,
        "used_cards": used_cards,
        "result": result_data,
    }


    save_round_log(log_data)

    # Incrementar nonce
    nonce += 1
    save_nonce(nonce)
