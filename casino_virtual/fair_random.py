import hashlib
from typing import Optional


class FairFunction:
    """
    Función provably fair basada en SHA-256.

    Genera una secuencia pseudoaleatoria a partir de:
        server_seed, client_seed, nonce y un contador interno.

    El jugador puede reconstruir esta secuencia y verificar el juego.
    No depende de símbolos de separación, solo concatenación de bytes.

    rejection sampling:
        Para generar un número en [a, b], generamos un entero uniforme
        de 32 bits. Si ese entero cae fuera del rango "aceptable" que
        permite mapearlo sin sesgo al rango deseado, se descarta (reject).
        Esto evita sesgos de distribución.
    """

    def __init__(self, server_seed: str, client_seed: str, nonce: int):
        self.server_seed = server_seed.encode()
        self.client_seed = client_seed.encode()
        self.nonce = str(nonce).encode()
        self.counter = 0

        # buffer interno con bytes pseudoaleatorios
        self.buffer = b""
        self.index = 0

    def _refill(self) -> None:
        """
        Genera 32 bytes nuevos concatenando:
        server_seed || client_seed || nonce || counter

        Todo es público después de la ronda, así que no hay secretos aquí.
        """
        state = (
            self.server_seed +
            self.client_seed +
            self.nonce +
            str(self.counter).encode()
        )
        digest = hashlib.sha256(state).digest()
        self.buffer += digest
        self.counter += 1

    def _next_bytes(self, n: int) -> bytes:
        """
        Entrega n bytes pseudoaleatorios desde el buffer interno.
        Lo rellena cuando sea necesario.
        """
        while len(self.buffer) - self.index < n:
            self._refill()

        out = self.buffer[self.index:self.index + n]
        self.index += n
        return out

    def randint(self, a: int, b: int) -> int:
        """
        Devuelve un entero uniforme en [a, b] usando rejection sampling.
        """
        if a > b:
            raise ValueError("a debe ser <= b")

        range_size = b - a + 1

        # 4 bytes -> 32 bits
        while True:
            chunk = self._next_bytes(4)
            value = int.from_bytes(chunk, "big")

            max_acceptable = (2**32 // range_size) * range_size - 1
            if value <= max_acceptable:
                return a + (value % range_size)
