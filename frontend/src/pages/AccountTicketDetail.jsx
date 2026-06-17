import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { ArrowLeft, Send, Loader2, Star } from 'lucide-react';
import { toast } from 'sonner';
import { Textarea } from '@/components/ui/textarea';
import { getTicket, markTicketSeen, addTicketMessage, submitSatisfaction } from '@/lib/api';

const STATUS_STYLES = {
    open:        { label: 'Ouvert',   cls: 'bg-blue-100 text-blue-700' },
    in_progress: { label: 'En cours', cls: 'bg-amber-100 text-amber-700' },
    resolved:    { label: 'Résolu',   cls: 'bg-green-100 text-green-700' },
    closed:      { label: 'Fermé',    cls: 'bg-gray-100 text-gray-500' },
};

function Message({ msg }) {
    const isAdmin = msg.author === 'admin';
    const date = new Date(msg.created_at).toLocaleString('fr-FR', {
        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });
    return (
        <div className={`flex gap-3 ${isAdmin ? '' : 'flex-row-reverse'}`}>
            <div className={`shrink-0 h-8 w-8 rounded-full flex items-center justify-center text-xs font-semibold ${
                isAdmin ? 'bg-[hsl(var(--primary)/0.12)] text-[hsl(var(--primary))]' : 'bg-black/5 text-[hsl(var(--foreground))]'
            }`}>
                {isAdmin ? 'B' : 'M'}
            </div>
            <div className={`max-w-[80%] ${isAdmin ? '' : 'items-end flex flex-col'}`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-[1.65] ${
                    isAdmin
                        ? 'bg-[hsl(var(--card))] border border-black/5'
                        : 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]'
                }`}>
                    {msg.content}
                </div>
                <div className="mt-1 text-[11px] text-[hsl(var(--muted-foreground))]">
                    {isAdmin ? 'Équipe Beaver' : 'Vous'} · {date}
                </div>
            </div>
        </div>
    );
}

function SatisfactionForm({ ticketId, onDone }) {
    const [nps, setNps] = useState(null);
    const [csat, setCsat] = useState(null);
    const [comment, setComment] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const canSubmit = nps !== null && csat !== null;

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!canSubmit) return;
        try {
            setSubmitting(true);
            await submitSatisfaction(ticketId, { nps, csat, comment: comment || null });
            toast.success('Merci pour votre évaluation !');
            onDone();
        } catch {
            toast.error('Erreur lors de l\'envoi.');
        } finally {
            setSubmitting(false);
        }
    };

    const npsLabel = nps === null ? '' : nps <= 6 ? 'Détracteur' : nps <= 8 ? 'Neutre' : 'Promoteur';
    const npsColor = nps === null ? '' : nps <= 6 ? 'text-red-500' : nps <= 8 ? 'text-amber-500' : 'text-green-600';

    return (
        <div className="rounded-2xl border border-[hsl(var(--primary)/0.2)] bg-[hsl(38_45%_96%)] p-6">
            <div className="font-medium mb-1">Ce ticket est résolu — comment s'est passée votre expérience ?</div>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mb-5">
                Votre évaluation nous aide à améliorer notre support.
            </p>
            <form onSubmit={onSubmit} className="space-y-5">
                {/* NPS */}
                <div>
                    <div className="label-caps mb-2">
                        Recommanderiez-vous Beaver ?
                        <span className={`ml-2 text-xs font-semibold ${npsColor}`}>{npsLabel}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                        {Array.from({ length: 11 }, (_, i) => (
                            <button key={i} type="button" onClick={() => setNps(i)}
                                className={`h-9 w-9 rounded-lg text-sm font-medium border transition-colors ${
                                    nps === i
                                        ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] border-transparent'
                                        : 'border-black/10 hover:bg-[hsl(var(--card))]'
                                }`}>{i}</button>
                        ))}
                    </div>
                    <div className="flex justify-between mt-1 text-[11px] text-[hsl(var(--muted-foreground))]">
                        <span>Pas du tout</span><span>Absolument</span>
                    </div>
                </div>
                {/* CSAT */}
                <div>
                    <div className="label-caps mb-2">Satisfaction de cette interaction</div>
                    <div className="flex gap-2">
                        {[1, 2, 3, 4, 5].map((v) => (
                            <button key={v} type="button" onClick={() => setCsat(v)}
                                className="focus:outline-none transition-transform hover:scale-110">
                                <Star className={`h-7 w-7 ${v <= (csat ?? 0) ? 'fill-amber-400 text-amber-400' : 'text-gray-300'}`} />
                            </button>
                        ))}
                    </div>
                </div>
                {/* Comment */}
                <div>
                    <div className="label-caps mb-2">Commentaire (optionnel)</div>
                    <Textarea rows={3} value={comment} onChange={(e) => setComment(e.target.value)}
                        placeholder="Dites-nous ce qui a bien fonctionné ou ce qu'on pourrait améliorer…"
                        className="bg-[hsl(var(--background))]" />
                </div>
                <button type="submit" disabled={!canSubmit || submitting}
                    className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-50 text-[hsl(var(--primary-foreground))] px-5 h-10 text-sm font-medium transition-colors">
                    {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Send className="h-4 w-4" />Envoyer l'évaluation</>}
                </button>
            </form>
        </div>
    );
}

export default function AccountTicketDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [ticket, setTicket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [reply, setReply] = useState('');
    const [sending, setSending] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => {
        if (!localStorage.getItem('beaver_beta_token')) navigate('/beta', { replace: true });
    }, [navigate]);

    const load = useCallback(async () => {
        try {
            const data = await getTicket(id);
            setTicket(data);
            if (data.unread_for_client) await markTicketSeen(id);
        } catch (err) {
            if (err?.response?.status === 401) navigate('/beta', { replace: true });
            else if (err?.response?.status === 404) navigate('/account/tickets', { replace: true });
            else toast.error('Erreur de chargement.');
        } finally {
            setLoading(false);
        }
    }, [id, navigate]);

    useEffect(() => { load(); }, [load]);
    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [ticket?.messages?.length]);

    const sendReply = async (e) => {
        e.preventDefault();
        if (!reply.trim()) return;
        try {
            setSending(true);
            const msg = await addTicketMessage(id, reply);
            setTicket((t) => ({ ...t, messages: [...t.messages, msg] }));
            setReply('');
        } catch {
            toast.error('Erreur lors de l\'envoi.');
        } finally {
            setSending(false);
        }
    };

    const formatDate = (iso) =>
        new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' });

    if (loading) return (
        <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" /></div>
    );
    if (!ticket) return null;

    const statusS = STATUS_STYLES[ticket.status] ?? { label: ticket.status, cls: 'bg-gray-100 text-gray-500' };
    const isClosed = ticket.status === 'closed';
    const isResolved = ticket.status === 'resolved';
    const needsSatisfaction = isResolved && !ticket.satisfaction;

    return (
        <section className="max-w-2xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
            <Link to="/account/tickets"
                className="inline-flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] mb-6 transition-colors">
                <ArrowLeft className="h-3.5 w-3.5" /> Mes tickets
            </Link>

            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusS.cls}`}>{statusS.label}</span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">{ticket.category}</span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">· Ouvert le {formatDate(ticket.created_at)}</span>
                </div>
                <h1 className="font-heading text-2xl sm:text-3xl tracking-[-0.02em]">{ticket.subject}</h1>
            </div>

            {/* Thread */}
            <div className="space-y-4 mb-6">
                {/* Initial description */}
                <Message msg={{ author: 'client', content: ticket.description, created_at: ticket.created_at }} />
                {ticket.messages.map((m) => <Message key={m.id} msg={m} />)}
                <div ref={bottomRef} />
            </div>

            {/* Satisfaction form */}
            {needsSatisfaction && (
                <div className="mb-6">
                    <SatisfactionForm ticketId={id} onDone={load} />
                </div>
            )}

            {isClosed && !needsSatisfaction && (
                <div className="mb-6 rounded-xl border border-black/5 bg-[hsl(var(--card))] p-4 text-sm text-center text-[hsl(var(--muted-foreground))]">
                    Ce ticket est fermé.{' '}
                    {ticket.satisfaction && <span className="text-green-600 font-medium">Évaluation soumise — merci !</span>}
                </div>
            )}

            {/* Reply form */}
            {!isClosed && (
                <form onSubmit={sendReply} className="flex gap-3 items-end">
                    <Textarea
                        rows={3}
                        value={reply}
                        onChange={(e) => setReply(e.target.value)}
                        placeholder="Votre réponse…"
                        className="flex-1 bg-[hsl(var(--background))]"
                        onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) sendReply(e); }}
                    />
                    <button type="submit" disabled={sending || !reply.trim()}
                        className="shrink-0 inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-50 text-[hsl(var(--primary-foreground))] h-11 w-11 transition-colors">
                        {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    </button>
                </form>
            )}
        </section>
    );
}
