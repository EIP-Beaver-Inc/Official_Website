"""Admin CLI for BETA licenses (spec section 7). No public admin API exists.

Usage (inside the backend container):
    python -m beta_license.cli beta-keys create --label "Prénom Nom" [--count N] [--days 14] [--max-machines 2]
    python -m beta_license.cli beta-keys list | show <id> | revoke <id> [--reason ..] | extend <id> --days N
    python -m beta_license.cli beta-keys reset-machines <id>
    python -m beta_license.cli beta-release register --platform windows --version 1.2.3 --file ./Beaver-beta.zip
    python -m beta_license.cli beta-release list
    python -m beta_license.cli beta-crypto gen-signing-key [--kid 2026-11] | gen-model-key --id beta-1
    python -m beta_license.cli beta-crypto test-vector [--out ../docs/beta/test-vector.json]
    python -m beta_license.cli beta-db init
Shortcuts: bin/beta-keys, bin/beta-release, bin/beta-crypto, bin/beta-db.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import csv
import json
import os
import sys
from datetime import datetime
from typing import Optional

from . import admin, storage
from .config import ConfigError, load_config
from .crypto import generate_model_key, generate_signing_key, private_key_b64, public_key_b64
from .status import as_utc


def _fmt(dt: Optional[datetime]) -> str:
    return as_utc(dt).strftime("%Y-%m-%d %H:%M") if dt else "-"


def _db():
    from motor.motor_asyncio import AsyncIOMotorClient

    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    except ImportError:  # pragma: no cover
        pass
    if not os.environ.get("MONGO_URL") or not os.environ.get("DB_NAME"):
        sys.exit("MONGO_URL and DB_NAME must be set")
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    return client, client[os.environ["DB_NAME"]]


def _config():
    try:
        return load_config()
    except ConfigError as exc:
        sys.exit(f"BETA configuration error: {exc}")


def _table(rows, headers):
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    print("  ".join(str(h).ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(r, widths)))


# ---------------------------------------------------------------- beta-keys
async def cmd_keys(args) -> None:
    client, db = _db()
    try:
        await storage.ensure_indexes(db)
        if args.action == "create":
            config = _config()
            created = await admin.create_keys(db, config, label=args.label, count=args.count, days=args.days,
                                              max_machines=args.max_machines, max_downloads=args.max_downloads,
                                              redeem_days=args.redeem_days)
            print("\n!! Plaintext keys are shown ONLY NOW. Only their hash is stored: copy them. !!\n")
            _table([(c["key"], c["id"][:8], c["label"], _fmt(c["redeem_by"])) for c in created],
                   ["KEY", "ID", "LABEL", "REDEEM BY"])
            if args.csv:
                fd = os.open(args.csv, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "w", newline="") as fh:
                    w = csv.writer(fh)
                    w.writerow(["key", "id", "label", "redeem_by", "duration_days", "max_machines"])
                    for c in created:
                        w.writerow([c["key"], c["id"], c["label"], as_utc(c["redeem_by"]).isoformat(),
                                    c["duration_days"], c["max_machines"]])
                print(f"\nCSV written to {args.csv} (contains plaintext keys: send it, then delete it).")
        elif args.action == "list":
            rows = await admin.list_keys(db)
            _table([(r["id"][:8], r["key_hint"], r["label"][:30], r["status"], _fmt(r["activated_at"]),
                     _fmt(r["expires_at"]), f'{r["machines"]}/{r["max_machines"]}',
                     f'{r.get("download_count", 0)}/{r["max_downloads"]}', _fmt(r["last_seen_at"])) for r in rows],
                   ["ID", "HINT", "LABEL", "STATUS", "ACTIVATED", "EXPIRES", "MACHINES", "DOWNLOADS", "LAST SEEN"])
        elif args.action == "show":
            info = await admin.show_key(db, args.id)
            k = info["key"]
            for field in ("id", "key_hint", "label", "status", "created_at", "redeem_by", "activated_at",
                          "expires_at", "duration_days", "max_machines", "max_downloads", "download_count",
                          "revoked", "revoked_at", "revoke_reason"):
                v = k.get(field)
                print(f"{field:15} {_fmt(v) if isinstance(v, datetime) else v}")
            print("\nMachines:")
            _table([(m["machine_hash"][:16] + "…", m.get("platform"), m.get("app_version"), _fmt(m["first_seen_at"]),
                     _fmt(m["last_seen_at"]), m.get("last_ip_truncated")) for m in info["machines"]],
                   ["MACHINE", "PLATFORM", "VERSION", "FIRST SEEN", "LAST SEEN", "IP"])
            print("\nLast events:")
            _table([(_fmt(e["at"]), e["type"], e.get("ip_truncated") or "-",
                     json.dumps(e.get("details") or {}, ensure_ascii=False)) for e in info["events"]],
                   ["AT", "TYPE", "IP", "DETAILS"])
        elif args.action == "revoke":
            k = await admin.revoke_key(db, args.id, args.reason)
            print(f"Key {k['id']} (…{k['key_hint']}) revoked.")
        elif args.action == "extend":
            k = await admin.extend_key(db, args.id, args.days)
            field = "expires_at" if k.get("activated_at") else "redeem_by"
            print(f"Key {k['id']} (…{k['key_hint']}): {field} is now {_fmt(k[field])} UTC.")
        elif args.action == "reset-machines":
            n = await admin.reset_machines(db, args.id)
            print(f"{n} machine(s) removed.")
    except admin.AdminError as exc:
        sys.exit(f"error: {exc}")
    finally:
        client.close()


# ---------------------------------------------------------------- beta-release
async def cmd_release(args) -> None:
    client, db = _db()
    try:
        await storage.ensure_indexes(db)
        if args.action == "register":
            rel = await admin.register_release(db, _config(), platform=args.platform, version=args.version,
                                               file_path=args.file)
            print(f"Release {rel['platform']} {rel['version']} active.\n  file   {rel['filename']}\n"
                  f"  size   {rel['size']} bytes\n  sha256 {rel['sha256']}")
        else:
            _table([(r["platform"], r["version"], r["filename"], r["size"], r["sha256"][:16] + "…",
                     "yes" if r["is_active"] else "", _fmt(r["created_at"])) for r in await admin.list_releases(db)],
                   ["PLATFORM", "VERSION", "FILE", "SIZE", "SHA256", "ACTIVE", "CREATED"])
    except admin.AdminError as exc:
        sys.exit(f"error: {exc}")
    finally:
        client.close()


# ---------------------------------------------------------------- beta-crypto
def cmd_crypto(args) -> None:
    if args.action == "gen-signing-key":
        sk = generate_signing_key()
        kid = args.kid or datetime.utcnow().strftime("%Y-%m")
        print("# Server .env (SECRET, never commit):")
        print(f"BETA_SIGNING_PRIVATE_KEY={private_key_b64(sk)}")
        print(f"BETA_SIGNING_KID={kid}")
        print("\n# Software repo, pinned public key (not secret):")
        print(f"kid={kid}")
        print(f"public_key_b64={public_key_b64(sk)}")
        print(f"public_key_hex={base64.b64decode(public_key_b64(sk)).hex()}")
    elif args.action == "gen-model-key":
        key = generate_model_key()
        b64 = base64.b64encode(key).decode()
        print("# Add to BETA_MODEL_KEYS in the server .env (SECRET, never commit), e.g.:")
        print(f"BETA_MODEL_KEYS={json.dumps({args.id: b64})}")
        print("\n# Pass to the software repo's model encryption script (SECRET, do not commit there either):")
        print(f"key_id={args.id}")
        print(f"key_b64={b64}")
        print(f"key_hex={key.hex()}")
    elif args.action == "gen-pepper":
        import secrets

        print(f"BETA_KEY_PEPPER={secrets.token_urlsafe(48)}")
    elif args.action == "test-vector":
        from .testvector import build_test_vector, dumps

        text = dumps(build_test_vector())
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"Test vector written to {args.out}")
        else:
            sys.stdout.write(text)


async def cmd_db(args) -> None:
    client, db = _db()
    try:
        await storage.ensure_indexes(db)
        print("BETA license indexes are up to date.")
    finally:
        client.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="beta_license.cli", description="Beaver BETA license administration")
    groups = p.add_subparsers(dest="group", required=True)

    keys = groups.add_parser("beta-keys").add_subparsers(dest="action", required=True)
    c = keys.add_parser("create", help="create keys (plaintext shown once)")
    c.add_argument("--label", required=True)
    c.add_argument("--count", type=int, default=1)
    c.add_argument("--days", type=int, help="validity after first activation (default BETA_DURATION_DAYS)")
    c.add_argument("--max-machines", type=int)
    c.add_argument("--max-downloads", type=int)
    c.add_argument("--redeem-days", type=int, help="days to activate (default BETA_REDEEM_WINDOW_DAYS)")
    c.add_argument("--csv", help="also export the plaintext keys to this NEW csv file")
    keys.add_parser("list")
    for name in ("show", "reset-machines"):
        keys.add_parser(name).add_argument("id", help="full id, id prefix (>= 6) or 4-char hint")
    r = keys.add_parser("revoke")
    r.add_argument("id")
    r.add_argument("--reason")
    e = keys.add_parser("extend", help="activated: push expires_at; never activated: push redeem_by")
    e.add_argument("id")
    e.add_argument("--days", type=int, required=True)

    rel = groups.add_parser("beta-release").add_subparsers(dest="action", required=True)
    reg = rel.add_parser("register")
    reg.add_argument("--platform", required=True, choices=admin.PLATFORMS)
    reg.add_argument("--version", required=True)
    reg.add_argument("--file", required=True)
    rel.add_parser("list")

    cr = groups.add_parser("beta-crypto").add_subparsers(dest="action", required=True)
    cr.add_parser("gen-signing-key").add_argument("--kid")
    cr.add_parser("gen-model-key").add_argument("--id", required=True)
    cr.add_parser("gen-pepper")
    cr.add_parser("test-vector").add_argument("--out")

    groups.add_parser("beta-db").add_subparsers(dest="action", required=True).add_parser("init")
    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    if args.group == "beta-keys":
        asyncio.run(cmd_keys(args))
    elif args.group == "beta-release":
        asyncio.run(cmd_release(args))
    elif args.group == "beta-crypto":
        cmd_crypto(args)
    else:
        asyncio.run(cmd_db(args))


if __name__ == "__main__":
    main()
