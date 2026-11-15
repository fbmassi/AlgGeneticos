# TP3 — Algoritmos Genéticos

Resolución del acertijo de cinco casas de Inteligencia Artificial (UADE) con un
algoritmo genético real, Python 3.10 o posterior y biblioteca estándar. No requiere
instalar paquetes. La consigna original se incluye en
`C221-TP3-AlgoritmosGeneticos.pdf`; los materiales teóricos no forman parte del repositorio.

## Ejecutar en Windows 11

Desde PowerShell, ubicado en la raíz del repositorio `AlgGeneticos`, con Python
instalado y disponible mediante `py`:

```powershell
py -3 ga.py --seed 42
py -3 ga.py --seed 42 --immediate
py -3 -m unittest discover -s . -p "test_*.py" -v
py -3 experimentos.py
py -3 verificar.py
```

Se puede usar `python` en lugar de `py -3`. Para cambiar el presupuesto:

```powershell
py -3 ga.py --seed 7 --population 300 --generations 3000 --seconds 30
```

La consola muestra las casas de izquierda a derecha, las pistas cumplidas, el
motivo de corte y, solamente si la solución es válida, la profesión que utiliza
Vim. El código de salida es **0** para solución completa y **1** para resultado
parcial. `--generations 0` permite evaluar solo la población inicial;
`--seconds 0` detiene la búsqueda tras evaluar el primer candidato.

## Notebook de entrega

`TP3-AlgoritmosGeneticos.ipynb` muestra la representación, la población y el
fitness, ejemplos de los operadores, una ejecución con semilla 42, las quince
pistas y la comprobación independiente de la ambigüedad. Importa `ga.py` y
`verificar.py`, sin duplicar el algoritmo.

En Jupyter, abrí el notebook desde esta carpeta con un kernel de Python 3.10 o
posterior y ejecutá todas las celdas desde un kernel limpio. El notebook requiere
un entorno Jupyter; los scripts siguen utilizando únicamente la biblioteca estándar.

En Google Colab, abrí el archivo `.ipynb` mediante **Archivo > Subir notebook**.
Luego cargá `ga.py` y `verificar.py` en la carpeta de trabajo mediante el panel
**Archivos** y ejecutá todas las celdas. No es necesario instalar paquetes adicionales.

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
| `TP3-AlgoritmosGeneticos.ipynb` | Demostración ejecutable que reutiliza los scripts |
| `test_ga.py` | Pruebas automatizadas con `unittest` |
| `experimentos.py` | Diez semillas por interpretación y tasa de éxito observada |
| `verificar.py` | Enumeración exacta independiente para auditar la ambigüedad |
| `TECNICA.md` | Diseño, parámetros, resultados medidos y limitaciones |

`ga.py` no importa ni consulta la enumeración exacta. Las seis tareas solicitadas
se desarrollan en la [documentación técnica](TECNICA.md). TP1 y TP2 quedan fuera
del alcance de este trabajo.
