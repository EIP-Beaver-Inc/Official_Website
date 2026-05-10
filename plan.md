# plan.md — BEAVER Marketing Site (React + FastAPI + MongoDB)

## 1) Objectives
- ✅ Reproduire fidèlement la landing page BEAVER (look éditorial premium) d’après les captures (cream-vert, accent brick, typo serif/sans).
- ✅ Implémenter un **Quiz EN 975-1** interactif (multi-écrans) avec scoring + explications.
- ✅ Mettre en place **FastAPI + MongoDB** pour persister : demandes de démo, messages contact, résultats quiz.
- ✅ Intégrer une **vidéo de démo pré-enregistrée** lue côté site (HTML5 player) avec **fallback** en attendant le mp4 final.
- 🎯 Objectif actuel : stabilisation, itérations de polish, et préparation à la livraison (assets finaux, éventuelle page admin).

---

## 2) Implementation Steps

### Phase 1 — Core Flow POC (à faire d’abord)
> **Statut : complété** (le POC a été absorbé par la V1, endpoints et flows sont en production).

**POC Backend (FastAPI)**
- ✅ Endpoints quiz + persistence (submit + results) en place.
- ✅ Endpoints contact + demo-requests en place.
- ✅ Connexion MongoDB + validation Pydantic.

**POC Frontend (React)**
- ✅ Parcours quiz fonctionnel.
- ✅ Formulaire contact + demande de démo (Dialog) fonctionnels.

**Exit criteria POC**
- ✅ Quiz complet fonctionne (questions → submit → résultat) + écriture DB.
- ✅ Contact + Demo request fonctionnent + écriture DB.

---

### Phase 2 — V1 App Development (Landing fidèle + pages)
> **Statut : complété et testé**

**Frontend (React + Tailwind + shadcn/ui)**
- ✅ Layout global : Header (logo + nav + CTA “Demander une démo” + burger mobile) / Footer.
- ✅ `/` Home fidèle captures:
  - ✅ Hero (badge “PIPELINE IA · TEMPS RÉEL”, H1 éditorial, CTAs, stats, carte image annotée)
  - ✅ Section 01 Pipeline (3 cards: ROI/BOBER/DefectTracker)
  - ✅ Section 02 Détection (grid 9 défauts)
  - ✅ Section 03 Démo vidéo (player HTML5, source locale + fallback)
  - ✅ Section 04 Backend/Score (classes Premium/Standard/Economy/Reject)
  - ✅ CTA final (Demander une démo + Contact)
- ✅ `/quiz` : flow interactif complet (intro + panel B/F/S/P → 15 QCM → écran email optionnel → résultats + débrief question par question).
- ✅ `/contact` : formulaire complet + aside infos.
- ✅ Modal “Demander une démo” accessible depuis Header, CTA final, et résultats quiz.
- ✅ Thème design final : Fraunces (serif) + Manrope (sans), tokens HSL, micro-animations (fade-up scroll + dot pulse), responsive.

**Backend (FastAPI + MongoDB)**
- ✅ Endpoints implémentés et validés :
  - ✅ `GET /api/health`
  - ✅ `GET /api/pipeline`, `GET /api/defects`, `GET /api/scoring`
  - ✅ `GET /api/quiz/questions`
  - ✅ `POST /api/quiz/submit` (+ validations)
  - ✅ `GET /api/quiz/results`
  - ✅ `POST /api/contact` (+ validations), `GET /api/contact`
  - ✅ `POST /api/demo-requests` (+ validations), `GET /api/demo-requests`
- ✅ Collections MongoDB utilisées : `quiz_results`, `contacts`, `demo_requests`.

**Données Quiz EN 975-1**
- ✅ 15 questions (types de produit B/F/S/P, classes qualité, défauts, dimensionnel, pipeline BEAVER) avec :
  - ✅ options
  - ✅ bonne réponse
  - ✅ explication affichée au débrief

**Fin de phase (obligatoire)**
- ✅ Tests E2E passés avec succès :
  - ✅ Backend : **16/16** checks/validations endpoints
  - ✅ Frontend : **10/10** user stories

---

### Phase 3 — Durcissement & Qualité (itérations)
> **Statut : prêt pour itérations futures (optionnel / selon demande)**

- 🔜 Remplacer le placeholder vidéo par la vidéo finale :
  - Déposer le fichier en `frontend/public/demo.mp4` (le player le prendra automatiquement via `/demo.mp4`).
- 🔜 Pixel-perfect / polish : ajustements typo/espaces sur retours client.
- 🔜 SEO : meta tags par page (title/description/OG), sitemap, robots.txt.
- 🔜 Analytics (optionnel) : ajout d’un outil (PostHog/GA) si requis.
- 🔜 Page admin (optionnel) :
  - Listing des `demo_requests`, `contacts`, `quiz_results`
  - Protection via token simple (env) ou auth légère.
- 🔜 i18n (optionnel) : si besoin d’une version EN/ES.

**User stories (Qualité / optionnel)**
1. En tant qu’utilisateur mobile, je peux lire et scroller sans layout cassé. ✅ (déjà validé)
2. En tant que visiteur, je vois des messages d’erreur clairs si le backend est indisponible. (à renforcer si souhaité)
3. En tant que visiteur, je peux reprendre le quiz si j’ai refresh (local state). (optionnel)
4. En tant que prospect, je peux soumettre les formulaires en moins de 30s. ✅
5. En tant qu’admin, je peux lister/exporter les leads et résultats quiz. (optionnel)

**Fin de phase**
- 🔜 Nouvelle passe E2E après ajout des options ci-dessus.

---

## 3) Next Actions
- Fournir le **fichier vidéo final** (mp4) et le déposer dans : `frontend/public/demo.mp4`.
- (Optionnel) Confirmer si besoin d’une **page admin** (listing leads + résultats quiz) et le niveau de protection (token env vs auth).
- (Optionnel) Confirmer besoins **SEO/analytics**.

---

## 4) Success Criteria
- ✅ Landing `/` visuellement fidèle (couleurs/typos/sections) + responsive.
- ✅ Quiz `/quiz` complet (15 questions) : score final, explications, sauvegarde MongoDB.
- ✅ Formulaires Contact + Demande de démo : validation + sauvegarde MongoDB + confirmations UX.
- ✅ Vidéo de démo lue correctement sur `/` (HTML5 player, fallback si fichier absent).
- ✅ Tests E2E passent : backend **16/16**, frontend **10/10** user stories.
- 🔜 Vidéo mp4 finale intégrée (remplacement placeholder).
