# attack_report.py
"""
Script demostrativo: ejecuta ataques y explica su detección.
Para usar en el informe o demo del proyecto.
"""

from casino_virtual.mac_utils import compute_mac, verify_mac
from verify import verify_commit
from casino_virtual.fair_random import FairFunction
from casino_virtual.blackjack import create_deck, shuffle_deck
import hashlib


def demo_modify_client_seed():
    print("\n=== DEMO ATAQUE: Modificar client_seed ===")

    key = b"X" * 32
    original = "AAAA:0"
    manipulated = "BBBB:0"

    print(f"client_seed original: {original}")
    print(f"client_seed manipulada: {manipulated}")

    mac = compute_mac(original, key)

    print(f"MAC válido: {mac.hex()}")
    print("Verificando client_seed manipulada...")

    ok = verify_mac(manipulated, key, mac)
    print("Resultado:", ok)


def demo_modify_server_seed():
    print("\n=== DEMO ATAQUE: Cambiar server_seed después del commit ===")

    real = "abc"
    fake = "zzz"

    commit = hashlib.sha256(real.encode()).hexdigest()

    print(f"Commit publicado: {commit}")
    print(f"Seed real: {real}")
    print(f"Seed falsa: {fake}")

    print("Verificación real:", verify_commit(real, commit))
    print("Verificación falsa:", verify_commit(fake, commit))


def demo_manipulate_cards():
    print("\n=== DEMO ATAQUE: Alterar cartas repartidas ===")

    rng = FairFunction("s", "c", 0)
    deck = create_deck()
    shuffle_deck(deck, rng)

    real = deck[::-1][:5]
    tampered = real.copy()
    tampered[3] = ("Q", "♣")

    print("Secuencia real:", real)
    print("Secuencia alterada:", tampered)
    print("Coinciden?:", real == tampered)


if __name__ == "__main__":
    demo_modify_client_seed()
    demo_modify_server_seed()
    demo_manipulate_cards()
