# TP3 — Algoritmos Genéticos

Resolución del acertijo de cinco casas de Inteligencia Artificial (UADE) con un
algoritmo genético real, Python 3.10 o posterior y biblioteca estándar. No requiere
instalar paquetes. Los materiales originales permanecen en `_materiales_locales/`,
excluidos de Git.

## Ejecutar en Windows 11

Desde PowerShell, con Python instalado y disponible mediante `py`:

```powershell
Set-Location C:\dev\TP_IA\ai-cases
py -3 TP3/ga.py --seed 42
py -3 TP3/ga.py --seed 42 --immediate
py -3 -m unittest discover -s TP3 -p "test_*.py" -v
py -3 TP3/experimentos.py
py -3 TP3/verificar.py
```

Se puede usar `python` en lugar de `py -3`. Para cambiar el presupuesto:

```powershell
py -3 TP3/ga.py --seed 7 --population 300 --generations 3000 --seconds 30
```

La consola muestra las casas de izquierda a derecha, las pistas cumplidas, el
motivo de corte y, solamente si la solución es válida, la profesión que utiliza
Vim. El código de salida es **0** para solución completa y **1** para resultado
parcial. `--generations 0` permite evaluar solo la población inicial;
`--seconds 0` detiene la búsqueda tras evaluar el primer candidato.

## Interpretación y respuesta

Por defecto, «verde a la derecha de blanca» significa **posición de verde mayor
que la de blanca**, sin imponer adyacencia. `--immediate` exige que sea la casa
inmediatamente siguiente. Las pistas de vecindad sí exigen distancia exactamente
uno, en cualquiera de los dos sentidos.

El acertijo **no tiene una respuesta única**: la auditoría independiente encuentra
31 soluciones con la interpretación predeterminada y 14 con la inmediata. En
ambas, Vim puede ser usado por el Desarrollador, Hacker, Ingeniero o Matemático.
La respuesta de una ejecución corresponde exclusivamente a la tabla encontrada.

## Archivos y alcance

| Archivo | Responsabilidad |
| --- | --- |
| `ga.py` | Representación, pistas, operadores, búsqueda y consola |
| `test_ga.py` | Pruebas automatizadas con `unittest` |
| `experimentos.py` | Diez semillas por interpretación y tasa de éxito observada |
| `verificar.py` | Enumeración exacta independiente para auditar la ambigüedad |
| `TECNICA.md` | Diseño, parámetros, resultados medidos y limitaciones |

`ga.py` no importa ni consulta la enumeración exacta. Las seis tareas solicitadas
se desarrollan en la [documentación técnica](TECNICA.md). TP1 y TP2 quedan fuera
del alcance de este trabajo.
