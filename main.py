# -*- coding: utf-8 -*-
# Entry point — gercek kod reymen/sistem/main.py icinde
import os, sys

_proje_kok = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _proje_kok)

if __name__ == "__main__":
    # CLI modu: runpy ile __main__ olarak calistir (interaktif dongu baslar)
    # reymen/sistem/main.py, sys.stdout/stderr'i yeniden TextIOWrapper'a sariyor.
    # run_path altinda eski wrapper GC olunca shared buffer kapaniyor.
    # Referansi burada tutarak GC'yi engelliyoruz.
    _stdout_ref = sys.stdout
    _stderr_ref = sys.stderr

    import runpy
    runpy.run_path(
        os.path.join(_proje_kok, "reymen", "sistem", "main.py"),
        run_name="__main__",
    )
else:
    # Modul modu: importlib ile modul olarak yukle (testler icin)
    # Bu mod __name__ == "__main__" blogunu CALISTIRMAZ.
    import importlib.util as _iu
    _modul_yolu = os.path.join(_proje_kok, "reymen", "sistem", "main.py")
    _modul_adi = "_reymen_sistem_main"
    if _modul_adi not in sys.modules:
        _spec = _iu.spec_from_file_location(_modul_adi, _modul_yolu)
        _mod = _iu.module_from_spec(_spec)
        sys.modules[_modul_adi] = _mod
        _spec.loader.exec_module(_mod)
    else:
        _mod = sys.modules[_modul_adi]
    # Tum isimleri bu modul'un namespace'ine kopyala
    for _k, _v in vars(_mod).items():
        if not _k.startswith("__"):
            globals()[_k] = _v
