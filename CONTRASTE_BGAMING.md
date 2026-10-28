# Contraste de catálogos BGaming — 28/10/2026

## Alcance y metodología

Se compararon las siguientes fuentes públicas:

- [BGaming oficial — Slots](https://bgaming.com/game-type/slots?types=slots), expandiendo todos los botones SHOW MORE mediante Playwright en GitHub Actions.
- [ChoiceCasino — Slots BGaming](https://choicecasino.com/es/games/bgaming/slots): 61 nombres visibles en la respuesta pública; el sitio anuncia 258. GitHub Actions recibió Cloudflare 403, por lo que NO se pudo extraer ni verificar el total de 258.
- [SlotCatalog — BGAMING](https://slotcatalog.com/es/soft/BGAMING): el proveedor anuncia 399 juegos totales y 314 video slots; el listado paginado señala 397 entradas. Se revisaron 72 títulos indexados de las primeras 6 de 34 páginas. GitHub Actions recibió Cloudflare 403, por lo que NO pudo recorrer todas las páginas.

La normalización elimina mayúsculas, tildes, signos y marcas ™; variantes y cambios de nombre no se fusionan automáticamente.

## Cantidades comprobadas

| Métrica | Cantidad |
|---|---:|
| BGaming slots oficiales (fichas HTML) | 244 |
| BGaming slots oficiales (nombres únicos) | 243 |
| Fichas oficiales que muestran botón PLAY DEMO | 235 |
| ChoiceCasino (títulos visibles comprobados) | 61 |
| ChoiceCasino (contador anunciado, sin extracción completa) | 258 |
| SlotCatalog (juegos totales anunciados) | 399 |
| SlotCatalog (video slots declaradas) | 314 |
| SlotCatalog (entradas paginadas anunciadas) | 397 |
| SlotCatalog (títulos de páginas 1–6 contrastados) | 72 |

BGaming tiene dos URLs de ficha diferentes para Aztec Magic MEGAWAYS™, incluida la URL histórica /games/elden-ring. No se contaron como dos nombres distintos.

## Cruces por nombre normalizado

- **ChoiceCasino visible vs. BGaming oficial:** 58 de 61 coinciden. Los otros 3 no aparecen con ese nombre en el FILTRO de slots oficiales. BGaming oficial tiene 185 nombres que no están en la muestra visible de ChoiceCasino; **no** puede asegurarse que falten en su catálogo completo de 258.
- **SlotCatalog (páginas 1–6) vs. BGaming oficial:** 68 de 72 coinciden exactamente. Las 4 excepciones se explican debajo. No puede calcularse una diferencia exhaustiva entre las 314 slots declaradas y los 243 nombres oficiales sin acceder a las páginas restantes y separar categorías y ediciones.
- **Presentes en las tres muestras:** Aloha King Elvis, Aztec Magic Megaways, Alien Fruits, Lucky Dama Muerta, Burning Chilli X, Hottest 666, Alien Fruits 2 y Lucky 8 Merge Up.

## ChoiceCasino: 3 nombres sin coincidencia exacta con el filtro oficial

| Juego | Análisis |
|---|---|
| Clash of Gods: Anubis vs Hades | BGaming publicó oficialmente ese título como colaboración con Golden Goat Gaming. El catálogo oficial filtrado incluye Clash of Gods Power Duel; no deben fusionarse automáticamente sin confirmar equivalencia/edición. |
| Fortune Spin | **No es un slot:** BGaming lo clasifica como **Casual**, por lo que es razonable que no aparezca bajo types=slots. |
| 1 2 3 4 5 | No apareció en las 243 entradas del filtro oficial; necesita verificación de categoría o vigencia. |

## SlotCatalog: 4 nombres de la muestra no presentes exactamente en el filtro oficial

| Juego | Análisis |
|---|---|
| Plinko 2 Halloween | Juego casual, no una tragamonedas tradicional; BGaming lo lista en su mapa global. |
| Platinum Lightning | Figura en el mapa global de BGaming, pero no en las 243 entradas del filtro consultado. |
| Miss Cherry Fruits Jackpot Party | Figura en el mapa global de BGaming, pero no en las 243 entradas del filtro consultado. |
| Gold Rush With Johnny Cash | El mapa global de BGaming contiene un título de nombre similar, Gold Rush – Johnny Cash; requiere verificar si se trata de la misma edición. |

No son cuatro juegos necesariamente ausentes de BGaming; hay mezcla de filtros, modalidades, ediciones y nombres.

## Ejemplos de slots oficiales ausentes de los 61 visibles en ChoiceCasino

Black Friday Madness, Luxury Feast Hold and Win, Joker Mask, Formula x10000, Wild Cash Gold, Khonsu Merge Up, Hot Rocket Mega Potz, Red Hot Chilli Chickens, Johnny vs Chicken, Wincent Wolf, Fortune Trio: Minions Of Fu, Miss Cherry Wild Frames, St. Patrick's Pots Hold and Win y Mystic Reels.

Los tres primeros aparecen sin botón PLAY DEMO en la ficha de catálogo oficial consultada; no se debe confundir el anuncio del juego con su disponibilidad comercial.

## Archivos

- [Matriz de comparación CSV (250 nombres distintos de las muestras combinadas)](results/bgaming/comparison.csv).
- [Matriz y métricas JSON](results/bgaming/comparison.json).
- [243 nombres oficiales / 244 fichas con URL del fabricante](results/bgaming/official_slots.json).
- [61 nombres visibles de ChoiceCasino](results/bgaming/choicecasino_visible.json).
- [72 nombres de SlotCatalog (primeras seis páginas)](results/bgaming/slotcatalog_sample72.json).
- [Evidencia de Cloudflare 403 de los navegadores automatizados](results/bgaming/diagnostics.json).

## Evaluación

Para un catálogo maestro, utilizar el listado oficial filtrado por tipo y su mapa global como fuentes primarias, añadir fuentes secundarias con etiquetas de procedencia y estado; no identificar un juego como ausente solo porque no aparece en el primer bloque de una página, y nunca confundir títulos Casual/Exclusive con Slots.
