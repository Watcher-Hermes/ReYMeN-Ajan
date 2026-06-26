# -*- coding: utf-8 -*-
"""
test_cache_manager.py — cache_manager.py testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/core/test_cache_manager.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(os.path.abspath(__file__)).parent.parent.parent
sys.path.insert(0, str(ROOT))

PASS = 0
FAIL = 0
SKIP = 0


def test(ad, aciklama, fn):
    global PASS, FAIL, SKIP
    try:
        r = fn()
        if r == "SKIP":
            SKIP += 1
            print(f"  SKIP | {ad} - {aciklama}")
        elif r:
            PASS += 1
            print(f"  PASS | {ad} - {aciklama}")
        else:
            FAIL += 1
            print(f"  FAIL | {ad} - {aciklama}")
    except Exception as e:
        FAIL += 1
        print(f"  FAIL | {ad} - {aciklama}: {e}")


def main():
    global PASS, FAIL, SKIP
    print("=" * 60)
    print("ReYMeN - CacheManager Testleri")
    print("=" * 60)

    # ── 1. Temel Islemler ─────────────────────────────────────────
    print("\n[1] CacheManager — kurulum")
    def t1():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60, maxsize=100)
        return c._ttl == 60 and c._maxsize == 100
    test("CacheManager", "__init__ with params", t1)

    def t2():
        from reymen.core import CacheManager
        c = CacheManager()
        return c._ttl == 60 and c._maxsize == 1000
    test("CacheManager", "__init__ defaults", t2)

    # ── 2. Temel CRUD ────────────────────────────────────────────
    print("\n[2] Temel CRUD")
    def t3():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("anahtar", 42)
        return c.get("anahtar") == 42
    test("CacheManager.set/get", "basic set and get", t3)

    def t4():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("anahtar", "deger")
        val = c.get("anahtar")
        return val == "deger"
    test("CacheManager.set/get", "string value", t4)

    def t5():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        d = {"x": [1, 2, 3], "y": None}
        c.set("dict", d)
        return c.get("dict") == d
    test("CacheManager.set/get", "dict value", t5)

    def t6():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("x", 1)
        c.set("y", 2)
        return c.get("x") == 1 and c.get("y") == 2
    test("CacheManager.multi", "multiple keys", t6)

    # ── 3. Eksik / Expired ──────────────────────────────────────
    print("\n[3] Eksik / Expired")
    def t7():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        return c.get("olmayan") is None
    test("CacheManager.get", "missing key returns None", t7)

    def t8():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        return c.get("olmayan", "varsayilan") == "varsayilan"
    test("CacheManager.get", "default value for missing key", t8)

    def t9():
        from reymen.core import CacheManager
        c = CacheManager(ttl=0.01)
        c.set("exp", "deger")
        import time
        time.sleep(0.02)
        return c.get("exp") is None
    test("CacheManager.ttl", "expired key returns None", t9)

    # ── 4. Delete / Clear ────────────────────────────────────────
    print("\n[4] Delete / Clear")
    def t10():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("x", 42)
        deleted = c.delete("x")
        return deleted and c.get("x") is None
    test("CacheManager.delete", "delete existing key", t10)

    def t11():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        deleted = c.delete("olmayan")
        return deleted is False
    test("CacheManager.delete", "delete missing key returns False", t11)

    def t12():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        return c.get("a") is None and c.get("b") is None and c.size == 0
    test("CacheManager.clear", "clear all entries", t12)

    # ── 5. Size / Keys / Stats ──────────────────────────────────
    print("\n[5] Size / Keys / Stats")
    def t13():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        return c.size == 0
    test("CacheManager.size", "empty cache", t13)

    def t14():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("a", 1)
        c.set("b", 2)
        return c.size == 2
    test("CacheManager.size", "two entries", t14)

    def t15():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("a", 1)
        c.set("b", 2)
        keys = c.keys()
        return "a" in keys and "b" in keys and len(keys) == 2
    test("CacheManager.keys", "list non-expired keys", t15)

    def t16():
        from reymen.core import CacheManager
        c = CacheManager(ttl=0.01)
        c.set("exp", "x")
        import time
        time.sleep(0.02)
        keys = c.keys()
        return "exp" not in keys
    test("CacheManager.keys", "expired keys excluded", t16)

    def t17():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60, maxsize=500)
        c.set("a", 1)
        s = c.stats()
        return s["size"] == 1 and s["maxsize"] == 500 and s["ttl"] == 60
    test("CacheManager.stats", "usage statistics", t17)

    # ── 6. LRU Eviction ──────────────────────────────────────────
    print("\n[6] LRU Eviction")
    def t18():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60, maxsize=3)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        c.set("d", 4)  # should evict "a"
        return c.get("a") is None and c.get("d") == 4 and c.size == 3
    test("CacheManager.evict", "evicts oldest when over maxsize", t18)

    def t19():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60, maxsize=2)
        c.set("a", 1)
        c.set("b", 2)
        c.get("a")  # touch "a"
        c.set("c", 3)  # should evict "b" (oldest), not "a"
        return c.get("a") == 1 and c.get("b") is None and c.get("c") == 3
    test("CacheManager.evict", "LRU order preserved by get", t19)

    def t20():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60, maxsize=0)
        for i in range(100):
            c.set(f"k{i}", i)
        return c.size == 100  # unlimited
    test("CacheManager.evict", "maxsize=0 means unlimited", t20)

    # ── 7. Per-key TTL ────────────────────────────────────────────
    print("\n[7] Per-key TTL")
    def t21():
        from reymen.core import CacheManager
        import time
        c = CacheManager(ttl=60)
        c.set("short", "x", ttl=0.01)
        c.set("long", "y", ttl=60)
        time.sleep(0.02)
        return c.get("short") is None and c.get("long") == "y"
    test("CacheManager.ttl", "per-key TTL override", t21)

    def t22():
        from reymen.core import CacheManager
        c = CacheManager(ttl=60)
        c.set("never", "x", ttl=0)
        return c.get("never") == "x"
    test("CacheManager.ttl", "ttl=0 means no expiry", t22)

    # ── 8. _clean_expired ───────────────────────────────────────
    print("\n[8] _clean_expired")
    def t23():
        from reymen.core import CacheManager
        import time
        c = CacheManager(ttl=0.01)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3, ttl=60)
        time.sleep(0.02)
        removed = c._clean_expired()
        return removed == 2 and c.size == 1
    test("CacheManager._clean_expired", "removes expired entries", t23)

    # ── 9. global_cache ─────────────────────────────────────────
    print("\n[9] global_cache")
    def t24():
        from reymen.core import global_cache
        global_cache.clear()
        global_cache.set("gkey", "gvalue")
        return global_cache.get("gkey") == "gvalue"
    test("global_cache", "set and get", t24)

    def t25():
        from reymen.core import global_cache
        global_cache.clear()
        global_cache.set("gk", 99)
        return global_cache.get("gk") == 99 and global_cache.size == 1
    test("global_cache", "size after set", t25)

    # ── 10. @cached decorator ───────────────────────────────────
    print("\n[10] @cached decorator")
    def t26():
        from reymen.core import cached
        @cached(ttl=60)
        def square(x):
            return x * x
        return square(3) == 9 and square(3) == 9
    test("@cached", "basic caching", t26)

    def t27():
        from reymen.core import cached
        call_count = [0]
        @cached(ttl=60)
        def expensive(x):
            call_count[0] += 1
            return x * 2
        expensive(5)
        expensive(5)
        return call_count[0] == 1  # only first call should invoke function
    test("@cached", "function called only once per args", t27)

    def t28():
        from reymen.core import cached
        @cached(ttl=60)
        def add(a, b):
            return a + b
        return add(1, 2) == 3 and add(3, 4) == 7
    test("@cached", "multiple arg sets", t28)

    def t29():
        from reymen.core import cached
        @cached(ttl=60)
        def kw_func(a, b=10):
            return a + b
        r1 = kw_func(5)
        r2 = kw_func(5, b=20)
        return r1 == 15 and r2 == 25
    test("@cached", "kwargs work", t29)

    def t30():
        from reymen.core import cached
        @cached(ttl=60)
        def f(x):
            return x * x
        f(3)
        info = f.cache_info()
        return info["size"] == 1
    test("@cached.cache_info", "reports size", t30)

    def t31():
        from reymen.core import cached
        @cached(ttl=60)
        def f(x):
            return x * x
        f(3)
        f.cache_clear()
        info = f.cache_info()
        return info["size"] == 0
    test("@cached.cache_clear", "clears cache", t31)

    # ── 11. Thread safety (basic) ──────────────────────────────
    print("\n[11] Thread safety")
    def t32():
        from reymen.core import CacheManager
        import threading
        c = CacheManager(ttl=60)
        errors = []
        def worker(n):
            try:
                for i in range(20):
                    c.set(f"k{n}_{i}", n * i)
                    r = c.get(f"k{n}_{i}")
                    if r != n * i:
                        errors.append(f"mismatch at {n}_{i}")
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=worker, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return len(errors) == 0
    test("CacheManager", "thread safety (5 threads x 20 ops)", t32)

    def t33():
        from reymen.core import CacheManager
        import threading
        c = CacheManager(ttl=60, maxsize=5)
        errors = []
        def writer(n):
            try:
                for i in range(100):
                    c.set(f"k{n}_{i}", i)
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=writer, args=(t,)) for t in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return len(errors) == 0
    test("CacheManager", "thread safety with eviction (3 threads x 100)", t33)

    # ── 12. str / repr ─────────────────────────────────────────
    print("\n[12] String representation")
    def t34():
        from reymen.core import CacheManager
        c = CacheManager(ttl=30, maxsize=200)
        s = str(c)
        return "CacheManager" in s and "30" in s and "200" in s
    test("CacheManager.__str__", "contains class name and params", t34)

    def t35():
        from reymen.core import CacheManager
        c = CacheManager(ttl=30, maxsize=200)
        r = repr(c)
        return "CacheManager" in r and "30" in r
    test("CacheManager.__repr__", "contains class name", t35)

    # ── Rapor ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    total = PASS + FAIL + SKIP
    print(f"SONUC: {PASS}/{total} PASS, {FAIL} FAIL, {SKIP} SKIP")
    print("=" * 60)
    return FAIL == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
