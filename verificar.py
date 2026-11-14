"""Auditoría exacta independiente de la ambigüedad. NO se usa desde ga.py."""

from collections import Counter
from itertools import permutations


def enumerate_solutions(immediate=False):
    """Enumera todas las asignaciones con poda por las pistas originales.

    Tuplas de posiciones por valor, en el orden de categorías de ga.py.
    No importa el fitness, los operadores ni las posiciones fijas del AG.
    """
    perms = list(permutations(range(5)))
    for colors in perms:
        red, blue, green, white, yellow = colors
        if blue != 0:  # Consecuencia de Desarrollador=primera y azul.
            continue
        if not (green == white + 1 if immediate else green > white):
            continue
        for professions in perms:
            mathematician, hacker, engineer, analyst, developer = professions
            if developer != 0 or developer != blue or mathematician != red:
                continue
            for editors in perms:
                brackets, sublime, atom, notepad, vim = editors
                if notepad != 2 or brackets != green or analyst != atom:
                    continue
                for databases in perms:
                    cassandra, mongo, neo, redis, hbase = databases
                    if cassandra != yellow or engineer != mongo or neo != sublime:
                        continue
                    for languages in perms:
                        python, csharp, java, cpp, javascript = languages
                        if hacker != python or redis != java:
                            continue
                        if abs(hbase - javascript) != 1 or abs(cassandra - csharp) != 1:
                            continue
                        yield colors, professions, languages, databases, editors


def summary(immediate=False):
    # Nombres locales: la auditoría no depende de la implementación del AG.
    names = ("Matemático", "Hacker", "Ingeniero", "Analista", "Desarrollador")
    solutions = list(enumerate_solutions(immediate))
    users = Counter(names[p.index(e[4])] for _, p, _, _, e in solutions)
    return solutions, users


if __name__ == "__main__":
    for immediate in (False, True):
        solutions, users = summary(immediate)
        print(f"Derecha {'inmediata' if immediate else 'no necesariamente inmediata'}: {len(solutions)} soluciones")
        for user, count in sorted(users.items()):
            print(f"  Vim: {user}: {count}")
