# -*- coding: utf-8 -*-
# SHIM — reymen/arac/cua_motor_araci.py yonlendirir
from reymen.arac.cua_motor_araci import *  # noqa: F401, F403
# Private API'ler (alt cizgi ile baslayan isimler * ile ihrac edilmez)
from reymen.arac.cua_motor_araci import (  # noqa: F401
    _config_yukle,
    _on_kosul_kontrol,
    _on_kosul_kontrolu_yapildi,
    _on_kosul_sonuc,
)

# patch("cua_motor_araci.BytesIO") ile test edebilmek için
from io import BytesIO  # noqa: F401
import base64 as _base64
import gc as _gc


def goruntu_base64_yap(goruntu, max_genislik: int = 1280) -> str:
    """PIL görüntüsünü Base64 JPEG'e dönüştür — BytesIO bu modülden alınır (patchlenebilir)."""
    try:
        from PIL import Image
        if goruntu.width > max_genislik:
            oran = max_genislik / goruntu.width
            yeni_boyut = (max_genislik, int(goruntu.height * oran))
            goruntu = goruntu.resize(yeni_boyut, Image.LANCZOS)
    except Exception:
        pass
    tampon = BytesIO()
    goruntu.save(tampon, format="JPEG", quality=85)
    b64 = _base64.b64encode(tampon.getvalue()).decode("utf-8")
    tampon.close()
    _gc.collect()
    return b64
