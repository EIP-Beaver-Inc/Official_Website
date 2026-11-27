"""Du devis à la livraison (orders.py), avec la vraie API et une base en mémoire."""
import json

import pytest

QUOTE = {"nom": "Marie Martin", "entreprise": "Scierie du Lac", "email": "marie@lac.fr",
         "telephone": "0600000000", "taille_scierie": "PME", "volume": "200 planches/h", "message": "Bonjour"}


@pytest.fixture
def request_id(app_client):
    r = app_client.post("/api/demo-requests", json=QUOTE)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def release(app_client, version="2.1.0", content=b"MZ fake installer"):
    (app_client.releases / f"BeaverSetup-{version}.exe").write_bytes(content)


def linux_release(app_client, version="2.1.0", content=b"#!/usr/bin/env bash\n"):
    (app_client.releases / f"BeaverSetup-{version}-linux.run").write_bytes(content)


def test_admin_routes_need_the_admin_token(app_client, request_id):
    assert app_client.get("/api/admin/requests").status_code == 401
    assert app_client.get("/api/admin/requests", headers={"X-Admin-Token": "wrong"}).status_code == 401


def test_a_new_request_is_listed_as_new(app_client, request_id):
    rows = app_client.get("/api/admin/requests", headers=app_client.admin).json()
    assert [(r["id"], r["status"]) for r in rows] == [(request_id, "nouveau")]


def test_the_quote_is_emailed_to_the_customer(app_client, request_id, mails):
    r = app_client.post(f"/api/admin/requests/{request_id}/quote", headers=app_client.admin,
                        json={"amount_ht": 4500, "details": "Licence 1 an + installation", "validity_days": 15})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "devis_envoye"
    assert mails[-1]["to"] == "marie@lac.fr"
    body = " ".join(mails[-1]["paragraphs"])
    assert "4 500,00 € HT" in body and "Licence 1 an + installation" in body and "répondez" in body
    row = app_client.get("/api/admin/requests", headers=app_client.admin).json()[0]
    assert row["quote"]["amount_ht"] == 4500 and row["quote"]["email_status"] == "sent"


def test_delivery_sends_licence_access_key_and_download_link(app_client, request_id, mails, signing_key):
    release(app_client, "2.0.9")
    release(app_client, "2.1.0")
    r = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin,
                        json={"licence_expires": "2027-11-30", "seats": 2})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["status"] == "livre" and out["download"]["version"] == "2.1.0"

    mail = mails[-1]
    blocks = dict(mail["code_blocks"])
    assert list(blocks) == ["Votre clé de licence (à copier en entier)"], "une seule clé dans le mail"
    licence_key = blocks["Votre clé de licence (à copier en entier)"]
    assert licence_key == out["licence_key"] == out["access_key"]
    assert mail["button"][1].startswith("https://site.test/api/download/")
    assert "jusqu'au 30/11/2027" in " ".join(mail["paragraphs"])

    # The licence is the website's signed format, for the company.
    import base64
    prefix, payload, signature = licence_key.split(".")
    signing_key.public_key().verify(base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4)),
                                    f"{prefix}.{payload}".encode())
    data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    assert data["customer"] == "Scierie du Lac" and data["seats"] == 2

    # The link in the email downloads the newest installer, and is counted.
    token = mail["button"][1].rsplit("/", 1)[1]
    d = app_client.get(f"/api/download/{token}")
    assert d.status_code == 200 and d.content == b"MZ fake installer"
    assert "BeaverSetup-2.1.0.exe" in d.headers["content-disposition"]
    assert app_client.db.downloads.docs[0]["count"] == 1


def test_the_customer_space_shows_the_licence_and_downloads(app_client, request_id, mails):
    release(app_client)
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin,
                          json={"licence_expires": None}).json()
    # The access key from the email opens the customer space (existing beta flow).
    r = app_client.post("/api/beta/validate", json={"key": out["access_key"], "company": "Scierie du Lac",
                                                    "contact_name": "Marie Martin", "email": "marie@lac.fr"})
    assert r.status_code == 200, r.text
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    lic = app_client.get("/api/beta/licence", headers=auth).json()["licence"]
    assert lic["key"] == out["licence_key"] and lic["expires"] is None
    link = app_client.get("/api/beta/download", headers=auth).json()
    assert link["version"] == "2.1.0" and link["url"].startswith("https://site.test/api/download/")
    assert app_client.get("/api/beta/download").status_code == 401


def test_no_delivery_without_an_installer(app_client, request_id, mails):
    r = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    assert r.status_code == 503 and "installateur" in r.json()["detail"]
    assert mails == []


def test_no_delivery_without_the_signing_key(app_client, request_id, mails, monkeypatch):
    release(app_client)
    monkeypatch.delenv("LICENCE_PRIVATE_KEY")
    r = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    assert r.status_code == 503 and "LICENCE_PRIVATE_KEY" in r.json()["detail"]
    assert mails == []


def test_a_delivered_order_is_not_delivered_twice_but_can_be_resent(app_client, request_id, mails):
    release(app_client)
    first = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    again = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    assert again.status_code == 409
    resent = app_client.post(f"/api/admin/requests/{request_id}/resend", headers=app_client.admin)
    assert resent.status_code == 200
    assert dict(mails[-1]["code_blocks"])["Votre clé de licence (à copier en entier)"] == first["licence_key"]
    assert len(app_client.get("/api/admin/licences", headers=app_client.admin).json()) == 1


def test_an_expired_or_unknown_link(app_client, request_id, mails):
    release(app_client)
    app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    assert app_client.get("/api/download/nope").status_code == 404
    app_client.db.downloads.docs[0]["expires_at"] = "2000-01-01T00:00:00+00:00"
    token = app_client.db.downloads.docs[0]["token"]
    r = app_client.get(f"/api/download/{token}")
    assert r.status_code == 410 and "espace client" in r.json()["detail"]


def test_status_changes(app_client, request_id, mails):
    ok = app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin,
                         json={"status": "commande"})
    assert ok.status_code == 200
    bad = app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin,
                          json={"status": "livre"})
    assert bad.status_code == 400
    app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin, json={"status": "annule"})
    release(app_client)
    assert app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin,
                           json={}).status_code == 409


# ---- Livraison automatique à la confirmation de commande ----

def test_the_quote_states_the_licence_terms(app_client, request_id, mails):
    app_client.post(f"/api/admin/requests/{request_id}/quote", headers=app_client.admin,
                    json={"amount_ht": 900, "details": "x", "licence_months": 24, "seats": 3})
    assert "Licence : 2 ans, 3 postes." in mails[-1]["paragraphs"]


def test_confirming_the_order_delivers_it_with_the_quote_terms(app_client, request_id, mails, signing_key):
    from datetime import date

    from orders import add_months
    release(app_client)
    app_client.post(f"/api/admin/requests/{request_id}/quote", headers=app_client.admin,
                    json={"amount_ht": 900, "details": "x", "licence_months": 12, "seats": 2})
    r = app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin,
                        json={"status": "commande"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["delivered"] is True and out["status"] == "livre"

    mail = mails[-1]
    assert mail["to"] == "marie@lac.fr" and mail["subject"] == "Votre logiciel Beaver est prêt"
    blocks = dict(mail["code_blocks"])
    assert blocks == {"Votre clé de licence (à copier en entier)": out["licence_key"]}
    assert mail["button"][1].startswith("https://site.test/api/download/")
    expires = add_months(date.today(), 12)
    assert f"jusqu'au {expires:%d/%m/%Y}" in " ".join(mail["paragraphs"])
    row = app_client.get("/api/admin/requests", headers=app_client.admin).json()[0]
    assert row["status"] == "livre" and row["delivery"]["seats"] == 2


def test_an_unlimited_licence_from_the_quote(app_client, request_id, mails):
    release(app_client)
    app_client.post(f"/api/admin/requests/{request_id}/quote", headers=app_client.admin,
                    json={"amount_ht": 900, "details": "x", "licence_months": None, "seats": 1})
    out = app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin,
                          json={"status": "commande"}).json()
    assert out["delivered"] and "sans limite de durée" in " ".join(mails[-1]["paragraphs"])


def test_without_an_installer_the_order_waits_and_says_why(app_client, request_id, mails):
    r = app_client.post(f"/api/admin/requests/{request_id}/status", headers=app_client.admin,
                        json={"status": "commande"})
    out = r.json()
    assert r.status_code == 200 and out["delivered"] is False and "installateur" in out["delivery_error"]
    assert all(m["subject"] != "Votre logiciel Beaver est prêt" for m in mails)
    row = app_client.get("/api/admin/requests", headers=app_client.admin).json()[0]
    assert row["status"] == "commande" and "installateur" in row["delivery_error"]
    assert app_client.get("/api/admin/licences", headers=app_client.admin).json() == []

    # Once an installer is published, "Livrer" finishes the job and clears the error.
    release(app_client)
    r = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    assert r.status_code == 200, r.text
    row = app_client.get("/api/admin/requests", headers=app_client.admin).json()[0]
    assert row["status"] == "livre" and "delivery_error" not in row


def test_add_months_keeps_the_day_or_takes_the_last_one():
    from datetime import date

    from orders import add_months
    assert add_months(date(2026, 11, 24), 12) == date(2027, 11, 24)
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2027, 12, 15), 1) == date(2028, 1, 15)



# ---- Une seule clé : la licence ouvre aussi l'espace client ----

def test_the_licence_opens_the_customer_space_without_registering(app_client, request_id, mails):
    release(app_client)
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    licence = out["licence_key"]
    # Collée depuis un mail : libellé copié avec, retours à la ligne, espace insécable invisible.
    pasted = "Votre clé de licence : " + licence[:50] + "\n" + licence[50:] + "\u200b "
    r = app_client.post("/api/beta/login", json={"key": pasted})
    assert r.status_code == 200, r.text
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    me = app_client.get("/api/beta/me", headers=auth).json()
    assert me["company"] == "Scierie du Lac" and me["contact_name"] == "Marie Martin" and me["email"] == "marie@lac.fr"
    assert app_client.get("/api/beta/licence", headers=auth).json()["licence"]["key"] == licence
    # « Première connexion » avec la licence : connecte aussi, sans créer de second compte.
    r = app_client.post("/api/beta/validate", json={"key": licence, "company": "x", "contact_name": "y",
                                                     "email": "z@z.fr"})
    assert r.status_code == 200, r.text
    assert len(app_client.db.beta_clients.docs) == 1


def test_an_old_access_key_still_works(app_client):
    # Une clé d'accès livrée avant la clé unique (ou une clé beta), en minuscules à la saisie.
    app_client.db.beta_keys.docs.append({"id": "k1", "key": "ABCD-EFGH-IJKL-MNOP", "status": "unused",
                                         "company": "Ancienne", "expires_at": None, "used_at": None})
    r = app_client.post("/api/beta/validate", json={"key": "abcd-efgh-ijkl-mnop", "company": "Ancienne",
                                                     "contact_name": "A", "email": "a@a.fr"})
    assert r.status_code == 200, r.text
    assert app_client.post("/api/beta/login", json={"key": " abcd-efgh-ijkl-mnop "}).status_code == 200


def test_delivery_sends_a_link_for_windows_and_for_linux(app_client, request_id, mails):
    release(app_client, "2.1.0")
    linux_release(app_client, "2.0.9")
    linux_release(app_client, "2.1.0")
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    assert set(out["downloads"]) == {"windows", "linux"}
    assert out["download"] == out["downloads"]["windows"]

    mail = mails[-1]
    labels = [label for label, _ in mail["buttons"]]
    assert labels == ["Télécharger pour Windows (2.1.0)", "Télécharger pour Linux (2.1.0)"]
    text = " ".join(mail["paragraphs"])
    assert "bash BeaverSetup-2.1.0-linux.run" in text and "Windows : lancez BeaverSetup" in text
    assert "4. Au premier lancement" in text

    # Each button downloads its own installer, as what it is.
    linux_token = mail["buttons"][1][1].rsplit("/", 1)[1]
    d = app_client.get(f"/api/download/{linux_token}")
    assert d.status_code == 200 and d.content.startswith(b"#!/usr/bin/env bash")
    assert "BeaverSetup-2.1.0-linux.run" in d.headers["content-disposition"]
    assert d.headers["content-type"].startswith("application/x-sh")
    windows_token = mail["buttons"][0][1].rsplit("/", 1)[1]
    assert app_client.get(f"/api/download/{windows_token}").content == b"MZ fake installer"


def test_a_linux_installer_alone_is_delivered(app_client, request_id, mails):
    linux_release(app_client)
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    assert out["status"] == "livre" and list(out["downloads"]) == ["linux"]
    mail = mails[-1]
    assert [label for label, _ in mail["buttons"]] == ["Télécharger pour Linux (2.1.0)"]
    text = " ".join(mail["paragraphs"])
    assert "Windows : lancez" not in text and "2. Linux" in text and "3. Au premier lancement" in text


def test_a_replaced_linux_installer_is_still_served_by_an_old_link(app_client, request_id, mails):
    linux_release(app_client, "2.1.0")
    app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={})
    token = mails[-1]["buttons"][0][1].rsplit("/", 1)[1]
    (app_client.releases / "BeaverSetup-2.1.0-linux.run").unlink()
    release(app_client, "2.2.0")                       # a newer Windows one must not be served instead
    linux_release(app_client, "2.2.0", b"#!/usr/bin/env bash\n# 2.2.0\n")
    d = app_client.get(f"/api/download/{token}")
    assert d.status_code == 200 and "BeaverSetup-2.2.0-linux.run" in d.headers["content-disposition"]


def test_the_customer_space_downloads_either_installer(app_client, request_id, mails):
    release(app_client)
    linux_release(app_client)
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    r = app_client.post("/api/beta/validate", json={"key": out["access_key"], "company": "Scierie du Lac",
                                                    "contact_name": "Marie Martin", "email": "marie@lac.fr"})
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    assert app_client.get("/api/beta/download", headers=auth).json()["platform"] == "windows"
    linux = app_client.get("/api/beta/download?platform=linux", headers=auth).json()
    assert linux["platform"] == "linux" and linux["file"] == "BeaverSetup-2.1.0-linux.run"
    assert app_client.get("/api/beta/download?platform=mac", headers=auth).status_code == 400


def test_the_customer_space_says_when_the_linux_installer_is_missing(app_client, request_id, mails):
    release(app_client)
    out = app_client.post(f"/api/admin/requests/{request_id}/deliver", headers=app_client.admin, json={}).json()
    r = app_client.post("/api/beta/validate", json={"key": out["access_key"], "company": "Scierie du Lac",
                                                    "contact_name": "Marie Martin", "email": "marie@lac.fr"})
    auth = {"Authorization": f"Bearer {r.json()['session_token']}"}
    missing = app_client.get("/api/beta/download?platform=linux", headers=auth)
    assert missing.status_code == 503 and "Linux" in missing.json()["detail"]


def test_the_admin_sees_both_installers(app_client):
    release(app_client, "2.1.0")
    linux_release(app_client, "2.0.0")
    info = app_client.get("/api/admin/releases", headers=app_client.admin).json()
    assert info["installers"]["windows"]["file"] == "BeaverSetup-2.1.0.exe"
    assert info["installers"]["linux"]["version"] == "2.0.0"
    assert info["latest"]["version"] == "2.1.0"
