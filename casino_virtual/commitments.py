import hashlib


def commitment(server_seed: str) -> str:
    """
    Devuelve SHA-256(server_seed).
    Propiedades:
        - hiding (no revela la seed)
        - binding (no permite cambiarla después)
    """
    return hashlib.sha256(server_seed.encode()).hexdigest()
