# Casino-Virtual

Básicamente un casino donde el servidor no puede hacerle la desconocida al jugador, y todo queda verificable criptográficamente.  
La idea es que el jugador pueda decir "demuéstrame que no me estái cagando", y nuestro super casino responda "EVIDENCIA"

---

## Idea general del proyecto

Un casino donde:
- Los juegos tienen resultados que se pueden verificar.
- El servidor no puede cambiar la aleatoriedad después.
- El jugador no puede manipular nada a su favor.
- Todo queda determinístico y transparente una vez reveladas las semillas.

Idea: el casino muestra un commit, el jugador manda su seed, el juego corre, y después el casino revela su seed para verificación.  
El jugador puede reconstruir el mazo/resultado y confirmar que no hubo mano negra.

---

## Cosas que se pueden implementar (lista pa ir tachando)

### Parte criptográfica (la volá seria)
- Hacer el módulo completo de aleatoriedad "provably fair" basado en SHA-256.
- Añadir un MAC para no permitir que alguien meta mano en los mensajes.
- Documentar formalmente los ataques tolerados o no tolerados (ataques del servidor, del jugador, de terceros, colusiones, etc. no me acuerdo de más :P).
- Extender a AEAD si queremos confidencialidad y autenticidad juntas (tipo AES-GCM).

### Parte del juego (lo que todos ven)
- El blackjack básico, ahí subí una mini idea, en volá faltaría:
  - doblar cuando corresponde (?)
  - dividir pares (?)
  - seguro (si el dealer tiene A)
- Agregar más juegos:
  - ruleta (no debería ser difícil)
  - dados (?)
  - Poker (?) igaul me tinca peluo

### Infraestructura y calidad (pa que no se nos caiga)
- Test unitarios del RNG. Onda:
  - verificar determinismo
  - validar distribución general (no buscamos una prueba estadística brígida, pero sí mínimo razonable)
- Logs verificables de las rondas (guardar seeds y resultados).
- Esquema pa múltiples jugadores, sin que puedan coludirse.
- Poder correr varias rondas con las mismas seeds 

### Mejoras de experiencia
- Interfaz más decente, o al menos imprimir las cartas de forma más bacán.
- Un verificador externo pa que el jugador pueda pegar seeds y ver si el casino hizo trampa o no.
- Ajustar textos del programa para que sea más amigable, menos técnico.

---

## Cómo funciona el protocolo

1. El servidor inventa una `server_seed` al azar y manda el commit, que es básicamente el SHA-256 de esa seed. El jugador ve solo el hash, así que el servidor no puede cambiarlo después.

2. El jugador manda su `client_seed`(O el sistema se la inventa, filo)

3. Con ambas seeds + un `nonce` se genera toda la aleatoriedad.  

4. Se juega la ronda completa (blackjack por ahora).

5. El servidor revela su `server_seed` original.  
   El jugador puede verificar:
   - que el commit calza,
   - que reconstruyendo el mazo obtiene exactamente las mismas cartas,
   - que el servidor no se mandó ninguna trampa.

---

## Flujo mínimo pa probar (MVP)

- Abrir consola, ejecutar `python casino_blackjack.py`.
- El programa:
  - te muestra el commit del servidor (un hash largo).
  - te pide tu client_seed (o la genera).
  - reparte cartas, juegas tu mano.
  - se revela la server_seed.
  - puedes verificar manualmente si quieres.

---

## Qué falta pa tener un casino "decente"

- Que el código tenga un verificador aparte (pa que el usuario pueda pegar seeds y ver si calza).
- Manejar múltiples jugadores (sin que se caguen entre ellos).
- Implementar el juego de más de 1 persona
- Documentar la seguridad formaaaaally (IND-CPA, UF-CMA, etc) pero en lenguaje que entienda el profe.
- Poner una interfaz web decente (aunque sea HTML feo, pero digno).
- Sistema de apuestas real: plata, fichas, límites, pagos exactos del blackjack, etc.

---

## Notas finales (por si acaso)

- La aleatoriedad NO se puede manipular a mitad del juego por parte del servidor, porque el commit lo deja amarrado.
- Si el jugador intenta cambiar seeds o repetir mensajes, con MAC lo paramos.
- Nada aquí depende de "confiar" en el servidor; todo queda demostrable con las seeds reveladas.

