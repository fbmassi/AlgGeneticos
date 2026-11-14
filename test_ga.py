"""Pruebas unitarias, oráculo por casas y auditoría exacta del TP3."""

import io
from contextlib import redirect_stdout
from dataclasses import replace
from random import Random
import unittest
from unittest.mock import patch

import ga
from verificar import enumerate_solutions, summary


# Ejemplo conocido usado SOLO en pruebas; no se inyecta en ejecuciones reales.
EXAMPLE_HOUSES = (
    ("Azul", "Desarrollador", "C++", "Neo4j", "Sublime Text"),
    ("Rojo", "Matemático", "Java", "Redis", "Vim"),
    ("Blanco", "Hacker", "Python", "HBase", "Notepad++"),
    ("Amarillo", "Analista", "JavaScript", "Cassandra", "Atom"),
    ("Verde", "Ingeniero", "C#", "MongoDB", "Brackets"),
)


def encode(houses):
    return tuple(tuple(next(i for i, h in enumerate(houses) if h[r] == value)
                       for value in category) for r, category in enumerate(ga.CATEGORIES))


EXAMPLE = encode(EXAMPLE_HOUSES)


def oracle(individual, immediate=False):
    """Reformula las pistas sobre las casas, sin llamar al fitness ni a clue_status."""
    homes = ga.houses(individual)

    def position(value):
        return next(i for i, home in enumerate(homes) if value in home)

    def together(a, b):
        return any(a in home and b in home for home in homes)

    def neighbors(a, b):
        return any((a in left and b in right) or (b in left and a in right)
                   for left, right in zip(homes, homes[1:]))

    return (
        len(homes) == 5,
        together("Matemático", "Rojo"),
        together("Hacker", "Python"),
        together("Brackets", "Verde"),
        together("Analista", "Atom"),
        position("Verde") - position("Blanco") == 1 if immediate
        else position("Verde") > position("Blanco"),
        together("Redis", "Java"),
        together("Cassandra", "Amarillo"),
        "Notepad++" in homes[2],
        "Desarrollador" in homes[0],
        neighbors("HBase", "JavaScript"),
        neighbors("Cassandra", "C#"),
        together("Neo4j", "Sublime Text"),
        together("Ingeniero", "MongoDB"),
        together("Desarrollador", "Azul"),
    )


class RepresentationTests(unittest.TestCase):
    def test_encoding_and_decoding(self):
        self.assertEqual(ga.houses(EXAMPLE), EXAMPLE_HOUSES)
        self.assertTrue(ga.well_formed(EXAMPLE))
        self.assertEqual(len(ga.houses(EXAMPLE)), 5)
        for column in zip(*ga.houses(EXAMPLE)):
            self.assertEqual(len(set(column)), 5)

    def test_random_population_valid_and_diverse(self):
        rng = Random(24)
        population = [ga.random_individual(rng) for _ in range(100)]
        self.assertEqual(len(set(population)), 100)
        for individual in population:
            self.assertTrue(ga.well_formed(individual))
            for r, (gene, pos) in ga.FIXED.items():
                self.assertEqual(individual[r][gene], pos)
        self.assertEqual(ga.random_individual(Random(1)), ga.random_individual(Random(1)))

    def test_malformed_rejected(self):
        for bad in (None, (), EXAMPLE[:4], ((0, 0, 2, 3, 4),) + EXAMPLE[1:],
                    ((0, 1, 2, 3, 5),) + EXAMPLE[1:],
                    ((False, 1, 2, 3, 4),) + EXAMPLE[1:],
                    ((0, 1, 2, 3),) + EXAMPLE[1:]):
            with self.subTest(bad=bad):
                self.assertFalse(ga.well_formed(bad))
                self.assertFalse(ga.is_solution(bad))
                with self.assertRaises(ValueError):
                    ga.fitness(bad)


class ClueTests(unittest.TestCase):
    def test_known_solution(self):
        self.assertEqual(ga.clue_status(EXAMPLE), (True,) * 15)
        self.assertEqual(ga.fitness(EXAMPLE), 15)
        self.assertTrue(ga.is_solution(EXAMPLE))
        self.assertEqual(ga.vim_user(EXAMPLE), "Matemático")

    def test_right_is_directional_and_optionally_immediate(self):
        self.assertFalse(ga.clue_status(EXAMPLE, True)[5])
        self.assertFalse(ga.is_solution(EXAMPLE, True))
        reverse = list(EXAMPLE)
        reverse[0] = tuple(4 - x for x in reverse[0])
        self.assertFalse(ga.clue_status(tuple(reverse))[5])

    def test_all_clues_against_independent_house_oracle(self):
        rng = Random(812)
        coverage = [set() for _ in range(15)]
        for _ in range(500):
            # Sin los genes fijos, para probar también 9, 10 y 15 en ambos sentidos.
            individual = tuple(tuple(rng.sample(range(5), 5)) for _ in range(5))
            for immediate in (False, True):
                expected = oracle(individual, immediate)
                self.assertEqual(ga.clue_status(individual, immediate), expected)
                self.assertEqual(ga.fitness(individual, immediate), sum(expected))
                self.assertEqual(ga.is_solution(individual, immediate), all(expected))
                for seen, status in zip(coverage, expected):
                    seen.add(status)
        for seen in coverage[1:]:
            self.assertEqual(seen, {True, False})

    def test_equality_and_neighbor_are_distinct(self):
        # HBase y JavaScript en la MISMA casa: no son vecinos (pista 11).
        individual = list(EXAMPLE)
        languages = list(individual[2])
        a, b = languages.index(individual[3][4]), 4
        languages[a], languages[b] = languages[b], languages[a]
        individual[2] = tuple(languages)
        self.assertFalse(ga.clue_status(tuple(individual))[10])
        self.assertEqual(oracle(tuple(individual)), ga.clue_status(tuple(individual)))

    def test_partial_never_answers_vim(self):
        partial = ga.random_individual(Random(7))
        self.assertFalse(ga.is_solution(partial))
        with self.assertRaises(ValueError):
            ga.vim_user(partial)


class OperatorTests(unittest.TestCase):
    def test_tournament_selects_best_sampled(self):
        rng = unittest.mock.Mock()
        rng.randrange.side_effect = [0, 2, 1]
        self.assertEqual(ga.tournament(["a", "b", "c", "d"], [1, 8, 3, 15], rng), "b")

    def test_order_crossover_expected_order(self):
        rng = unittest.mock.Mock()
        rng.sample.return_value = [1, 3]
        self.assertEqual(ga.order_crossover((0, 1, 2, 3, 4), (4, 3, 2, 1, 0), rng),
                         (3, 1, 2, 0, 4))

    def test_mutation_zero_and_one(self):
        self.assertEqual(ga.mutate(EXAMPLE, Random(4), 0), EXAMPLE)
        changed = ga.mutate(EXAMPLE, Random(4), 1)
        for before, after in zip(EXAMPLE, changed):
            self.assertEqual(sum(x != y for x, y in zip(before, after)), 2)
        self.assertNotEqual(changed, EXAMPLE)

    def test_operators_preserve_permutations_fixed_genes_and_parents(self):
        rng = Random(16)
        for _ in range(300):
            a, b = ga.random_individual(rng), ga.random_individual(rng)
            snapshot = tuple(tuple(row) for row in a), tuple(tuple(row) for row in b)
            crossed = ga.crossover(a, b, rng)
            mutated = ga.mutate(crossed, rng, 1)
            self.assertEqual((a, b), snapshot)
            for individual in (crossed, mutated):
                self.assertTrue(ga.well_formed(individual))
                for r, (gene, pos) in ga.FIXED.items():
                    self.assertEqual(individual[r][gene], pos)


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.config = ga.Config(population=8, elite=1, immigrants=1, max_seconds=1000)
        self.partial = ga.random_individual(Random(7))

    def test_solution_cutoff_and_priority(self):
        with patch("ga.random_individual", return_value=EXAMPLE):
            result = ga.solve(replace(self.config, max_generations=0, max_seconds=0))
        self.assertEqual(result.reason, "solucion")
        self.assertEqual(result.generation, 0)
        self.assertEqual(result.individual, EXAMPLE)

    def test_generation_cutoff(self):
        config = replace(self.config, max_generations=2, crossover_rate=0, mutation_rate=0)
        with patch("ga.random_individual", return_value=self.partial):
            result = ga.solve(config, clock=lambda: 0)
        self.assertEqual(result.reason, "generaciones")
        self.assertEqual(result.generation, 2)
        self.assertEqual(result.individual, self.partial)
        with patch("ga.random_individual", return_value=self.partial):
            result = ga.solve(replace(config, max_generations=0), clock=lambda: 0)
        self.assertEqual(result.generation, 0)

    def test_time_cutoff_zero_and_during_generation(self):
        with patch("ga.random_individual", return_value=self.partial):
            result = ga.solve(replace(self.config, max_seconds=0), clock=lambda: 0)
        self.assertEqual(result.reason, "tiempo")
        self.assertEqual(result.generation, 0)
        ticks = iter([0] * 9 + [2])  # inicio + ocho evaluaciones iniciales
        with patch("ga.random_individual", return_value=self.partial):
            result = ga.solve(replace(self.config, max_seconds=1), clock=lambda: next(ticks))
        self.assertEqual(result.reason, "tiempo")
        self.assertEqual(result.generation, 1)
        self.assertEqual(result.elapsed, 2)

    def test_fixed_seed_reproducibility_and_real_evolution(self):
        config = ga.Config(seed=42)
        first = ga.solve(config, clock=lambda: 0)
        second = ga.solve(config, clock=lambda: 0)
        self.assertEqual(first, second)
        self.assertGreater(first.generation, 0)
        self.assertEqual(first.reason, "solucion")
        self.assertTrue(all(oracle(first.individual)))

    def test_best_so_far_returned_on_limit(self):
        population = [ga.random_individual(Random(i)) for i in range(8)]
        with patch("ga.random_individual", side_effect=population):
            result = ga.solve(replace(self.config, max_generations=0), clock=lambda: 0)
        self.assertEqual(result.score, max(ga.fitness(x) for x in population))
        self.assertEqual(ga.fitness(result.individual), result.score)

    def test_restart_after_stagnation(self):
        config = replace(self.config, max_generations=3, restart_after=2,
                         crossover_rate=0, mutation_rate=0)
        with patch("ga.random_individual", return_value=self.partial) as generate:
            result = ga.solve(config, clock=lambda: 0)
        # 8 iniciales; 1 inmigrante en g1; 8 nuevos en g2; 1 inmigrante en g3.
        self.assertEqual(generate.call_count, 18)
        self.assertEqual(result.individual, self.partial)
        self.assertEqual(result.reason, "generaciones")

    def test_restart_keeps_global_best_even_if_new_population_is_worse(self):
        high = list(EXAMPLE)
        editors = list(high[4])
        editors[0], editors[4] = editors[4], editors[0]
        high[4] = tuple(editors)
        high = tuple(high)
        self.assertGreater(ga.fitness(high), ga.fitness(self.partial))
        self.assertFalse(ga.is_solution(high))
        config = replace(self.config, max_generations=3, restart_after=2,
                         crossover_rate=0, mutation_rate=0)
        with patch("ga.random_individual", side_effect=[high] + [self.partial] * 17):
            result = ga.solve(config, clock=lambda: 0)
        self.assertEqual(result.individual, high)
        self.assertEqual(result.score, ga.fitness(high))

    def test_output_matches_validator_for_solution_and_partial(self):
        for individual, reason in ((EXAMPLE, "solucion"), (self.partial, "generaciones")):
            result = ga.Result(individual, ga.fitness(individual), 0, 0, reason)
            output = ga.format_result(result, self.config)
            self.assertIn(f"{result.score}/15", output)
            for house in ga.houses(individual):
                for value in house:
                    self.assertIn(value, output)
            if ga.is_solution(individual):
                self.assertIn("En ESTA solución utiliza Vim: Matemático", output)
            else:
                self.assertIn("MEJOR SOLUCIÓN PARCIAL", output)
                self.assertNotIn("En ESTA solución utiliza Vim:", output)
                failed = ", ".join(str(i) for i, ok in enumerate(ga.clue_status(individual), 1) if not ok)
                self.assertIn(f"Pistas incumplidas: {failed}", output)

    def test_invalid_parameters(self):
        for changes in ({"population": 1}, {"max_generations": -1}, {"max_seconds": -1},
                        {"max_seconds": float("nan")}, {"max_seconds": float("inf")},
                        {"population": 8.2}, {"elite": 300}, {"immigrants": 298},
                        {"elite": -1}, {"immigrants": -1}, {"tournament_size": 0},
                        {"mutation_rate": 2}, {"crossover_rate": -0.1}, {"restart_after": 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(ga.Config(), **changes)

    def test_cli_success_and_partial_exit_codes(self):
        output = io.StringIO()
        with patch("sys.argv", ["ga.py", "--seed", "42"]), redirect_stdout(output):
            self.assertEqual(ga.main(), 0)
        self.assertIn("SOLUCIÓN COMPLETA", output.getvalue())
        with patch("sys.argv", ["ga.py", "--seconds", "0"]), redirect_stdout(io.StringIO()):
            self.assertEqual(ga.main(), 1)


class AmbiguityTests(unittest.TestCase):
    def test_exact_counts_vim_distribution_and_all_solutions_valid(self):
        for immediate, expected in (
            (False, {"Desarrollador": 12, "Hacker": 6, "Ingeniero": 1, "Matemático": 12}),
            (True, {"Desarrollador": 6, "Hacker": 2, "Ingeniero": 1, "Matemático": 5}),
        ):
            solutions, users = summary(immediate)
            self.assertEqual(dict(users), expected)
            self.assertEqual(len(solutions), sum(expected.values()))
            self.assertEqual(len(set(solutions)), len(solutions))
            for individual in solutions:
                self.assertTrue(ga.is_solution(individual, immediate))
                self.assertTrue(all(oracle(individual, immediate)))
        self.assertTrue(set(enumerate_solutions(True)) < set(enumerate_solutions(False)))


if __name__ == "__main__":
    unittest.main()
