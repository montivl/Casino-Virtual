import unittest
from collections import Counter
from casino_virtual.fair_random import FairFunction
from casino_virtual.mac_utils import compute_mac, verify_mac

class TestCasinoCrypto(unittest.TestCase):
    
    def test_rng_determinism(self):
        """Mismas seeds deben dar mismos números."""
        rng1 = FairFunction("server", "client", 1)
        rng2 = FairFunction("server", "client", 1)
        self.assertEqual(rng1.randint(0, 100), rng2.randint(0, 100))

    def test_rng_avalanche(self):
        """Cambio mínimo en seed debe cambiar totalmente el resultado."""
        rng1 = FairFunction("server1", "client", 1)
        rng2 = FairFunction("server2", "client", 1)
        self.assertNotEqual(rng1.randint(0, 100000), rng2.randint(0, 100000))

    def test_mac_integrity(self):
        """HMAC debe fallar si el mensaje cambia."""
        key = b"secret_key"
        msg = "data"
        tag = compute_mac(msg, key)
        self.assertTrue(verify_mac(msg, key, tag))
        self.assertFalse(verify_mac("data_modified", key, tag))

    def test_distribution(self):
        """Test estadístico básico (no riguroso, solo sanity check)."""
        rng = FairFunction("s", "c", 1)
        # Generar 1000 números entre 0 y 9
        counts = Counter(rng.randint(0, 9) for _ in range(1000))
        # Esperamos ~100 por cada número. Si alguno tiene < 50 o > 150, algo anda mal.
        for x in range(10):
            self.assertTrue(50 < counts[x] < 150, f"Sesgo detectado en {x}: {counts[x]}")

if __name__ == '__main__':
    unittest.main()