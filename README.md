# Probador de demos Hacksaw

Repositorio independiente para comprobar IDs y URLs del cliente Hacksaw sin utilizar SlotsLaunch.

Prueba el lanzador público de staging y, cuando obtiene una ruta `/ID/version/index.html` real, abre el cliente desde `static-live.hacksawgaming.com` en un navegador aislado. Clasifica errores HTTP, `version.json`, títulos, canvas, carga de scripts y fallos de autenticación de demo.

**Un HTTP 200 no significa que el juego sea jugable.** Las URLs de sesión son temporales y el probador no ejecuta apuestas ni intenta eludir autenticación.

## Ejecutar

En **Actions → Probar IDs Hacksaw → Run workflow**. Los resultados se descargan desde el artefacto `hacksaw-probe-results` (CSV, JSON y resumen). La lista inicial de IDs se edita en [ids.json](ids.json).

Para ejecutar localmente:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python probe.py
```

El workflow también se ejecuta en cada actualización del código o de los IDs.
