# plan.md — BEAVER Marketing Site (React + FastAPI + MongoDB)

## 1) Objectives
- Reproduire fidèlement la landing page BEAVER (look éditorial premium) d’après les captures.
- Implémenter un **Quiz EN 975-1** interactif (multi-écrans) avec scoring + explications.
- Mettre en place **FastAPI + MongoDB** pour persister : demandes de démo, messages contact, résultats quiz.
- Intégrer une **vidéo de démo pré-enregistrée** lue côté site (fichier dans le projet, placeholder au départ).

---

## 2) Implementation Steps

### Phase 1 — Core Flow POC (à faire d’abord)
Objectif: valider le cœur fonctionnel “quiz + persistence” et “forms + persistence” sans dépendre du design final.

**POC Backend (FastAPI)**
- Créer endpoints minimum :
  - `POST /api/quiz/submit` (reçoit answers, calcule score, sauvegarde `quiz_results`)
  - `POST /api/contact` (sauvegarde `contacts`)
  - `POST /api/demo-requests` (sauvegarde `demo_requests`)
  - `GET /api/quiz/questions` (retourne banque questions)
- Connexion MongoDB + models Pydantic + validation.

**POC Frontend (React)**
- Page simple `/quiz` : enchaînement questions → résultat (score + explications) → submit vers backend.
- Page simple `/contact` + modal/page “Demander une démo” → submit vers backend.
- Vérifier : erreurs API, loading states, confirmations.

**User stories (POC)**
1. En tant que visiteur, je peux répondre à un mini-quiz et obtenir un score immédiatement.
2. En tant que visiteur, je vois des explications sur mes réponses pour comprendre la norme.
3. En tant que visiteur, je peux envoyer un message via Contact et recevoir une confirmation.
4. En tant que visiteur, je peux demander une démo et recevoir une confirmation.
5. En tant qu’admin (tech), je peux vérifier dans MongoDB que les soumissions sont stockées.

**Exit criteria POC**
- Un parcours quiz complet fonctionne (questions → submit → résultat) + écriture DB.
- Contact + Demo request fonctionnent + écriture DB.

---

### Phase 2 — V1 App Development (Landing fidèle + pages)
Objectif: construire le site complet autour du core validé.

**Frontend (React + Tailwind + shadcn/ui)**
- Layout global : Header (logo + nav + CTA) / Footer.
- `/` Home fidèle captures:
  - Hero (badge “PIPELINE IA · TEMPS RÉEL”, H1, CTA, stats, carte image annotée)
  - Section 01 Pipeline (3 cards: ROI/BOBER/DefectTracker)
  - Section 02 Détection (grid 9 défauts)
  - Section 03 Démo vidéo (player HTML5, source locale)
  - Section 04 Backend/Score (explication courte + classes)
  - CTA final (Demander une démo)
- `/quiz` : flow multi-écrans (intro → type produit B/F/S/P → QCM 12–15 → résultats).
- `/contact` : formulaire complet.
- Modal/page “Demander une démo” accessible depuis CTA header + CTA final.
- Thème design: couleurs + fonts (serif éditorial titres, sans body), spacing, hover/animations légères.

**Backend (FastAPI)**
- Structurer modules: `routes/`, `schemas.py`, `db.py`, `data/quiz_questions.py`, `data/defects.py`.
- Ajouter endpoints utiles:
  - `GET /api/defects`
  - `POST /api/quiz/start` (optionnel: session id)
- Seed optionnel (questions) ou questions codées côté backend.

**Données Quiz EN 975-1**
- Implémenter 12–15 QCM avec catégories: types produits, dimensions, classes qualité, défauts admissibles.
- Chaque question contient: `options`, `correct_answer`, `explanation`.

**User stories (V1)**
1. En tant que visiteur, je comprends l’offre en <10s via le hero et les sections pipeline/défauts.
2. En tant que visiteur, je peux regarder une vidéo de démo directement sur la landing.
3. En tant que visiteur, je peux démarrer le quiz, progresser par étapes et terminer sans friction.
4. En tant que visiteur, je peux laisser mon email (optionnel) avec mon résultat de quiz.
5. En tant que prospect, je peux demander une démo depuis n’importe quelle page via le CTA.

**Fin de phase (obligatoire)**
- 1 passe de tests E2E (navigation, quiz complet, envois formulaires, affichage confirmations).

---

### Phase 3 — Durcissement & Qualité (itérations)
- Ajustements pixel-perfect (typos/tailles/espacements) pour coller aux captures.
- Responsiveness (mobile/tablet) + accessibilité (focus, labels, contrastes).
- Ajout page “Merci”/toasts, gestion erreurs réseau, retries légers.
- Optionnel: endpoints `GET` admin (protégés par env token simple) pour lister soumissions.

**User stories (Qualité)**
1. En tant qu’utilisateur mobile, je peux lire et scroller sans layout cassé.
2. En tant que visiteur, je vois des messages d’erreur clairs si le backend est indisponible.
3. En tant que visiteur, je peux reprendre le quiz si j’ai refresh (local state).
4. En tant que prospect, je peux soumettre les formulaires en moins de 30s.
5. En tant qu’admin, je peux exporter/lister les résultats quiz (simple endpoint).

**Fin de phase**
- 1 passe de tests E2E complète + corrections jusqu’à stabilité.

---

## 3) Next Actions
- Confirmer/recevoir le **fichier vidéo** (mp4) + nom souhaité (ex: `demo.mp4`).
- Valider la banque de questions (12–15) : si tu as un PDF/notes EN 975-1 à suivre, les fournir.
- Lancer Phase 1 (POC) : backend endpoints + quiz minimal + persistance.

---

## 4) Success Criteria
- Landing `/` visuellement fidèle (couleurs/typos/sections) + responsive.
- Quiz `/quiz` complet: 12–15 questions, score final, explications, sauvegarde MongoDB.
- Formulaires Contact + Demande de démo: validation + sauvegarde MongoDB + confirmation UX.
- Vidéo de démo lue correctement sur `/` (HTML5 player, fallback si fichier absent).
- Tests E2E passent sur: navigation, quiz, formulaires, états loading/erreur.
