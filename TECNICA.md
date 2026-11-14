# Diseño y verificación del TP3

## Materiales y correspondencia con la consigna

Se revisaron ambos PDF y el DOCX de enunciado incluidos en
`TP 3 - Algoritmos Genéticos.zip`, además de `dev_ga_base.py`. Los tres enunciados
coinciden en las 15 pistas y las tareas; se normalizan las grafías Atóm/Atom y
Neo4J/Neo4j sin cambiar su significado. El esqueleto tiene partes incompletas y
permite proponer otra estructura: se reemplaza por funciones pequeñas y dos
clases de datos. No se reutilizan sus variables sin definir ni su codificación
binaria, que permitiría valores inválidos y duplicados.

Como apoyo se consultaron las páginas 26–41 y 48–52 de
`8. Algoritmos Genéticos.pdf` y los apartados de algoritmos genéticos y del
acertijo de Einstein de `Apuntes - Inteligencia Artificial (2).docx`. Los apuntes
describen selección por aptitud, cruzamiento, mutación, penalizaciones y genes
inmutables. La notebook mencionada en clase no está en los materiales disponibles
y no es necesaria para ejecutar el TP.

| Tarea | Resolución |
| --- | --- |
| 1. Diseñar individuo | Cinco permutaciones de posiciones, una por categoría |
| 2. Generar población inicial | Barajado aleatorio con semilla y tres genes fijos |
| 3. Selección, cruce y mutación | Torneo, cruce de orden y swaps |
| 4. Tres condiciones de corte | Todas las pistas, generaciones o tiempo |
| 5. Alternativas de generación | Inmigrantes y reinicialización implementados; otras alternativas explicadas abajo |
| 6. Resolver y responder Vim | Validación completa y respuesta relativa a la solución encontrada |

## Individuo y población inicial

Cada individuo es una tupla inmutable de cinco tuplas. Las filas representan,
en orden, colores, profesiones, lenguajes, bases de datos y editores. El orden
de valores está declarado en `CATEGORIES`. Cada gen guarda la **posición de la
casa** del valor correspondiente, de 0 a 4; la consola muestra de 1 a 5. Por
ejemplo, la fila de profesiones `(1, 2, 4, 3, 0)` sitúa al Matemático en la segunda
casa y al Desarrollador en la primera. `houses` invierte esta representación para
mostrar una fila por casa.

Cada categoría es una permutación de `0,1,2,3,4`: garantiza cinco valores distintos,
sin ausentes ni duplicados. `well_formed` verifica esta propiedad incluso para
individuos externos, sin presuponer las pistas.

`random_individual` baraja las posiciones libres mediante una instancia local de
`random.Random(seed)`. Se fijan Desarrollador en 0 (pista 10), Notepad++ en 2
(pista 9) y Azul en 0 (consecuencia de las pistas 10 y 15). Esto reduce el espacio
sin eliminar soluciones válidas ni predefinir quién usa Vim. Se mantienen estas
tres ubicaciones en todos los operadores; sus padres deben pertenecer a este
mismo espacio de búsqueda. El resto de las asignaciones es aleatorio. La
población puede contener individuos repetidos; la unicidad requerida es la de
los atributos dentro de cada individuo.

## Aptitud y validez

`clue_status` devuelve 15 booleanos en el orden del enunciado. La pista 1 es la
estructura de cinco casas y las otras 14 son las relaciones originales. Una
estructura mal formada se rechaza con `ValueError` antes de calcular la aptitud.
Se usa **fitness = 15 − cantidad de pistas incumplidas**, equivalente a contar
pistas satisfechas. No hay pesos arbitrarios ni pistas agregadas. La pista 1 y
las tres pistas incorporadas por construcción aportan una constante al AG, pero
se verifican también en individuos externos.

Las igualdades comparan posiciones de dos atributos; las pistas 9 y 10 comparan
contra una ubicación fija. Las pistas 11 y 12 exigen diferencia absoluta igual a
uno. La pista 6 usa `verde > blanca` por defecto, o `verde == blanca + 1` cuando
se activa la interpretación inmediata.

La comprobación final `is_solution` exige estructura válida y **todas** las
condiciones. No acepta solamente un puntaje almacenado. El AG confirma mediante
ella cualquier candidato con fitness 15. `vim_user` vuelve a validar y rechaza
resultados parciales. No se cambia «el Desarrollador vive en azul» por la pista
distinta «vive junto a azul» del ejemplo clásico de Einstein.

## Operadores y reemplazo

1. **Torneo de tres:** sortea tres índices con reemplazo y selecciona el mayor
   fitness. Los empates favorecen al primero sorteado, sin ordenar por profesión.
2. **Cruce de orden OX:** para cada categoría extrae los genes libres de ambos
   padres. Copia un segmento del primero y rellena circularmente las otras
   posiciones siguiendo el orden del segundo, omitiendo valores ya presentes.
   Reincorpora los genes fijos. Los padres permanecen inmutables. Si no se aplica
   cruce, se copia un padre y se permite mutarlo.
3. **Mutación:** cada categoría tiene probabilidad 0,12 de intercambiar dos genes
   libres. Mantiene las permutaciones y los genes fijos; no realiza búsqueda
   exhaustiva, reparación por pistas ni mejora local oculta.
4. **Reemplazo generacional:** conserva dos élites sin cambios, incorpora quince
   inmigrantes aleatorios y completa la población con descendientes. Después de
   cien generaciones sin mejora del mejor fitness, reinicializa la población
   completa, sin reinsertar las élites en esa generación para evitar volver
   inmediatamente a la misma meseta. El mejor candidato global se conserva
   aparte para informar correctamente un corte por límites. El contador se
   reinicia con una mejora global o con esa reinicialización.

## Parámetros y condiciones de corte

| Parámetro predeterminado | Valor y motivo |
| --- | --- |
| Población | 300: diversidad con evaluación barata |
| Torneo | 3: presión selectiva moderada |
| Probabilidad de cruce por descendiente | 0,30: recombina sin destruir siempre las combinaciones actuales |
| Probabilidad de swap por categoría | 0,12: cambios pequeños, sin congelar las posiciones |
| Élites | 2: evita perder los mejores candidatos |
| Inmigrantes por generación | 15 (5 %): incorpora diversidad continua |
| Reinicialización de población | 100 generaciones sin mejora global: permite escapar de mesetas |
| Máximo de generaciones | 3000: presupuesto finito de evolución |
| Máximo de tiempo | 30 segundos: presupuesto práctico configurable |
| Semilla de la consola | 42: facilita repetir una demostración |

Los parámetros completos se pueden ajustar mediante `Config` desde Python. La
consola expone semilla, población, generaciones, tiempo e interpretación; al
cambiar población ajusta inmigrantes al 5 % con tope de 15 y élites hasta 2.

Se implementan tres cortes explícitos: `solucion`, `generaciones` y `tiempo`. La
población inicial se considera generación 0; el máximo cuenta las generaciones
evolutivas adicionales. El tiempo se mide con `time.monotonic`, desde antes de
generar la población inicial, y se controla tras evaluar cada nuevo candidato.
Con tiempo cero se evalúa al menos uno para poder devolver un resultado. El
límite no es de tiempo real estricto: puede sobrepasarse por el costo de un
candidato y las operaciones de preparación de la generación.

Si se detecta una solución en esa evaluación, tiene prioridad sobre los límites;
en los demás casos el tiempo se comprueba antes del siguiente paso, y el corte
por generaciones ocurre al finalizar el presupuesto. Una generación puede
interrumpirse por tiempo o solución. Una salida parcial muestra las pistas
incumplidas y no atribuye Vim a ninguna profesión como respuesta válida.

## Alternativas para incorporar individuos

Se implementan generación aleatoria inicial, descendientes por recombinación y
mutación, inmigrantes aleatorios y reinicialización de población. La
reinicialización parcial conservando élites se ensayó, pero no se usa en la
configuración final: atraía rápidamente a la población a la misma meseta. Otra
alternativa, **no implementada**, es la generación guiada que satisface más pistas
antes de introducir un individuo; reduce combinaciones inútiles, pero agrega
sesgo y lógica específica del acertijo. Tampoco se implementan solucionadores
de restricciones ni búsqueda local dentro del AG. La enumeración exacta de
`verificar.py` tiene exclusivamente un propósito de auditoría independiente.

## Ambigüedad verificada de Vim

`verificar.py` enumera las permutaciones de posiciones por categoría y poda por
las pistas ya evaluables. Tiene sus propios predicados, no importa el AG ni su
fitness y nunca se invoca desde `ga.py`. El recorrido cubre todos los órdenes de
las cinco categorías; solo descarta ramas que contradicen pistas. La deducción
Azul=primera casa es válida en ambas interpretaciones.

| Interpretación de derecha | Soluciones | Vim: Desarrollador | Hacker | Ingeniero | Matemático |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cualquier posición mayor | 31 | 12 | 6 | 1 | 12 |
| Inmediatamente siguiente | 14 | 6 | 2 | 1 | 5 |

No hay soluciones donde el Analista use Vim, porque usa Atom. Las 14 soluciones
inmediatas forman un subconjunto estricto de las 31 textuales. Estos resultados
verifican los números mencionados en las instrucciones del trabajo, sin asumirlos
como condición del algoritmo genético. La respuesta académica debe distinguir
la profesión encontrada en una ejecución de una respuesta universal que las
pistas no determinan. Corresponde al docente aclarar o agregar pistas si se busca
una única respuesta.

## Resultados y pruebas

Se ejecutó Python 3.13.4 en Windows con los parámetros finales de la tabla, sin
dependencias externas. `py -3 TP3/experimentos.py` reproduce las semillas 0–9 en
ambos modos. Cada resultado de esa tanda se validó antes de contabilizarlo:

| Semilla | Generación textual | Segundos | Vim textual | Generación inmediata | Segundos | Vim inmediata |
| ---: | ---: | ---: | --- | ---: | ---: | --- |
| 0 | 148 | 0,928 | Matemático | 126 | 0,680 | Desarrollador |
| 1 | 23 | 0,136 | Desarrollador | 19 | 0,108 | Matemático |
| 2 | 10 | 0,070 | Matemático | 23 | 0,132 | Matemático |
| 3 | 16 | 0,101 | Desarrollador | 131 | 1,030 | Hacker |
| 4 | 21 | 0,122 | Desarrollador | 21 | 0,158 | Hacker |
| 5 | 30 | 0,187 | Matemático | 37 | 0,323 | Hacker |
| 6 | 12 | 0,072 | Desarrollador | 22 | 0,174 | Desarrollador |
| 7 | 11 | 0,067 | Desarrollador | 22 | 0,171 | Desarrollador |
| 8 | 7 | 0,041 | Ingeniero | 7 | 0,053 | Ingeniero |
| 9 | 9 | 0,051 | Matemático | 13 | 0,075 | Matemático |

Éxito: **10/10 en cada interpretación**, con 15/15 pistas. Se verificaron además
las semillas 10–29 sin cambiar parámetros: **20/20 por interpretación**. En ese
grupo, el modo textual necesitó entre 10 y 126 generaciones (7,503 s acumulados)
y el inmediato entre 11 y 247 (14,836 s acumulados). Total de la configuración
final: **60/60 ejecuciones completas, 100 % observado**. Ninguna terminó por un
límite ni se aceptó como solución un candidato parcial.

Para repetir la ampliación desde PowerShell:

```powershell
@'
import sys
sys.path.insert(0, "TP3")
from ga import Config, solve, is_solution
for immediate in (False, True):
    results = [solve(Config(seed=s, immediate=immediate)) for s in range(10, 30)]
    print(immediate, sum(is_solution(r.individual, immediate) for r in results), len(results))
'@ | py -3 -
```

La demostración con semilla 42 terminó en generación 9 con el Matemático usando
Vim en el modo textual (0,057 s), y en generación 22 con el Desarrollador usando
Vim en el inmediato (0,131 s). Ambas tablas cumplen todas las pistas de su modo.

Los ensayos iniciales con cruce 0,85 y mutación 0,20 resolvieron 10/10 casos
textuales y 9/10 inmediatos con semillas 0–9 y límite de 30 s. Bajar la mutación
sin renovar la población mantuvo mesetas de 14/15 pistas. Esos resultados
motivaron la configuración final; no se presentan como ejecuciones exitosas.

La suite incluye **23 pruebas**: estructura y unicidad, codificación/decodificación,
las 15 pistas contra un oráculo formulado por casas (500 individuos arbitrarios
en ambos modos), igualdad frente a vecindad y dirección, rechazo de falsos
positivos, torneo y OX con resultados esperados, swaps, 300 pares de padres con
operadores preservando estructura, las tres condiciones de corte, reinicios y
conservación del mejor global, repetibilidad, parámetros inválidos, consola y
códigos de salida. También verifica las 31 y 14 soluciones exactas con el
validador y con el oráculo por casas, sus distribuciones de Vim y la inclusión de
un conjunto en el otro. La tanda de semillas es un experimento separado de la
suite unitaria.

## Ventajas y limitaciones

El AG permite explorar combinaciones con operadores pequeños y conservar
representaciones válidas, y sirve para explicar evolución, selección y diversidad.
La representación por permutaciones evita penalizar duplicados que nunca deberían
generarse. Sus desventajas son la sensibilidad a parámetros y semillas, las
mesetas de fitness y la ausencia de garantía de convergencia o unicidad. Para
este problema pequeño, la enumeración con poda resulta más apropiada si el
objetivo fuese demostrar todas las respuestas; aquí queda separada porque la
consigna exige resolver mediante un algoritmo genético.

Una tasa de éxito medida solo describe esas ejecuciones. La semilla reproduce
individuo, puntaje, generación y motivo de corte si no interviene el límite de
tiempo, con la misma versión de Python y los mismos parámetros. El tiempo real
varía según equipo y carga; un corte temporal puede cambiar entre ejecuciones.
