# Resultados de la primera ejecución — 28/10/2026

[Ver ejecución de GitHub Actions](https://github.com/Shisetsu-Code/Probador/actions/runs/40775667385)

## Resumen

| Métrica | Resultado |
|---|---:|
| IDs probados | 35 |
| IDs que entregaron version.json HTTP 200 | 30 |
| Clientes que cargaron canvas | 30 |
| IDs rechazados en esta muestra | 5 |
| Demos con autenticación exitosa verificada | 0 |

**IMPORTANTE:** HTTP 200, `version.json` y canvas prueban carga de recursos, **no jugabilidad**.

## Títulos que nos interesan

| ID | Título identificado | Estado |
|---:|---|---|
| 2522 | Hellmageddon | Recursos |
| 2524 | Hellmageddon | Recursos |
| 2528 | Ghost Vision | Recursos |
| 2530 | Ghost Vision | Recursos |
| 2532 | Ghost Vision | Recursos |
| 2580 | Buried by Night | Recursos |
| 2544 | Donny Dough OG | Recursos |
| 2526 | Le Platin | Recursos |
| 2484 | Corporation Wars | Recursos |
| 2556 | Richville Rumble | Recursos |

Múltiples IDs que muestran el mismo nombre no demuestran que sean intercambiables: podrían representar variantes de lanzamiento.

## Pruebas de clientes directos

Se obtuvo la ruta de staging y se abrió desde `static-live.hacksawgaming.com`, en un navegador nuevo:

- **Hellmageddon / 2524** → `/2524/1.30.0/index.html`: HTML 200, canvas, **error de wallet/CORS**.
- **Ghost Vision / 2528** → `/2528/1.47.2/index.html`: HTML 200, canvas, **error de wallet/CORS**.
- **Dark Summoning / 1392** → `/1392/1.29.3/index.html`: HTML 200, canvas, **error de wallet/CORS**.
- **Mines / 1126** → `/1126/1.145.0/index.html`: `static-live` devuelve 403 para esa versión.

Las URL del cliente no incluyen automáticamente una sesión demo válida. No se incluyeron sesiones, credenciales ni tokens de usuarios.

## Informes originales

- [IDs y respuestas detalladas (JSON)](results/id_tests.json)
- [IDs y resultados (CSV)](results/id_tests.csv)
- [Prueba de clientes directos (JSON)](results/direct_missing_id_checks.json)
- [Resumen (JSON)](results/summary.json)
