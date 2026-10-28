# Auditoría de acceso directo a demos Hacksaw — 28/10/2026

## Objetivo
Identificar el cliente HTML5 **de juegos que no figuran en el catálogo oficial accesible** y comprobar si funcionan sin pasar por SlotsLaunch.

## Resultados reproducibles

| Juego | ID visto en la demo pública | Versión del cliente | Dominio | Estado |
|---|---:|---|---|---|
| Hellmageddon | 2521 | 1.30.0 | static-stg.hacksawgaming.com | Canvas/recursos; wallet no inicializa |
| Ghost Vision | 2528 | 1.47.2 | static-stg.hacksawgaming.com | Canvas/recursos; wallet no inicializa |
| Buried by Night | 2577 | 1.21.1 | static-stg.hacksawgaming.com | Canvas/recursos; wallet no inicializa |

Otras variantes que devuelven título y recursos de juego:
- Hellmageddon: IDs **2522, 2524**
- Ghost Vision: IDs **2530, 2532**
- Buried by Night: ID **2580**

Los IDs de variante no deben considerarse equivalentes ni fungibles sin verificar.

### Cómo se detectó el enlace intermedio

En DGN Zone, el botón de demo consulta `/api/demo-url?id=...`, abre un iframe de `slotslaunch.com` y la página `/api/game-url` de SlotsLaunch deriva al lanzador de Hacksaw (`static-stg`). Por tanto, **DGN Zone también depende de SlotsLaunch**.

| Juego | Identificador interno en SlotsLaunch |
|---|---:|
| Hellmageddon | 47341 |
| Ghost Vision | 46493 |
| Buried by Night | 46495 |

### Control oficial independiente

Se probaron los botones **Try it** de `hacksawgaming.com`, aceptando cookies y confirmando mayoría de edad:

- Dark Summoning: ID **1392**, `static-live/1392/1.29.3/index.html`
- Le Bandit: ID **1309**, `static-live/1309/1.26.2/index.html`

Ambos generan un cliente legítimo desde la web del fabricante, pero **en el navegador de GitHub Actions también muestran `Connection lost to wallet`**. Por tanto, no puede inferirse del error que los títulos anticipados carezcan de demos jugables en todos los entornos.

### Inspección CORS

Desde GitHub Actions, las solicitudes HTTP `OPTIONS` (preflight de `POST`) a:
- `rgs-demo.hacksawgaming.com/api/play/authenticate`
- `rgs-demo.hacksawgaming.com/api/play/partnerSettings`
- `rgs-hacksaw-fun-stg.hacksawgaming.com/api/play/authenticate`
- `rgs-hacksaw-stg.hacksawgaming.com/api/play/partnerSettings`

respondieron **204** con cabeceras CORS. **No obstante**, el navegador reportó fallo de CORS o autorización durante la carga real. Una solicitud `OPTIONS` sintética exitosa no demuestra que se acepten los encabezados o la sesión de un lanzamiento real; la causa exacta sigue sin confirmarse.

## Comprobación adicional de static-live (ejecución completa)

La ejecución [40777628373](https://github.com/Shisetsu-Code/Probador/actions/runs/40777628373) terminó correctamente.

- **11 IDs sometidos a comprobación:** 10 clientes reales y un control negativo.
- **10 clientes reales:** HTTP 200 en `static-live`, título correcto, motor cargado.
- **10/10:** mensaje `Connection lost to wallet`; ninguna demo jugable verificada en GitHub Actions.
- Los resultados están en [results/direct_missing_id_checks.json](results/direct_missing_id_checks.json).
- El inventario compacto está en [results/clientes_identificados.csv](results/clientes_identificados.csv).

Nuevas rutas detectadas: `/2577/1.21.1/index.html`, `/2580/1.21.1/index.html`, `/2544/1.6.0/index.html`. El código HTTP corresponde a las solicitudes con parámetros demo de prueba, **no** certifica que la ruta sin parámetros inicie una sesión.

## Conclusión

**Se ha conseguido acceso a los archivos del cliente y sus IDs/versiones. No se ha validado una demo jugable independiente.** Los enlaces de cliente no sustituyen un lanzamiento demo válido del proveedor. No se recomienda ocultar el fallo con un proxy CORS, inventar tokens ni utilizar credenciales de terceros.

## Código y evidencia

- `probe.py` + `ids.json`: identifica títulos por game ID en Chromium.
- `direct.py`: comprueba la existencia del cliente en `static-live` con navegador aislado.
- `public_demo.py`: comprueba la ruta real desde páginas públicas y recoge capturas.
- `official_control.py`: verifica el flujo oficial completo de consentimiento, edad y botón Try it.
- `preflight.py`: inspección CORS HTTP de solo lectura.
- `trace_cors.py`: prueba de observabilidad CDP (los iframes de otro proceso no siempre quedan visibles).
- Pestaña **Actions**: los artefactos contienen JSON y capturas; no incluyen valores de token, cabeceras privadas ni cookies.

Para continuar hasta obtener una demo realmente funcional, se necesita un lanzamiento públicamente autorizado que permita inicializar el backend o colaboración del proveedor. La validación debe comprobar la respuesta de autenticación y la ausencia del error de wallet en una sesión fresca, sin asumir que HTTP 200 es éxito.
