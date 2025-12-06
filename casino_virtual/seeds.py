import secrets


def generate_server_seed() -> str:
    return secrets.token_hex(32)


def generate_client_seed() -> str:
    return secrets.token_hex(32)


def load_nonce(path: str = "nonce.txt") -> int:
    """
    Carga nonce desde archivo. Si no existe, parte en 0.
    """
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0


def save_nonce(nonce: int, path: str = "nonce.txt") -> None:
    with open(path, "w") as f:
        f.write(str(nonce))
