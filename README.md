# Casino-Virtual

Básicamente un casino donde el servidor no puede hacerle la desconocida al jugador, y todo queda verificable criptográficamente.  
La idea es que el jugador pueda decir "demuéstrame que no me estái cagando", y nuestro super casino responda "EVIDENCIA".

---

## Idea general del proyecto

Queremos un casino donde:
- Los juegos tienen resultados que se pueden verificar después.
- El servidor no puede cambiar la aleatoriedad una vez que mostró el commit.
- El jugador tampoco puede hacerse el vivo y mandar seeds falsas.
- Todo el proceso (ronda completa) queda fijado por dos seeds: la del servidor y la del jugador, más un `nonce` que ahora sí aumenta bien.

Flujo básico:  
El casino muestra un commit sobre su seed, el jugador manda la suya, se corre el juego, y al final el casino revela su seed original para verificación.  
El jugador reconstruye la aleatoriedad y revisa si el servidor actuó correctamente o si intentó pasarse de listo.

---

## Consideraciones nuevas según feedback 

### 1. Qué pasa si el servidor "cambia" la client_seed que envió el jugador?
Nuestro sistema como estaba no lo protegía explícitamente.  
Para evitar esta situación, debemos:

- Autenticar los mensajes entre cliente y servidor (MAC o AEAD).
- Guardar (y mostrar) la client_seed que el servidor dice usar durante la ronda.
- Implementar un verificador externo que puede revisar:
  - server_seed revelada,
  - client_seed enviada por el usuario,
  - nonce de la ronda,
  - secuencia de cartas.

Así, si el servidor inventa una client_seed distinta, eso queda inmediatamente en evidencia al reconstruir la ronda.

### 2. Por qué SHA-256?  
- Porque nos da un **commitment** con propiedades:
  - **Hiding**: el hash no filtra la seed del servidor.
  - **Binding**: el servidor no puede cambiar su seed después.
- Es rápido, estándar y fácil de verificar.
- No nos mete dependencias innecesarias (como llaves públicas).

### 3. Libertades del casino en blackjack  
Blackjack es especial porque el casino tiene **reglas fijas** ("pide hasta 17", etc.). Esto significa:
- El casino no puede reaccionar estratégicamente a lo que hace el jugador.
- Dado un mazo ordenado por el RNG, las acciones del dealer quedan 100% determinadas.
- Entonces el servidor tampoco puede influir en la partida después del barajado.

Esto NO es cierto en juegos donde los jugadores pueden reaccionar a otros (poker, por ejemplo), ya que ahí sí hay decisiones estratégicas de más de un participante.

### 4. Múltiples jugadores usando el mismo mazo  
Si dos jugadores están sentados en la misma mesa:
- Todos deben usar **el mismo mazo generado** por el RNG.
- El orden de carta 1, 2, 3, ... debe ser verificable por todos los jugadores simultáneamente.
- Hay que formalizar:
  - cómo se reparten las cartas entre jugadores,
  - cómo se evita que el casino favorezca a uno u otro,
  - cómo se mantiene un solo flujo de RNG común.

### 5. Nonce ahora sí aumenta  
Antes teníamos `nonce = 0` fijo.  
Ahora el plan es:
- tener un `nonce` por ronda,  
- incrementarlo (`nonce += 1`) cada vez que se juega una nueva mano.

Además, dejamos de concatenar con símbolos como `|`, porque realmente no aporta nada: basta concatenar strings o bytes limpios.

### 6. No es necesario incluir llaves públicas/privadas… salvo que sus ataques lo requieran  
Nuestro sistema base no necesita criptografía asimétrica, *a menos que*:
- queramos evitar que un tercero modifique mensajes (pero eso se resuelve con MAC/AEAD),
- queramos un verificador descentralizado (ahí entran VRF/Smart Contracts).

Pero no las metemos “porque sí”, para evitar complejidad innecesaria.

### 7. Debemos crear un verify.py  
El ayudante lo pidió. Tareas:
- Input: server_seed, client_seed, nonce, historial de cartas entregadas.
- Output: “verifica / no verifica”.
- Idealmente simple pa que cualquier usuario lo pueda correr.

### 8. Explicar Rejection Sampling  
Nuestro RNG usa rejection sampling pa obtener números uniformes.  
Ejemplo corto (para el informe):
- Tomamos un número grande de 32 bits.
- No todos los valores se dividen exacto por el rango.
- Entonces rechazamos los valores que causarían sesgo.
- Esto asegura distribución uniforme en [a, b].

### 9. Revisar otras formas de Provably Fair  
Nos pidieron estudiar alternativas además del commit + hash.  
Podemos considerar:
- **Smart contracts**: verificación descentralizada del barajado.
- **VRFs** (Verifiable Random Functions): generan números impredecibles pero verificables.
- **Randomness beacons** (Faros de Aleatoriedad): tipo NIST Beacon o drand, que proveen randomness pública.

---

## Cosas que se pueden implementar (lista pa ir tachando)

### Parte criptográfica (la volá seria)
- Hacer el módulo completo de aleatoriedad "provably fair" con SHA-256.
- Añadir un MAC para asegurar que el servidor no cambie la client_seed ni modifique mensajes.
- Incluir un esquema de compromiso formal (propiedades **hiding** y **binding**).
- Documentar ataques posibles: servidor malicioso, jugador malicioso, terceros, colusión entre jugadores, etc.
- Extender a AEAD si queremos confidencialidad y autenticidad juntas.
- Investigar alternativas: VRF, faros de aleatoriedad, smart contracts (!!).

### Parte del juego (lo que todos ven)
- Mejorar blackjack:
  - doblar (?)
  - dividir pares (?)
  - seguro si el dealer tiene A
- Agregar juegos nuevos:
  - ruleta (fácil)
  - dados (?)
  - poker (probablemente peludo, porque ahí sí hay estrategia).

### Infraestructura y calidad (pa que no se nos caiga)
- Tests unitarios del RNG:
  - determinismo,
  - mínima uniformidad.
- Logs verificables por ronda:
  - server_seed,
  - client_seed original,
  - nonce,
  - commit,
  - cartas entregadas.
- Manejo de múltiples jugadores con un solo mazo.
- Nonce que realmente aumenta por ronda.
- Crear `verify.py` para verificación fácil.

### Mejoras de experiencia
- Imprimir las cartas de manera más bonita.
- Mensajitos más amigables para el jugador.
- Una interfaz web muy simple para mostrar rondas.
- Un verificador web donde el usuario pegue seeds y vea si calza.

---

## Cómo funciona el protocolo

1. El servidor genera su `server_seed` y publica su hash (`commit`).  
   Esto fija el comportamiento futuro del servidor (binding).

2. El jugador envía su `client_seed`.  
   O el sistema la crea, filo.

3. Con ambas seeds + un `nonce` se crea el RNG que define todo el juego.

4. Se juega la ronda:
   - Se baraja con el RNG,
   - El blackjack se ejecuta según reglas fijas del casino.

5. El servidor revela su `server_seed`.  
   El jugador verifica:
   - commit correcto,
   - reconstrucción exacta del mazo,
   - que las jugadas del dealer concuerdan con las reglas del juego.

---

## Flujo mínimo pa probar (MVP)   

- Abrir consola, ejecutar `python casino_blackjack.py`.
- El programa:
  - te muestra el commit,
  - te pide la client_seed,
  - reparte cartas,
  - muestra resultado,
  - revela la server_seed,
  - y te deja verificar todo después.

---

## Qué falta pa tener un casino "decente"

- El verificador externo `verify.py` (obligatorio según ayudante).
- Manejo completo de 2+ jugadores con un solo mazo.
- Implementar rondas consecutivas con `nonce` creciente.
- Capítulo formal de seguridad: IND-CPA, UF-CMA, compromiso (hiding/binding).
- Una interfaz decente y no pura consola.
- Sistema de apuestas real y pagos completos del blackjack.

---

## Notas finales (por si acaso)

- La aleatoriedad no se puede manipular a mitad del juego, porque el commit obliga al servidor a usar la seed original.
- Autenticando los mensajes evitamos que el servidor "edite" la client_seed o que el jugador mande versiones falsas.
- Nada depende de confiar en el servidor: todo queda demostrable con seeds + nonce + RNG verificable.

