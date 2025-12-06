# Casino-Virtual

Básicamente un casino donde el servidor no puede hacerle la desconocida al jugador, y todo queda verificable criptográficamente.  
La idea es que el jugador pueda decir "demuéstrame que no me estái cagando", y nuestro super casino responda "EVIDENCIA".

---

## Idea general del proyecto

Queremos un casino donde:
- Los juegos tienen resultados que se pueden verificar después.
- El servidor no puede cambiar la aleatoriedad una vez que mostró el commit.
- El jugador tampoco puede hacerse el vivo y mandar seeds falsas.
- Todo el proceso (ronda completa) queda fijado por dos seeds: la del servidor y la del jugador, más un `nonce` que aumenta en cada ronda (ya implementado).

Flujo básico:
1. El casino muestra un commit sobre su seed.  
2. El jugador manda su client_seed.  
3. El juego corre usando una función provably fair determinista.  
4. El casino revela su server_seed.  
5. El jugador verifica que no hubo mano negra.

---

## Consideraciones nuevas según feedback

### 1. Qué pasa si el servidor "cambia" la client_seed que envió el jugador?
~~Nuestro sistema como estaba no lo protegía explícitamente.~~  
Ahora SÍ:

- Se implementó HMAC-SHA256 para autenticar la client_seed.
- Se guarda silenciosamente la client_seed y su MAC en el log.
- `verify.py` revisa que el MAC coincida, confirmando que nada fue alterado.

### 2. Por qué SHA-256?
Nos da un compromiso con:
- **Hiding** (seed del servidor queda oculta)
- **Binding** (el servidor no puede cambiarla después)

Implementado en `commitments.py`.

### 3. Libertades del casino en blackjack
- El dealer sigue una regla fija (pedir bajo 17).
- Dado el mazo generado, no puede tomar decisiones estratégicas.
- Perfecto para provably fair: ya está implementado.

### 4. Múltiples jugadores usando el mismo mazo
Aún no implementado.  
Tarea futura: ver cómo repartir cartas sin favorecer a nadie.

### 5. Nonce ahora sí aumenta
Antes era fijo.  
~~Pendiente~~ → **YA IMPLEMENTADO** en `seeds.py` y `casino_round.py`.

### 6. Llaves públicas/privadas
Aún no necesarias.  
El MAC simétrico cubre la integridad entre cliente y servidor en este proyecto.

### 7. Debemos crear verify.py
~~Pendiente.~~  
→ **YA IMPLEMENTADO** con commit check, MAC check y reconstrucción de baraja.

### 8. Explicar Rejection Sampling
El RNG basado en SHA256 usa rejection sampling para obtener enteros uniformes.  
Explicado en el informe y aplicado en `fair_random.py`.

### 9. Revisar otras formas de Provably Fair
Pendiente revisar:
- VRFs  
- Randomness beacons  
- Smart contracts  
(Solo análisis, no implementación aún.)

---

## Cosas que se pueden implementar (lista pa ir tachando)

### Parte criptográfica (la volá seria)
- ~~Módulo RNG provably fair con SHA-256~~ ✔
- ~~MAC para proteger client_seed~~ ✔
- Explicar formalmente *hiding / binding*  
- Documentar ataque del servidor / jugador / MITM  
- Extender a AEAD (confidencialidad + integridad)  
- Estudiar VRF, beacons, smart contracts

### Parte del juego
- Mejorar Blackjack:
  - Doble
  - Dividir pares
  - Seguro del dealer
- Nuevos juegos:
  - Ruleta (fácil)
  - Dados (simple)
  - Poker (difícil por decisiones estratégicas)

### Infraestructura
- Tests unitarios del RNG:
  - determinismo  
  - distribución razonable
- ~~Logs verificables~~ ✔
- Múltiples jugadores con un solo mazo (pendiente)
- ~~Nonce persistente~~ ✔
- ~~Verificador externo (verify.py)~~ ✔

### Experiencia de usuario
- Prints más bonitos
- Mensajes más amigables
- Interfaz web mínima
- Verificador web (futuro)

---

## Cómo funciona el protocolo

1. Servidor genera `server_seed` y publica su commit.  
2. Jugador envía `client_seed` (autenticada con MAC).  
3. Se crea el RNG con ambas seeds + nonce.  
4. Se juega la ronda (Blackjack individual o multijugador).  
5. El servidor revela `server_seed`.  
6. `verify.py` reconstruye y confirma que no hubo trampa.

---

## Flujo mínimo pa probar (MVP)

- Ejecutar `python main.py`.
- Ver el commit.
- Enviar o generar client_seed.
- Jugar blackjack.
- Ver el resultado.
- El sistema guarda todo en logs silenciosos.
- Ejecutar `python verify.py` para revisar todo.

---

## Qué falta pa tener un casino "decente"

- Multi-jugador real con un solo mazo.  
- Variantes avanzadas del blackjack.  
- Análisis formal de seguridad (IND-CPA, UF-CMA, compromiso).  
- Interfaz decente, no solo consola.  
- Sistema de apuestas real.

---

## Notas finales (por si acaso)

- La aleatoriedad no se puede manipular a mitad del juego gracias al commit.  
- La client_seed queda protegida con HMAC (UF-CMA).  
- El verificador externo asegura que todo es reproducible.  
- No se confía en el servidor: la gracia es que **no se necesita confiar**.

