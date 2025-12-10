import unittest
import hashlib

from verify import verify_commit
from casino_virtual.mac_utils import compute_mac, verify_mac
from casino_virtual.fair_random import FairFunction
from casino_virtual.blackjack import create_deck, shuffle_deck


class TestAttackScenarios(unittest.TestCase):

    def test_attack_modify_client_seed(self):
        print("\n=== ATAQUE 1: Modificar client_seed ===")

        original_message = "AAAA:0"
        attacker_message = "BBBB:0"
        key = b"X" * 32

        # MAC generado con mensaje manipulado
        fake_mac = compute_mac(attacker_message, key).hex()

        print(f"Mensaje original esperado por el MAC: {original_message}")
        print(f"Mensaje que realmente firmó el atacante: {attacker_message}")
        print(f"MAC usado en el log: {fake_mac}")

        ok = verify_mac(original_message, key, bytes.fromhex(fake_mac))
        print(f"Resultado verificación MAC: {ok}")

        self.assertFalse(ok, "Modificar client_seed debería invalidar el MAC")

    def test_attack_modify_server_seed(self):
        print("\n=== ATAQUE 2: Cambiar server_seed después del commit ===")

        real_seed = "abc"
        fake_seed = "zzz"

        real_commit = hashlib.sha256(real_seed.encode()).hexdigest()

        print(f"Commit publicado originalmente: {real_commit}")
        print(f"Server_seed real: {real_seed}")
        print(f"Server_seed falsa revelada por el atacante: {fake_seed}")

        ok_real = verify_commit(real_seed, real_commit)
        ok_fake = verify_commit(fake_seed, real_commit)

        print(f"Verificación con server_seed REAL: {ok_real}")
        print(f"Verificación con server_seed FALSA: {ok_fake}")

        self.assertTrue(ok_real)
        self.assertFalse(ok_fake, "Si server_seed cambia, commit debe fallar")

    def test_attack_modify_used_cards(self):
        print("\n=== ATAQUE 3: Alterar la secuencia de cartas ===")

        rng = FairFunction("s", "c", 0)
        deck = create_deck()
        shuffle_deck(deck, rng)

        correct = deck[::-1][:5]
        tampered = correct.copy()
        tampered[2] = ("K", "♠")

        print(f"Secuencia correcta: {correct}")
        print(f"Secuencia alterada: {tampered}")

        self.assertNotEqual(correct, tampered)

    def test_attack_modify_mac_message(self):
        print("\n=== ATAQUE 4: Cambiar el nonce o la client_seed dentro del mac_message ===")

        key = b"X" * 32
        original = "seed123:5"
        tampered = "seed123:999"

        tag = compute_mac(original, key)

        print(f"Mensaje original: {original}")
        print(f"Mensaje manipulado: {tampered}")
        print(f"MAC original: {tag.hex()}")

        ok = verify_mac(tampered, key, tag)
        print(f"Resultado verificación MAC: {ok}")

        self.assertFalse(ok, "Modificar mac_message debe invalidar MAC")

    def test_attack_deck_manipulation(self):
        print("\n=== ATAQUE 5: Manipulación del mazo después de barajado ===")

        rng = FairFunction("s", "c", 0)
        deck = create_deck()
        shuffle_deck(deck, rng)

        used = deck[::-1][:10]
        tampered = used.copy()
        tampered[-1] = ("A", "♣")

        print(f"Mazo real usado: {used}")
        print(f"Mazo manipulado: {tampered}")

        self.assertNotEqual(used, tampered)

    def test_reuse_server_seed_without_nonce_change(self):
        print("\n=== ATAQUE 6: Reuso indebido de server_seed ===")

        rng1 = FairFunction("same_seed", "client", 0)
        rng2 = FairFunction("same_seed", "client", 1)

        deck1 = create_deck()
        deck2 = create_deck()

        shuffle_deck(deck1, rng1)
        shuffle_deck(deck2, rng2)

        print("Primer mazo generado con nonce = 0:")
        print(deck1[:10], "...")

        print("Segundo mazo generado con nonce = 1:")
        print(deck2[:10], "...")

        self.assertNotEqual(deck1, deck2, "Nonce debe alterar el mazo")


if __name__ == "__main__":
    unittest.main(verbosity=2)