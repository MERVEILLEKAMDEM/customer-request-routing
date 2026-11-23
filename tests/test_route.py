import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from route import MODELE, router  # noqa: E402


@pytest.mark.skipif(not MODELE.exists(), reason="lancer d'abord python src/train.py")
def test_fraude_prioritaire():
    r = router("Quelqu'un a utilisé ma carte sur internet, je ne reconnais pas l'achat")
    assert r["categorie"] == "fraude"
    assert r["priorite"].startswith("P1")
