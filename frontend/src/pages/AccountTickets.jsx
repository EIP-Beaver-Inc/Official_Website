import { useEffect, useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plus, ArrowLeft, Loader2, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { listMyTickets, createTicket } from '@/lib/api';

const CATEGORIES = ['Bug', 'Question', 'Amélioration', 'Autre'];

const STATUS_STYLES = {
    open:        { label: 'Ouvert',    cls: 'bg-blue-100 text-blue-700' },
    in_progress: { label: 'En cours',  cls: 'bg-amber-100 text-amber-700' },
    resolved:    { label: 'Résolu',    cls: 'bg-green-100 text-green-700' },
    closed:      { label: 'Fermé',     cls: 'bg-gray-100 text-gray-500' },
};

function StatusBadge({ status }) {
    const s = STATUS_STYLES[status] ?? { label: status, cls: 'bg-gray-100 text-gray-500' };
    return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${s.cls}`}>{s.label}</span>;
}

function NewTicketModal({ onClose, onCreated }) {
    const [form, setForm] = useState({ subject: '', description: '', category: 'Autre' });
    const [loading, setLoading] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            await createTicket(form);
            toast.success('Ticket créé.');
            onCreated();
            onClose();
        } catch {
            toast.error('Erreur lors de la création du ticket.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-2xl border border-black/5 bg-[hsl(var(--background))] shadow-[0_24px_60px_rgba(17,17,17,0.18)] p-6">
                <h2 className="font-heading text-2xl mb-5">Nouveau ticket</h2>
                <form onSubmit={submit} className="space-y-4">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Catégorie</Label>
                        <div className="flex flex-wrap gap-2">
                            {CATEGORIES.map((c) => (
                                <button key={c} type="button"
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
                        <Label className="label-caps">Sujet <span className="text-[hsl(var(--primary))]">*</span></Label>
                        <Input
                            value={form.subject}
                            onChange={(e) => setForm((s) => ({ ...s, subject: e.target.value }))}
                            placeholder="Ex. L'application plante au lancement"
                            className="bg-[hsl(var(--background))]"
                            required
                        />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Description <span className="text-[hsl(var(--primary))]">*</span></Label>
                        <Textarea
                            rows={5}
                            value={form.description}
                            onChange={(e) => setForm((s) => ({ ...s, description: e.target.value }))}
                            placeholder="Décrivez le problème ou la demande en détail…"
                            className="bg-[hsl(var(--background))]"
                            required
                        />
                    </div>
                    <div className="flex gap-3 pt-1">
                        <button type="button" onClick={onClose}
                            className="flex-1 rounded-full border border-black/10 h-11 text-sm font-medium hover:bg-[hsl(var(--card))] transition-colors">
                            Annuler
                        </button>
                        <button type="submit" disabled={loading}
                            className="flex-1 inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] h-11 text-sm font-medium transition-colors">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Créer le ticket'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function AccountTickets() {
    const navigate = useNavigate();
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        if (!localStorage.getItem('beaver_beta_token')) navigate('/beta', { replace: true });
    }, [navigate]);

    const load = useCallback(async () => {
        try {
            const data = await listMyTickets();
            setTickets(data.tickets);
        } catch (err) {
            if (err?.response?.status === 401) { navigate('/beta', { replace: true }); }
            else toast.error('Erreur de chargement.');
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    useEffect(() => { load(); }, [load]);

    const formatDate = (iso) =>
        new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });

    return (
        <section className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
            {showModal && <NewTicketModal onClose={() => setShowModal(false)} onCreated={load} />}

            <div className="flex items-center justify-between gap-4 mb-8">
                <div>
                    <Link to="/account" className="inline-flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] mb-3 transition-colors">
                        <ArrowLeft className="h-3.5 w-3.5" /> Retour à l'espace client
                    </Link>
                    <h1 className="font-heading text-3xl tracking-[-0.02em]">Mes tickets</h1>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="shrink-0 inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-4 h-10 text-sm font-medium transition-colors"
                >
                    <Plus className="h-4 w-4" /> Nouveau ticket
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" /></div>
            ) : tickets.length === 0 ? (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-12 text-center">
                    <div className="text-sm text-[hsl(var(--muted-foreground))] mb-4">Aucun ticket pour l'instant.</div>
                    <button onClick={() => setShowModal(true)}
                        className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-10 text-sm font-medium transition-colors">
                        <Plus className="h-4 w-4" /> Créer mon premier ticket
                    </button>
                </div>
            ) : (
                <div className="space-y-3">
                    {tickets.map((t) => (
                        <Link
                            key={t.id}
                            to={`/account/tickets/${t.id}`}
                            className="flex items-center gap-4 rounded-xl border border-black/5 bg-[hsl(var(--card))] p-4 hover:bg-black/[0.02] transition-colors group"
                        >
                            {t.unread_for_client && (
                                <span className="shrink-0 h-2 w-2 rounded-full bg-[hsl(var(--primary))]" title="Nouvelle réponse" />
                            )}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1 flex-wrap">
                                    <StatusBadge status={t.status} />
                                    <span className="text-xs text-[hsl(var(--muted-foreground))]">{t.category}</span>
                                    {t.unread_for_client && (
                                        <span className="text-xs text-[hsl(var(--primary))] font-medium">Nouvelle réponse</span>
                                    )}
                                </div>
                                <div className="font-medium text-sm truncate">{t.subject}</div>
                                <div className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                                    Mis à jour le {formatDate(t.updated_at)} · {t.messages.length} message{t.messages.length !== 1 ? 's' : ''}
                                </div>
                            </div>
                            <ChevronRight className="h-4 w-4 text-[hsl(var(--muted-foreground))] shrink-0 group-hover:translate-x-0.5 transition-transform" />
                        </Link>
                    ))}
                </div>
            )}
        </section>
    );
}
