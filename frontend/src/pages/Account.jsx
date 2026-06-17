import { useEffect, useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Download, BookOpen, MessageSquare, LogOut, Loader2,
    ChevronDown, ChevronRight, Clock, CheckCircle, Send,
    Ticket, ArrowRight,
} from 'lucide-react';
import { toast } from 'sonner';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { fetchBetaMe, fetchTutorials, listMyTickets, submitFeedback } from '@/lib/api';

const FEEDBACK_CATEGORIES = ['Interface', 'Performance', 'Précision IA', 'Documentation', 'Autre'];

const DOWNLOAD_URL = '#';
const APP_VERSION = '0.1.0-beta';

const CATEGORY_COLORS = {
    'Démarrage': 'bg-green-100 text-green-700',
    'Configuration': 'bg-blue-100 text-blue-700',
    'Utilisation': 'bg-purple-100 text-purple-700',
    'Bêta': 'bg-amber-100 text-amber-700',
};

function TutorialCard({ tutorial }) {
    const [open, setOpen] = useState(false);
    const [openStep, setOpenStep] = useState(null);
    const colorClass = CATEGORY_COLORS[tutorial.category] ?? 'bg-gray-100 text-gray-600';

    return (
        <div className="rounded-xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
            <button
                onClick={() => setOpen((v) => !v)}
                className="w-full flex items-start justify-between gap-4 p-5 text-left hover:bg-black/[0.02] transition-colors"
            >
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${colorClass}`}>
                            {tutorial.category}
                        </span>
                        <span className="inline-flex items-center gap-1 text-[11px] text-[hsl(var(--muted-foreground))]">
                            <Clock className="h-3 w-3" />
                            {tutorial.duration}
                        </span>
                    </div>
                    <div className="font-medium text-sm">{tutorial.title}</div>
                    <div className="mt-1 text-[13px] text-[hsl(var(--muted-foreground))] leading-snug">
                        {tutorial.description}
                    </div>
                </div>
                <span className="shrink-0 mt-0.5 text-[hsl(var(--muted-foreground))]">
                    {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </span>
            </button>

            {open && (
                <div className="border-t border-black/5 divide-y divide-black/5">
                    {tutorial.steps.map((step, i) => (
                        <div key={i}>
                            <button
                                onClick={() => setOpenStep(openStep === i ? null : i)}
                                className="w-full flex items-center gap-3 px-5 py-3.5 text-left hover:bg-black/[0.02] transition-colors"
                            >
                                <span className="shrink-0 inline-flex h-5 w-5 items-center justify-center rounded-full bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary))] text-[11px] font-semibold">
                                    {i + 1}
                                </span>
                                <span className="text-sm font-medium">{step.title}</span>
                                <span className="ml-auto text-[hsl(var(--muted-foreground))]">
                                    {openStep === i
                                        ? <ChevronDown className="h-3.5 w-3.5" />
                                        : <ChevronRight className="h-3.5 w-3.5" />}
                                </span>
                            </button>
                            {openStep === i && (
                                <div className="px-5 pb-4 ml-8 text-sm text-[hsl(var(--muted-foreground))] leading-[1.7]">
                                    {step.content}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

const FAQ = [
    {
        q: "L'application ne détecte pas ma caméra.",
        a: "Vérifiez que la caméra est branchée avant de lancer Beaver. Pour les caméras IP, assurez-vous que l'URL RTSP est correcte et que la caméra est sur le même réseau.",
    },
    {
        q: "Les classes attribuées me semblent incorrectes.",
        a: "Recommencez la calibration avec au moins 5 planches de référence. Vérifiez également l'éclairage de la ligne (lumière uniforme, sans reflets) et la mise au point de l'objectif.",
    },
    {
        q: "L'application est lente ou rame.",
        a: "Beaver recommande un processeur 4 cœurs et 8 Go de RAM minimum. Fermez les autres applications gourmandes. Si le problème persiste, réduisez la résolution caméra dans les paramètres.",
    },
    {
        q: "Comment signaler un bug ?",
        a: "Envoyez un email à beaver.eip@gmail.com avec une description du problème, les logs (Aide → Afficher les logs → Exporter) et si possible une capture d'écran.",
    },
];

function FaqItem({ item }) {
    const [open, setOpen] = useState(false);
    return (
        <div className="border-b border-black/5 last:border-0">
            <button
                onClick={() => setOpen((v) => !v)}
                className="w-full flex items-center justify-between gap-4 py-4 text-left"
            >
                <span className="text-sm font-medium">{item.q}</span>
                {open ? <ChevronDown className="h-4 w-4 shrink-0 text-[hsl(var(--muted-foreground))]" /> : <ChevronRight className="h-4 w-4 shrink-0 text-[hsl(var(--muted-foreground))]" />}
            </button>
            {open && (
                <div className="pb-4 text-sm text-[hsl(var(--muted-foreground))] leading-[1.7]">
                    {item.a}
                </div>
            )}
        </div>
    );
}

function FeedbackForm() {
    const [form, setForm] = useState({ category: 'Autre', content: '' });
    const [submitting, setSubmitting] = useState(false);
    const [done, setDone] = useState(false);

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!form.content.trim()) return;
        try {
            setSubmitting(true);
            await submitFeedback(form);
            setDone(true);
            setForm({ category: 'Autre', content: '' });
            toast.success('Feedback envoyé, merci !');
        } catch {
            toast.error('Erreur lors de l\'envoi.');
        } finally {
            setSubmitting(false);
        }
    };

    if (done) return (
        <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 text-center text-sm text-[hsl(var(--muted-foreground))]">
            Merci pour votre retour ! <button onClick={() => setDone(false)} className="underline underline-offset-4 ml-1">Envoyer un autre</button>
        </div>
    );

    return (
        <form onSubmit={onSubmit} className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 space-y-4">
            <div className="flex flex-col gap-1.5">
                <Label className="label-caps">Catégorie</Label>
                <div className="flex flex-wrap gap-2">
                    {FEEDBACK_CATEGORIES.map((c) => (
                        <button
                            key={c} type="button"
                            onClick={() => setForm((s) => ({ ...s, category: c }))}
                            className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
                                form.category === c
                                    ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] border-transparent'
                                    : 'border-black/10 hover:bg-[hsl(38_45%_94%)]'
                            }`}
                        >{c}</button>
                    ))}
                </div>
            </div>
            <div className="flex flex-col gap-1.5">
                <Label className="label-caps">Votre remarque</Label>
                <Textarea
                    rows={4}
                    value={form.content}
                    onChange={(e) => setForm((s) => ({ ...s, content: e.target.value }))}
                    placeholder="Décrivez votre remarque, une idée, une observation…"
                    className="bg-[hsl(var(--background))]"
                    required
                />
            </div>
            <div className="flex justify-end">
                <button
                    type="submit" disabled={submitting}
                    className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-5 h-10 text-sm font-medium transition-colors"
                >
                    {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Send className="h-4 w-4" />Envoyer</>}
                </button>
            </div>
        </form>
    );
}

export default function Account() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [tutorials, setTutorials] = useState([]);
    const [ticketSummary, setTicketSummary] = useState({ total: 0, unread: 0 });
    const [loading, setLoading] = useState(true);

    const logout = () => {
        localStorage.removeItem('beaver_beta_token');
        navigate('/beta', { replace: true });
    };

    const load = useCallback(async () => {
        const token = localStorage.getItem('beaver_beta_token');
        if (!token) {
            navigate('/beta', { replace: true });
            return;
        }
        try {
            const [me, tutos, ticketData] = await Promise.all([fetchBetaMe(), fetchTutorials(), listMyTickets()]);
            setUser(me);
            setTutorials(tutos);
            setTicketSummary({ total: ticketData.tickets.length, unread: ticketData.unread_count });
        } catch (err) {
            const status = err?.response?.status;
            if (status === 401 || status === 403) {
                localStorage.removeItem('beaver_beta_token');
                toast.error(status === 403 ? 'Votre accès a été révoqué.' : 'Session expirée, veuillez vous reconnecter.');
                navigate('/beta', { replace: true });
            } else {
                toast.error('Erreur de chargement. Vérifiez votre connexion.');
            }
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    useEffect(() => { load(); }, [load]);

    const formatDate = (iso) => {
        if (!iso) return null;
        return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 sm:py-16 space-y-10">

            {/* Header */}
            <div className="flex items-start justify-between gap-4">
                <div>
                    <div className="label-caps mb-1">
                        <span className="text-[hsl(var(--primary))]">Espace client</span> · Beaver Beta
                    </div>
                    <h1 className="font-heading text-3xl sm:text-4xl tracking-[-0.02em]">
                        {user?.company ?? 'Bienvenue'}
                    </h1>
                    <div className="mt-2 flex items-center gap-2 flex-wrap">
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 text-green-700 px-3 py-1 text-xs font-medium">
                            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                            Accès actif
                        </span>
                        {user?.expires_at && (
                            <span className="text-xs text-[hsl(var(--muted-foreground))]">
                                Expire le {formatDate(user.expires_at)}
                            </span>
                        )}
                    </div>
                </div>
                <button
                    onClick={logout}
                    className="inline-flex items-center gap-1.5 rounded-full border border-black/10 px-3 h-9 text-sm hover:bg-[hsl(var(--card))] transition-colors text-[hsl(var(--muted-foreground))] shrink-0"
                >
                    <LogOut className="h-3.5 w-3.5" />
                    Déconnexion
                </button>
            </div>

            {/* Download */}
            <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-8">
                <div className="label-caps mb-4">Téléchargement</div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                    <div className="flex-1">
                        <div className="font-heading text-2xl">Beaver {APP_VERSION}</div>
                        <div className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                            Windows 10/11 · x64 · Aucune installation requise
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <a
                            href={DOWNLOAD_URL}
                            className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                        >
                            <Download className="h-4 w-4" />
                            Télécharger
                        </a>
                        <a
                            href="mailto:beaver.eip@gmail.com"
                            className="inline-flex items-center gap-2 rounded-full border border-black/10 px-4 h-11 text-sm font-medium hover:bg-[hsl(38_45%_94%)] transition-colors"
                        >
                            <MessageSquare className="h-4 w-4" />
                            Support
                        </a>
                    </div>
                </div>
            </div>

            {/* Tutorials */}
            <div>
                <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="h-4 w-4 text-[hsl(var(--primary))]" />
                    <span className="label-caps">Guides et tutoriels</span>
                    <span className="ml-auto text-xs text-[hsl(var(--muted-foreground))]">
                        {tutorials.length} guide{tutorials.length > 1 ? 's' : ''}
                    </span>
                </div>
                {tutorials.length === 0 ? (
                    <div className="rounded-xl border border-black/5 bg-[hsl(var(--card))] p-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
                        Les guides arrivent bientôt.
                    </div>
                ) : (
                    <div className="space-y-3">
                        {tutorials.map((t) => <TutorialCard key={t.id} tutorial={t} />)}
                    </div>
                )}
            </div>

            {/* Tickets */}
            <div>
                <div className="flex items-center gap-2 mb-4">
                    <Ticket className="h-4 w-4 text-[hsl(var(--primary))]" />
                    <span className="label-caps">Mes tickets</span>
                    {ticketSummary.unread > 0 && (
                        <span className="inline-flex items-center justify-center h-5 min-w-5 rounded-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] text-[11px] font-bold px-1.5">
                            {ticketSummary.unread}
                        </span>
                    )}
                </div>
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 flex items-center justify-between gap-4">
                    <div>
                        <div className="text-sm font-medium">
                            {ticketSummary.total === 0
                                ? 'Aucun ticket pour l\'instant'
                                : `${ticketSummary.total} ticket${ticketSummary.total > 1 ? 's' : ''}`}
                        </div>
                        {ticketSummary.unread > 0 && (
                            <div className="mt-1 text-xs text-[hsl(var(--primary))] font-medium">
                                {ticketSummary.unread} réponse{ticketSummary.unread > 1 ? 's' : ''} non lue{ticketSummary.unread > 1 ? 's' : ''}
                            </div>
                        )}
                        <div className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                            Signalez un bug, posez une question ou demandez une amélioration.
                        </div>
                    </div>
                    <Link
                        to="/account/tickets"
                        className="shrink-0 inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-4 h-10 text-sm font-medium transition-colors"
                    >
                        Voir mes tickets <ArrowRight className="h-4 w-4" />
                    </Link>
                </div>
            </div>

            {/* FAQ */}
            <div>
                <div className="label-caps mb-4">Questions fréquentes</div>
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] px-5">
                    {FAQ.map((item, i) => <FaqItem key={i} item={item} />)}
                </div>
            </div>

            {/* Feedback libre */}
            <div>
                <div className="label-caps mb-1">Feedback rapide</div>
                <p className="text-sm text-[hsl(var(--muted-foreground))] mb-4">
                    Une remarque, une idée ? Envoyez-la directement sans créer de ticket.
                </p>
                <FeedbackForm />
            </div>

            {/* Beta feedback */}
            <div className="rounded-2xl border border-[hsl(var(--primary)/0.2)] bg-[hsl(38_45%_96%)] p-6 sm:p-8">
                <div className="flex items-start gap-4">
                    <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[hsl(var(--primary)/0.1)]">
                        <Send className="h-5 w-5 text-[hsl(var(--primary))]" />
                    </span>
                    <div>
                        <div className="font-medium mb-1">En fin de bêta, pensez à nous envoyer :</div>
                        <ul className="space-y-1.5 text-sm text-[hsl(var(--muted-foreground))]">
                            {[
                                'Le formulaire de retour UX (envoyé par email)',
                                'La base de données locale : Fichier → Exporter → Base de données',
                                'Les logs d\'erreur : Aide → Afficher les logs → Exporter',
                            ].map((item) => (
                                <li key={item} className="flex items-start gap-2">
                                    <CheckCircle className="h-4 w-4 shrink-0 mt-0.5 text-[hsl(var(--primary)/0.6)]" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                        <a
                            href="mailto:beaver.eip@gmail.com"
                            className="mt-4 inline-flex items-center gap-2 text-sm text-[hsl(var(--primary))] underline underline-offset-4"
                        >
                            beaver.eip@gmail.com
                        </a>
                    </div>
                </div>
            </div>

        </div>
    );
}
