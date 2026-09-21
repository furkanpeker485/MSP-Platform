#!/usr/bin/env python3
"""Demo kasası — kiracı ayrışmasını göstermek için asgari sır deposu.

Gerçek kurulumda burada HashiCorp Vault durur. Demoda önemli olan davranış şudur:
sır yolu her zaman `tenants/<kiracı>/...` altındadır ve bir kiracı için çalışan iş
başka kiracının alanını isterse kasa 403 döner. Bu, platform kodundaki
`app/integrations/vault.py` içindeki CrossTenantAccess kuralının ağ üzerindeki karşılığıdır.
"""
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STORE: dict[str, dict] = {}
PATH_RE = re.compile(r"^/v1/secret/data/tenants/(?P<tenant>[a-z0-9-]+)/(?P<key>.+)$")


class Handler(BaseHTTPRequestHandler):
    server_version = "msp-demo-vault/1.0"

    def _json(self, code: int, body: dict) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _tenant_guard(self):
        """İstek başlığındaki kiracı ile yoldaki kiracı aynı olmak zorunda."""
        m = PATH_RE.match(self.path)
        if not m:
            self._json(400, {"hata": "gecersiz yol"})
            return None
        caller = self.headers.get("X-Hisar-Tenant", "")
        if caller and caller != m["tenant"]:
            self._json(403, {
                "hata": "kiraci sinirini asan erisim",
                "isteyen": caller, "istenen": m["tenant"],
            })
            return None
        return m

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            return self._json(200, {"durum": "ok", "kayit": len(STORE)})
        m = self._tenant_guard()
        if not m:
            return
        key = f"{m['tenant']}/{m['key']}"
        if key not in STORE:
            return self._json(404, {"hata": "kasada yok", "anahtar": key})
        self._json(200, {"data": {"data": STORE[key]}})

    def do_POST(self) -> None:  # noqa: N802
        m = self._tenant_guard()
        if not m:
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        key = f"{m['tenant']}/{m['key']}"
        STORE[key] = payload.get("data", payload)
        self._json(200, {"yazildi": key, "kasa": STORE[key].get("store")})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[kasa] {fmt % args}", flush=True)


if __name__ == "__main__":
    print("[kasa] 0.0.0.0:8200 dinleniyor", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8200), Handler).serve_forever()
