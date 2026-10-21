from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experimentos.comum.legado import exp4


if __name__ == "__main__":
    exp4()
