"""Executa os experimentos exploratórios 1 a 5 na ordem histórica."""
from experimentos.comum.legado import exp1, exp2, exp3, exp4, exp5


if __name__ == "__main__":
    for experimento in (exp1, exp2, exp3, exp4, exp5):
        experimento()
