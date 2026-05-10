{
  "brand": {
    "name": "BEAVER",
    "personality": [
      "éditorial premium",
      "calme et rigoureux",
      "industriel (bois) mais sophistiqué",
      "B2B confiance / norme EN 975-1",
      "beaucoup d'espace, hiérarchie magazine"
    ],
    "language": "fr-FR",
    "no_dark_mode": true,
    "no_webgl": true
  },

  "design_tokens": {
    "color_system_hsl": {
      "notes": "Tokens HSL à copier dans :root (index.css) et/ou Tailwind config. Objectif: fond cream-vert très pâle + cards cream chaudes + accent rouge brique terreux.",
      "core": {
        "background": "120 33% 94%",
        "foreground": "0 0% 7%",

        "card": "38 45% 96%",
        "card_foreground": "0 0% 7%",

        "popover": "38 45% 96%",
        "popover_foreground": "0 0% 7%",

        "primary": "10 60% 40%",
        "primary_foreground": "38 45% 96%",

        "secondary": "120 18% 90%",
        "secondary_foreground": "0 0% 10%",

        "muted": "120 16% 91%",
        "muted_foreground": "0 0% 38%",

        "accent": "120 22% 90%",
        "accent_foreground": "0 0% 10%",

        "destructive": "0 72% 52%",
        "destructive_foreground": "0 0% 98%",

        "border": "40 18% 86%",
        "input": "40 18% 86%",
        "ring": "10 60% 40%"
      },
      "brand_extras": {
        "mint_canvas": "120 33% 94%",
        "cream_card": "38 45% 96%",
        "cream_card_2": "36 35% 93%",
        "ink": "0 0% 7%",
        "ink_soft": "0 0% 18%",
        "brick": "10 60% 40%",
        "brick_hover": "10 62% 36%",
        "brick_soft_bg": "10 55% 92%",
        "sage_line": "120 12% 82%",
        "metric_gray": "0 0% 45%"
      },
      "chart_suggestion": {
        "chart_1": "10 60% 40%",
        "chart_2": "120 28% 34%",
        "chart_3": "35 35% 45%",
        "chart_4": "190 28% 34%",
        "chart_5": "0 0% 25%"
      },
      "tailwind_mapping_hint": {
        "bg": "bg-[hsl(var(--background))]",
        "text": "text-[hsl(var(--foreground))]",
        "cta": "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
        "card": "bg-[hsl(var(--card))]"
      }
    },

    "gradients_and_texture": {
      "rule": "Respecter la GRADIENT RESTRICTION RULE: gradients uniquement décoratifs, max 20% viewport, jamais sur zones de lecture.",
      "allowed_background_gradient": {
        "usage": "Uniquement en hero (fond), très subtil.",
        "css": "background: radial-gradient(900px 500px at 15% 10%, hsla(120, 35%, 92%, 0.9) 0%, transparent 60%), radial-gradient(700px 420px at 85% 20%, hsla(38, 55%, 94%, 0.9) 0%, transparent 55%), linear-gradient(180deg, hsl(120 33% 94%) 0%, hsl(120 28% 93%) 100%);"
      },
      "noise_overlay": {
        "usage": "Overlay très léger sur sections clés (hero + CTA final).",
        "css": "background-image: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.9%22 numOctaves=%222%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22120%22 height=%22120%22 filter=%22url(%23n)%22 opacity=%220.06%22/%3E%3C/svg%3E');"
      }
    },

    "typography": {
      "google_fonts": {
        "heading_serif": {
          "family": "Fraunces",
          "why": "Serif éditorial premium avec italiques expressives (proche esprit Canela/GT Super), excellente dispo Google Fonts.",
          "weights": ["300", "400", "600"],
          "italics": true,
          "use_for": ["H1/H2/H3", "chiffres stats (italique)", "mots accentués en italique"]
        },
        "body_sans": {
          "family": "Manrope",
          "why": "Sans moderne, technique, très lisible pour B2B industriel; contraste élégant avec Fraunces.",
          "weights": ["400", "500", "600", "700"],
          "italics": false,
          "use_for": ["body", "nav", "labels", "UI"]
        }
      },
      "css_font_vars": {
        "--font-heading": "'Fraunces', ui-serif, Georgia, serif",
        "--font-body": "'Manrope', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
      },
      "type_scale_tailwind": {
        "h1": "font-[var(--font-heading)] text-4xl sm:text-5xl lg:text-6xl leading-[1.02] tracking-[-0.02em]",
        "h2": "font-[var(--font-heading)] text-3xl sm:text-4xl leading-[1.08] tracking-[-0.015em]",
        "h3": "font-[var(--font-heading)] text-2xl sm:text-3xl leading-[1.12] tracking-[-0.01em]",
        "body": "font-[var(--font-body)] text-sm sm:text-base leading-[1.65] text-[hsl(var(--foreground))]",
        "lead": "font-[var(--font-body)] text-base sm:text-lg leading-[1.6] text-[hsl(var(--muted-foreground))]",
        "label_caps": "font-[var(--font-body)] text-xs tracking-[0.18em] uppercase text-[hsl(var(--muted-foreground))]",
        "meta": "font-[var(--font-body)] text-xs tracking-[0.14em] uppercase"
      },
      "inline_highlight": {
        "pattern": "Dans les paragraphes, mettre en valeur 1-2 mots max en italique serif + brick.",
        "class": "font-[var(--font-heading)] italic text-[hsl(var(--primary))]"
      }
    },

    "spacing_grid": {
      "container": {
        "max_width": "max-w-6xl",
        "padding": "px-4 sm:px-6 lg:px-8"
      },
      "section_spacing": {
        "y": "py-14 sm:py-18 lg:py-24",
        "gap": "gap-8 sm:gap-10 lg:gap-14"
      },
      "card_padding": "p-5 sm:p-6 lg:p-7",
      "editorial_rhythm": "Toujours 2–3x plus d'espace que 'confortable'. Préférer des blocs courts + respirations (Separator)."
    },

    "radius_shadow_border": {
      "radius": {
        "base": "rounded-xl",
        "card": "rounded-2xl",
        "pill": "rounded-full",
        "media": "rounded-3xl"
      },
      "border": {
        "style": "border border-[hsl(var(--border))]",
        "hairline": "border border-black/5"
      },
      "shadow": {
        "card": "shadow-[0_10px_30px_rgba(17,17,17,0.06)]",
        "hover": "hover:shadow-[0_16px_44px_rgba(17,17,17,0.10)]",
        "soft": "shadow-[0_1px_0_rgba(17,17,17,0.06)]"
      }
    },

    "motion": {
      "principles": [
        "Subtil, éditorial: pas de bounce.",
        "Durées 180–260ms, easing doux.",
        "Pas de transition: all (interdit)."
      ],
      "durations": {
        "fast": "duration-150",
        "base": "duration-200",
        "slow": "duration-300"
      },
      "easing": {
        "standard": "ease-out",
        "emphasis": "[cubic-bezier(0.16,1,0.3,1)]"
      },
      "hover_lift": "transition-shadow duration-200 ease-out hover:-translate-y-0.5 (ajouter transition-transform uniquement sur l'élément concerné)",
      "fade_up_on_scroll": {
        "implementation": "CSS + IntersectionObserver (pas de lib). Ajouter data-animate='fade-up' sur sections/cards.",
        "classes": {
          "initial": "opacity-0 translate-y-3",
          "entered": "opacity-100 translate-y-0"
        },
        "transition": "transition-opacity duration-300 ease-out transition-transform duration-300 ease-out"
      },
      "dot_pulse": {
        "css": "@keyframes beaver-pulse {0%{transform:scale(1);opacity:.9} 70%{transform:scale(1.8);opacity:0} 100%{transform:scale(1.8);opacity:0}}",
        "usage": "Dans badge live: un point plein + un pseudo-élément animé (ring)."
      }
    },

    "accessibility": {
      "focus": {
        "rule": "Focus visible partout.",
        "class": "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--background))]"
      },
      "contrast": "Texte #111 sur fond cream OK. Sur brick, utiliser primary-foreground cream. Éviter texte gris trop clair.",
      "reduced_motion": "Respecter prefers-reduced-motion: désactiver fade-up et pulse si activé."
    }
  },

  "component_path": {
    "shadcn_primary": [
      "/app/frontend/src/components/ui/button.jsx",
      "/app/frontend/src/components/ui/badge.jsx",
      "/app/frontend/src/components/ui/card.jsx",
      "/app/frontend/src/components/ui/dialog.jsx",
      "/app/frontend/src/components/ui/input.jsx",
      "/app/frontend/src/components/ui/textarea.jsx",
      "/app/frontend/src/components/ui/label.jsx",
      "/app/frontend/src/components/ui/progress.jsx",
      "/app/frontend/src/components/ui/radio-group.jsx",
      "/app/frontend/src/components/ui/separator.jsx",
      "/app/frontend/src/components/ui/sheet.jsx",
      "/app/frontend/src/components/ui/sonner.jsx"
    ],
    "icons": {
      "library": "lucide-react",
      "examples": ["ArrowRight", "ShieldCheck", "Scan", "Layers", "Video", "Factory", "BadgeCheck"]
    }
  },

  "components_spec": {
    "pill_cta_with_arrow": {
      "base": "Button (shadcn)",
      "variants": {
        "primary": "rounded-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] px-5 sm:px-6 h-11 sm:h-12 text-sm sm:text-base font-semibold transition-colors duration-200 hover:bg-[hsl(10_62%_36%)]",
        "secondary_outline": "rounded-full border border-[hsl(var(--border))] bg-transparent text-[hsl(var(--foreground))] px-5 sm:px-6 h-11 sm:h-12 transition-colors duration-200 hover:bg-[hsl(var(--secondary))]"
      },
      "arrow_icon": "<ArrowRight className='ml-2 h-4 w-4' />",
      "data_testid": {
        "primary": "primary-cta-button",
        "secondary": "secondary-cta-button"
      }
    },

    "badge_pill_with_dot_pulse": {
      "base": "Badge (shadcn)",
      "class": "rounded-full bg-[hsl(var(--card))] text-[hsl(var(--foreground))] border border-black/5 px-3 py-1 text-xs tracking-[0.12em] uppercase",
      "dot": {
        "structure": "span.dot + span.dotPulse",
        "dot_class": "inline-block h-2 w-2 rounded-full bg-[hsl(var(--primary))]",
        "pulse_class": "relative -ml-2 inline-block h-2 w-2 rounded-full bg-[hsl(var(--primary))] after:content-[''] after:absolute after:inset-0 after:rounded-full after:bg-[hsl(var(--primary))] after:animate-[beaver-pulse_1.4s_ease-out_infinite]"
      },
      "data_testid": "live-pipeline-badge"
    },

    "numbered_editorial_card": {
      "base": "Card (shadcn)",
      "layout": "En-tête: numéro (01) très grand + icône coin haut droit; sous-titre ALLCAPS brick; titre serif; body.",
      "classes": {
        "card": "rounded-2xl bg-[hsl(var(--card))] border border-black/5 shadow-[0_10px_30px_rgba(17,17,17,0.06)] transition-shadow duration-200 hover:shadow-[0_16px_44px_rgba(17,17,17,0.10)]",
        "inner": "p-6",
        "number": "font-[var(--font-heading)] italic text-[hsl(var(--primary))] text-4xl",
        "kicker": "mt-3 text-xs tracking-[0.18em] uppercase text-[hsl(var(--primary))]",
        "title": "mt-2 font-[var(--font-heading)] text-2xl leading-[1.1]",
        "desc": "mt-3 text-sm leading-[1.7] text-[hsl(var(--muted-foreground))]"
      },
      "data_testid": "pipeline-step-card"
    },

    "stats_inline": {
      "layout": "Ligne de 3 stats: label ALLCAPS + chiffre énorme serif italique brick.",
      "classes": {
        "wrap": "grid grid-cols-3 gap-4 sm:gap-6",
        "label": "text-xs tracking-[0.18em] uppercase text-[hsl(var(--muted-foreground))]",
        "value": "mt-1 font-[var(--font-heading)] italic text-[hsl(var(--primary))] text-4xl sm:text-5xl leading-none"
      },
      "data_testid": "hero-stats"
    },

    "section_header_with_step": {
      "pattern": "À gauche: '01 · PIPELINE' en label caps; à droite: titre serif + phrase courte.",
      "classes": {
        "kicker": "text-xs tracking-[0.22em] uppercase text-[hsl(var(--muted-foreground))]",
        "kicker_em": "text-[hsl(var(--primary))]",
        "title": "mt-3 font-[var(--font-heading)] text-3xl sm:text-4xl leading-[1.08]",
        "subtitle": "mt-3 max-w-2xl text-sm sm:text-base leading-[1.7] text-[hsl(var(--muted-foreground))]"
      },
      "data_testid": "section-header"
    },

    "hero_image_card_with_annotations": {
      "layout": "Card media à droite (desktop): image scierie + overlays défauts (chips translucides brick) + footer metrics.",
      "classes": {
        "card": "relative overflow-hidden rounded-3xl bg-[hsl(var(--card))] border border-black/5 shadow-[0_16px_50px_rgba(17,17,17,0.10)]",
        "img": "aspect-[4/3] w-full object-cover",
        "chip": "absolute rounded-full bg-[hsla(10,60%,40%,0.14)] text-[hsl(var(--primary))] border border-[hsla(10,60%,40%,0.25)] px-3 py-1 text-xs font-semibold backdrop-blur-sm",
        "footer": "flex items-center justify-between gap-3 border-t border-black/5 bg-[hsla(38,45%,96%,0.85)] backdrop-blur-sm p-4"
      },
      "metrics": {
        "left": "TRACK #2471",
        "middle": "SCORE 82/100",
        "right": "CLASSE Standard"
      },
      "data_testid": "hero-annotated-media"
    }
  },

  "page_guidelines": {
    "home": {
      "header": {
        "layout": "Barre haute sticky légère (pas opaque): logo castor + wordmark à gauche; nav minimal; CTA brick à droite.",
        "classes": "sticky top-0 z-50 backdrop-blur-md bg-[hsla(120,33%,94%,0.75)] border-b border-black/5",
        "nav": "Liens: Accueil, Quiz · EN 975-1, Contact. Hover: underline hairline + légère variation couleur.",
        "logo": {
          "url": "https://customer-assets.emergentagent.com/job_b42adf92-a9e6-4bb5-a663-a3501b832c94/artifacts/w80li2v9_zqsedrghj.png",
          "treatment": "Logo 28–32px, aligné baseline avec wordmark 'Beaver'."
        },
        "data_testid": {
          "header": "site-header",
          "nav": "site-nav",
          "demo": "header-request-demo-button"
        }
      },

      "hero": {
        "layout": "2 colonnes desktop: gauche texte + CTAs + stats; droite media card annotée. Mobile: empiler (texte puis media).",
        "composition": [
          "Badge live pill (dot pulse)",
          "H1 serif très grand avec 1 mot en italique brick",
          "Lead paragraph",
          "2 CTAs (primary filled brick + secondary outline)",
          "Stats inline (3 items)"
        ],
        "animation": "Fade-up sur badge, H1, CTAs, stats; media card fade-up + léger delay.",
        "data_testid": "home-hero"
      },

      "pipeline_section": {
        "header": "01 · PIPELINE",
        "layout": "Grille 3 cards numérotées (01 ROI MobileNetV3, 02 BOBER YOLOv8, 03 DefectTracker).",
        "cards": "Numbered editorial card.",
        "micro": "Hover lift discret + shadow.",
        "data_testid": "home-pipeline"
      },

      "defects_section": {
        "header": "02 · DÉFAUTS",
        "layout": "Grille 3 colonnes desktop / 2 tablette / 1 mobile. 9 items (classes EN 975-1).",
        "item_style": "Petites cards cream, titre serif, meta caps (ex: 'CLASSE').",
        "data_testid": "home-defects"
      },

      "video_demo_section": {
        "header": "03 · DÉMO VIDÉO",
        "layout": "Bloc media large (aspect-ratio) dans card arrondie; à côté (desktop) bullets techniques.",
        "player": "HTML5 <video controls> avec poster. Encadrer dans Card + border hairline.",
        "data_testid": "home-video"
      },

      "backend_score_section": {
        "header": "04 · CLASSEMENT",
        "layout": "2 colonnes: gauche explication (C++ pipeline, scoring), droite cards 'Premium / Standard / Economy / Reject' en stack.",
        "cards": "Cards simples avec badge brick soft + titre serif.",
        "data_testid": "home-scoring"
      },

      "final_cta_section": {
        "layout": "Section courte, fond légèrement différent (secondary) + noise overlay léger. Titre serif + 1 phrase + CTA pill.",
        "data_testid": "home-final-cta"
      },

      "footer": {
        "layout": "Minimal: logo + 2-3 liens + mention. Pas de gradient.",
        "data_testid": "site-footer"
      }
    },

    "quiz": {
      "flow": ["Intro", "QCM multi-step (5 étapes)", "Résultats + débrief"],
      "layout": {
        "page": "Fond mint canvas. Container max-w-5xl.",
        "top_bar": "À gauche: badge échantillon (ÉCHANTILLON · CHÊNE · OAK-001). À droite: label caps 'ESSENCE VERROUILLÉE'.",
        "progress": "Affichage '1 / 5' + Progress (shadcn) brick. Sur mobile: progress full width sous top bar.",
        "main": "Image bois (Card media) + Card question numérotée (01 / Type de produit / 4 familles normatives).",
        "answers": "RadioGroup (shadcn) en grille 2x2 desktop, 1 colonne mobile. Chaque option: lettre énorme serif italique brick (B/F/S/P) + description + specs caps en bas.",
        "nav": "Boutons Précédent (outline) / Suivant (brick) alignés à droite; sur mobile: full width stack."
      },
      "result_screen": {
        "score": "Grand score serif italique brick + label caps 'RÉSULTAT'.",
        "explanation": "Bloc débrief: 3 bullets (Pourquoi, Norme, Reco).",
        "cta": "CTA 'Demander une démo' + lien 'Recommencer le quiz'."
      },
      "data_testid": {
        "page": "quiz-page",
        "progress": "quiz-progress",
        "question": "quiz-question-card",
        "answer": "quiz-answer-option",
        "next": "quiz-next-button",
        "prev": "quiz-prev-button",
        "result": "quiz-result"
      }
    },

    "contact": {
      "layout": "Formulaire dans Card large + aside (coordonnées / promesse).",
      "fields": ["Nom", "Entreprise", "Email", "Téléphone", "Message"],
      "components": "Input, Textarea, Label, Button, Sonner toast.",
      "data_testid": {
        "page": "contact-page",
        "form": "contact-form",
        "submit": "contact-form-submit-button"
      }
    },

    "demo_modal": {
      "component": "Dialog (shadcn)",
      "layout": "DialogContent large, 2 colonnes desktop: formulaire court + encart 'Ce que vous recevez'.",
      "data_testid": {
        "open": "open-demo-dialog-button",
        "dialog": "demo-dialog",
        "submit": "demo-request-submit-button"
      }
    }
  },

  "responsive_rules": {
    "hero": {
      "mobile": "Empiler: badge + H1 + lead + CTAs (stack) + stats (2 colonnes puis 3) + media card.",
      "desktop": "Grid 12 colonnes: texte span 6-7, media span 5-6."
    },
    "quiz": {
      "mobile": "Progress full width; options en 1 colonne; boutons full width; image bois au-dessus de la question.",
      "desktop": "Image à gauche, question à droite; options 2x2."
    }
  },

  "image_urls": {
    "logo": [
      {
        "category": "brand",
        "description": "Logo castor low-poly fourni",
        "url": "https://customer-assets.emergentagent.com/job_b42adf92-a9e6-4bb5-a663-a3501b832c94/artifacts/w80li2v9_zqsedrghj.png"
      }
    ],
    "hero": [
      {
        "category": "hero-media",
        "description": "Photo scierie / ligne de sciage (à annoter avec overlays défauts)",
        "url": "https://images.unsplash.com/photo-1597008641621-cefdcf7187d5?auto=format&fit=crop&w=1600&q=80"
      }
    ],
    "quiz": [
      {
        "category": "quiz-sample",
        "description": "Texture bois chêne (planche macro) pour écran quiz",
        "url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=1600&q=80"
      }
    ],
    "video_poster": [
      {
        "category": "video",
        "description": "Poster vidéo démo (industrie bois / scierie)",
        "url": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=1600&q=80"
      }
    ]
  },

  "libraries": {
    "required": [],
    "optional": [
      {
        "name": "IntersectionObserver (native)",
        "why": "Fade-up on scroll sans dépendance.",
        "install": "Aucune",
        "usage": "Créer un hook useInViewFadeUp.js et appliquer data-animate='fade-up'."
      }
    ]
  },

  "instructions_to_main_agent": [
    "Mettre à jour /app/frontend/src/index.css : remplacer les variables :root par les HSL ci-dessus (pas de dark mode utilisé).",
    "Importer Google Fonts Fraunces + Manrope dans index.html (ou via CSS @import) et définir --font-heading/--font-body.",
    "Ne pas utiliser App.css centré; supprimer/ignorer styles CRA par défaut. Utiliser Tailwind pour layout.",
    "Créer des composants React .js (pas .tsx) pour: Header, Hero, PipelineCards, DefectsGrid, VideoSection, ScoringSection, FinalCTA, Footer.",
    "Tous les boutons/inputs/liens/options quiz doivent avoir data-testid en kebab-case.",
    "Animations: implémenter fade-up via IntersectionObserver + classes (pas de lib). Respecter prefers-reduced-motion.",
    "Quiz: utiliser Progress + RadioGroup shadcn; conserver l'esthétique éditoriale (kickers caps, chiffres italiques brick).",
    "Respecter la règle gradients: uniquement hero décoratif, jamais sur zones de lecture, max 20% viewport."
  ],

  "appendix_general_ui_ux_design_guidelines": "<General UI UX Design Guidelines>  \n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
