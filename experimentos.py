"""Ejecuta diez semillas en cada interpretación, sin guardar archivos."""

from ga import Config, is_solution, solve, vim_user


def main():
    for immediate in (False, True):
        print(f"\nDerecha: {'inmediata' if immediate else 'posición mayor'}")
        print("Semilla | Corte | Generación | Fitness | Segundos | Usuario de Vim")
        results = []
        for seed in range(10):
            config = Config(seed=seed, immediate=immediate)
            result = solve(config)
            valid = is_solution(result.individual, immediate)
            user = vim_user(result.individual, immediate) if valid else "sin respuesta válida"
            print(f"{seed} | {result.reason} | {result.generation} | {result.score}/15 | {result.elapsed:.3f} | {user}", flush=True)
            results.append(valid)
        print(f"Éxito observado: {sum(results)}/{len(results)} ({sum(results)/len(results):.0%})")
    print("La tasa observada no garantiza convergencia para otras semillas o presupuestos.")


if __name__ == "__main__":
    main()
