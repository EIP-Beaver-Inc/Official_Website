import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Download, BookOpen, MessageSquare, CheckCircle } from 'lucide-react';

const DOWNLOAD_URL = '#';

const STEPS = [
    {
        title: '1. Télécharger l\'application',
        description: 'Cliquez sur le bouton ci-dessus pour télécharger le binaire Beaver. Compatible Windows 10/11 (x64).',
    },
    {
        title: '2. Installer et lancer',
        description: 'Décompressez l\'archive et lancez Beaver.exe. Aucune installation requise.',
    },
    {
        title: '3. Connecter votre caméra',
        description: 'Branchez votre caméra IP ou USB. L\'application détecte automatiquement les flux RTSP et USB.',
    },
    {
        title: '4. Calibrer et tester',
        description: 'Suivez l\'assistant de calibration, puis passez vos premières planches sous l\'objectif.',
    },
    {
        title: '5. Envoyer vos retours',
        description: 'À la fin de la bêta, exportez les logs et la base de données locale depuis le menu Fichier, et envoyez-les à beaver.eip@gmail.com.',
    },
];

export default function BetaDownload() {
    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem('beaver_beta_token');
        if (!token) {
            navigate('/beta', { replace: true });
        }
    }, [navigate]);

    return (
        <section className="max-w-3xl mx-auto px-4 sm:px-6 py-12 sm:py-20">
            <div data-animate="fade-up">
                <div className="label-caps">
                    <span className="text-[hsl(var(--primary))]">Bienvenue</span> · Accès beta confirmé
                </div>
                <h1 className="mt-3 font-heading text-4xl sm:text-5xl leading-[1.04] tracking-[-0.02em]">
                    Télécharger <span className="brick-italic">Beaver</span>
                </h1>
                <p className="mt-5 text-[hsl(var(--muted-foreground))] leading-[1.7]">
                    Votre accès beta est activé. Téléchargez l'application et suivez les étapes ci-dessous pour commencer vos tests.
                </p>
            </div>

            <div data-animate="fade-up" className="mt-8 flex flex-col sm:flex-row gap-3">
                <a
                    href={DOWNLOAD_URL}
                    className="inline-flex items-center justify-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-7 h-13 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                    style={{ height: '3.25rem' }}
                >
                    <Download className="h-4 w-4" />
                    Télécharger Beaver (Windows x64)
                </a>
                <a
                    href="mailto:beaver.eip@gmail.com"
                    className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 bg-transparent hover:bg-[hsl(var(--card))] text-[hsl(var(--foreground))] px-7 text-sm font-medium transition-colors"
                    style={{ height: '3.25rem' }}
                >
                    <MessageSquare className="h-4 w-4" />
                    Contacter l'équipe
                </a>
            </div>

            <div data-animate="fade-up" className="mt-12">
                <div className="flex items-center gap-2 mb-5">
                    <BookOpen className="h-4 w-4 text-[hsl(var(--primary))]" />
                    <span className="label-caps">Guide de démarrage rapide</span>
                </div>
                <div className="space-y-3">
                    {STEPS.map((step) => (
                        <div
                            key={step.title}
                            className="flex gap-4 rounded-xl border border-black/5 bg-[hsl(var(--card))] p-4 sm:p-5"
                        >
                            <CheckCircle className="h-5 w-5 mt-0.5 shrink-0 text-[hsl(var(--primary)/0.5)]" />
                            <div>
                                <div className="font-medium text-sm">{step.title}</div>
                                <div className="mt-1 text-sm text-[hsl(var(--muted-foreground))] leading-[1.65]">
                                    {step.description}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div
                data-animate="fade-up"
                className="mt-8 rounded-2xl border border-black/5 bg-[hsl(38_45%_94%)] p-6"
            >
                <div className="label-caps mb-3">À la fin de la bêta</div>
                <p className="text-sm text-[hsl(var(--muted-foreground))] leading-[1.7]">
                    Merci de nous envoyer à{' '}
                    <a href="mailto:beaver.eip@gmail.com" className="text-[hsl(var(--primary))] underline underline-offset-4">
                        beaver.eip@gmail.com
                    </a>{' '}
                    : le formulaire de retour UX, la base de données locale (menu Fichier → Exporter), et les logs d'erreur (menu Aide → Logs). Ces données nous aident à améliorer l'application.
                </p>
            </div>
        </section>
    );
}
