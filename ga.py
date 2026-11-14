"""TP3: algoritmo genético para el acertijo de las cinco casas (sin dependencias)."""

import argparse
from dataclasses import dataclass
from math import isfinite
from random import Random
from time import monotonic


# Cada fila contiene la POSICIÓN (0..4) de los valores en este orden.
CATEGORIES = (
    ("Rojo", "Azul", "Verde", "Blanco", "Amarillo"),
    ("Matemático", "Hacker", "Ingeniero", "Analista", "Desarrollador"),
    ("Python", "C#", "Java", "C++", "JavaScript"),
    ("Cassandra", "MongoDB", "Neo4j", "Redis", "HBase"),
    ("Brackets", "Sublime Text", "Atom", "Notepad++", "Vim"),
)
HEADERS = ("Color", "Profesión", "Lenguaje", "Base de datos", "Editor")
Individual = tuple[tuple[int, ...], ...]
# Pistas 10 y 9, más Azul=primera casa, deducida de 10 y 15.
FIXED = {0: (1, 0), 1: (4, 0), 4: (3, 2)}
FREE = tuple(tuple(i for i in range(5) if i != FIXED.get(r, (-1, -1))[0])
             for r in range(5))


def well_formed(individual):
    """Verifica las cinco permutaciones; no exige las pistas ni los genes fijos."""
    return (isinstance(individual, (tuple, list)) and len(individual) == 5
            and all(isinstance(row, (tuple, list)) and len(row) == 5
                    and all(type(x) is int for x in row)
                    and set(row) == set(range(5)) for row in individual))


def clue_status(individual, immediate=False):
    """Pistas 1..15 en el orden original. Una estructura inválida se rechaza."""
    if not well_formed(individual):
        raise ValueError("Se requieren cinco permutaciones de las posiciones 0..4")
    c, p, l, d, e = individual
    return (
        True,                           # 1: cinco casas, unicidad por categoría
        p[0] == c[0],                    # 2: Matemático - rojo
        p[1] == l[0],                    # 3: Hacker - Python
        e[0] == c[2],                    # 4: Brackets - verde
        p[3] == e[2],                    # 5: Analista - Atom
        c[2] == c[3] + 1 if immediate else c[2] > c[3],  # 6: derecha
        d[3] == l[2],                    # 7: Redis - Java
        d[0] == c[4],                    # 8: Cassandra - amarillo
        e[3] == 2,                       # 9: Notepad++ - centro
        p[4] == 0,                       # 10: Desarrollador - primera
        abs(d[4] - l[4]) == 1,           # 11: HBase vecino de JavaScript
        abs(d[0] - l[1]) == 1,           # 12: Cassandra vecino de C#
        d[2] == e[1],                    # 13: Neo4j - Sublime Text
        p[2] == d[1],                    # 14: Ingeniero - MongoDB
        p[4] == c[1],                    # 15: Desarrollador - azul
    )


def fitness(individual, immediate=False):
    """15 menos una penalización de 1 por cada pista incumplida."""
    return sum(clue_status(individual, immediate))


def is_solution(individual, immediate=False):
    """Validación final explícita, sin aceptar un puntaje como prueba de validez."""
    return well_formed(individual) and all(clue_status(individual, immediate))


def houses(individual):
    """Decodifica a cinco casas ordenadas de izquierda a derecha."""
    if not well_formed(individual):
        raise ValueError("Individuo mal formado")
    return tuple(tuple(values[row.index(pos)]
                       for values, row in zip(CATEGORIES, individual))
                 for pos in range(5))


def vim_user(individual, immediate=False):
    if not is_solution(individual, immediate):
        raise ValueError("Una solución parcial no permite responder quién usa Vim")
    return CATEGORIES[1][individual[1].index(individual[4][4])]


def random_individual(rng):
    rows = []
    for r in range(5):
        positions = list(range(5))
        row = [None] * 5
        if r in FIXED:
            gene, pos = FIXED[r]
            row[gene] = pos
            positions.remove(pos)
        rng.shuffle(positions)
        for gene, pos in zip(FREE[r], positions):
            row[gene] = pos
        rows.append(tuple(row))
    return tuple(rows)


def tournament(population, scores, rng, size=3):
    """Muestreo con reemplazo; gana el mayor fitness, desempate por orden sorteado."""
    contestants = [rng.randrange(len(population)) for _ in range(size)]
    return population[max(contestants, key=scores.__getitem__)]


def order_crossover(a, b, rng):
    """OX: conserva un segmento de a y completa circularmente en el orden de b."""
    n = len(a)
    start, end = sorted(rng.sample(range(n + 1), 2))
    child = [None] * n
    child[start:end] = a[start:end]
    remaining = [x for x in b[end:] + b[:end] if x not in child]
    slots = list(range(end, n)) + list(range(start))
    for i, x in zip(slots, remaining):
        child[i] = x
    return tuple(child)


def crossover(a, b, rng):
    """OX por categoría, excluyendo las posiciones fijadas por pistas."""
    rows = []
    for r, genes in enumerate(FREE):
        values = order_crossover(tuple(a[r][i] for i in genes),
                                 tuple(b[r][i] for i in genes), rng)
        row = list(a[r])
        for gene, pos in zip(genes, values):
            row[gene] = pos
        rows.append(tuple(row))
    return tuple(rows)


def mutate(individual, rng, rate=0.12):
    """Con probabilidad rate por categoría intercambia dos genes libres."""
    rows = []
    for r, genes in enumerate(FREE):
        row = list(individual[r])
        if rng.random() < rate:
            a, b = rng.sample(genes, 2)
            row[a], row[b] = row[b], row[a]
        rows.append(tuple(row))
    return tuple(rows)


@dataclass(frozen=True)
class Config:
    seed: int = 42
    population: int = 300
    max_generations: int = 3000
    max_seconds: float = 30.0
    tournament_size: int = 3
    crossover_rate: float = 0.3
    mutation_rate: float = 0.12
    elite: int = 2
    immigrants: int = 15
    restart_after: int = 100
    immediate: bool = False

    def __post_init__(self):
        for name in ("population", "max_generations", "tournament_size", "elite", "immigrants", "restart_after"):
            if type(getattr(self, name)) is not int:
                raise ValueError(f"{name} debe ser entero")
        if self.population < 2 or self.max_generations < 0 or self.tournament_size < 1 or self.restart_after < 1:
            raise ValueError("Población >= 2, generaciones >= 0, torneo y reinicio >= 1")
        if not 0 <= self.elite < self.population or not 0 <= self.immigrants < self.population - self.elite:
            raise ValueError("Elitismo e inmigrantes deben dejar lugar a descendientes")
        if not isfinite(self.max_seconds) or self.max_seconds < 0:
            raise ValueError("El tiempo debe ser finito y no negativo")
        if not 0 <= self.crossover_rate <= 1 or not 0 <= self.mutation_rate <= 1:
            raise ValueError("Las probabilidades deben estar entre 0 y 1")


@dataclass(frozen=True)
class Result:
    individual: Individual
    score: int
    generation: int
    elapsed: float
    reason: str


def solve(config=Config(), *, clock=monotonic):
    """Búsqueda exclusivamente genética. La generación inicial es la número 0."""
    rng = Random(config.seed)
    start = clock()
    best, best_score = None, -1
    last_progress = 0

    def evaluate(individual, generation):
        nonlocal best, best_score, last_progress
        score = fitness(individual, config.immediate)
        if score > best_score:
            best, best_score = individual, score
            last_progress = generation
        elapsed = clock() - start
        # Una solución efectivamente evaluada tiene prioridad sobre los límites.
        if score == 15 and is_solution(individual, config.immediate):
            return score, Result(individual, score, generation, elapsed, "solucion")
        if elapsed >= config.max_seconds:
            return score, Result(best, best_score, generation, elapsed, "tiempo")
        return score, None

    population, scores = [], []
    for _ in range(config.population):
        individual = random_individual(rng)
        score, result = evaluate(individual, 0)
        if result:
            return result
        population.append(individual)
        scores.append(score)

    for generation in range(1, config.max_generations + 1):
        ranked = sorted(range(len(population)), key=scores.__getitem__, reverse=True)
        next_population = [population[i] for i in ranked[:config.elite]]
        next_scores = [scores[i] for i in ranked[:config.elite]]
        restart = generation - last_progress >= config.restart_after
        if restart:
            last_progress = generation
            # El mejor global sigue reservado para el resultado. No reinsertarlo
            # evita atraer inmediatamente toda la población a la misma meseta.
            next_population, next_scores = [], []
        while len(next_population) < config.population:
            if restart or len(next_population) < config.elite + config.immigrants:
                child = random_individual(rng)
            else:
                a = tournament(population, scores, rng, config.tournament_size)
                b = tournament(population, scores, rng, config.tournament_size)
                child = crossover(a, b, rng) if rng.random() < config.crossover_rate else a
                child = mutate(child, rng, config.mutation_rate)
            score, result = evaluate(child, generation)
            if result:
                return result
            next_population.append(child)
            next_scores.append(score)
        population, scores = next_population, next_scores
    return Result(best, best_score, config.max_generations, clock() - start, "generaciones")


def format_result(result, config):
    valid = is_solution(result.individual, config.immediate)
    lines = [f"Semilla: {config.seed} | Derecha: {'inmediata' if config.immediate else 'cualquier posición mayor'}",
             f"Corte: {result.reason} | Generación: {result.generation} | Tiempo: {result.elapsed:.3f} s",
             f"Pistas cumplidas: {result.score}/15",
             "SOLUCIÓN COMPLETA" if valid else "MEJOR SOLUCIÓN PARCIAL; no satisface todas las pistas"]
    rows = [(str(i),) + house for i, house in enumerate(houses(result.individual), 1)]
    headers = ("Casa",) + HEADERS
    widths = [max(len(row[i]) for row in [headers] + rows) for i in range(6)]
    for row in [headers] + rows:
        lines.append(" | ".join(x.ljust(w) for x, w in zip(row, widths)))
    if valid:
        lines.append(f"En ESTA solución utiliza Vim: {vim_user(result.individual, config.immediate)}.")
        lines.append("El enunciado admite otras soluciones y distintos usuarios de Vim; ver verificar.py.")
    else:
        failed = [str(i) for i, ok in enumerate(clue_status(result.individual, config.immediate), 1) if not ok]
        lines.append("Pistas incumplidas: " + ", ".join(failed))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--population", type=int, default=300)
    parser.add_argument("--generations", type=int, default=3000)
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--immediate", action="store_true", help="Exigir verde inmediatamente a la derecha de blanca")
    args = parser.parse_args()
    try:
        config = Config(seed=args.seed, population=args.population,
                        max_generations=args.generations, max_seconds=args.seconds,
                        immigrants=min(15, max(0, args.population // 20)),
                        elite=min(2, max(0, args.population - 2)), immediate=args.immediate)
    except ValueError as error:
        parser.error(str(error))
    result = solve(config)
    print(format_result(result, config))
    return 0 if is_solution(result.individual, config.immediate) else 1


if __name__ == "__main__":
    raise SystemExit(main())
