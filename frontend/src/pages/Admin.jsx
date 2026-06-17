import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Key, Users, Copy, Check, LogOut, Loader2, RefreshCw, Eye, EyeOff, Trash2, Ticket, MessageSquare, ChevronDown, Send, BarChart2 } from 'lucide-react';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { adminListKeys, adminListClients, adminGenerateKey, adminDeleteClient, adminListTickets, adminUpdateTicketStatus, adminReplyTicket, adminListFeedback, adminGetStats } from '@/lib/api';

const TICKET_STATUSES = [
    { value: 'open',        label: 'Ouvert',   cls: 'bg-blue-100 text-blue-700' },
    { value: 'in_progress', label: 'En cours', cls: 'bg-amber-100 text-amber-700' },
    { value: 'resolved',    label: 'Résolu',   cls: 'bg-green-100 text-green-700' },
    { value: 'closed',      label: 'Fermé',    cls: 'bg-gray-100 text-gray-500' },
];

function TicketStatusBadge({ status }) {
    const s = TICKET_STATUSES.find((x) => x.value === status) ?? { label: status, cls: 'bg-gray-100 text-gray-500' };
    return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${s.cls}`}>{s.label}</span>;
}

function TicketModal({ ticket: initial, onClose, onUpdated }) {
    const [ticket, setTicket] = useState(initial);
    const [reply, setReply] = useState('');
    const [sending, setSending] = useState(false);
    const [updatingStatus, setUpdatingStatus] = useState(false);

    const changeStatus = async (status) => {
        try {
            setUpdatingStatus(true);
            await adminUpdateTicketStatus(ticket.id, status);
            setTicket((t) => ({ ...t, status }));
            onUpdated();
            toast.success('Statut mis à jour.');
        } catch { toast.error('Erreur.'); }
        finally { setUpdatingStatus(false); }
    };

    const sendReply = async (e) => {
        e.preventDefault();
        if (!reply.trim()) return;
        try {
            setSending(true);
            const msg = await adminReplyTicket(ticket.id, reply);
            setTicket((t) => ({ ...t, messages: [...t.messages, msg] }));
            setReply('');
            onUpdated();
        } catch { toast.error('Erreur lors de l\'envoi.'); }
        finally { setSending(false); }
    };

    const formatDate = (iso) => new Date(iso).toLocaleString('fr-FR', {
        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
    });

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm">
            <div className="w-full sm:max-w-2xl max-h-[90vh] overflow-y-auto rounded-t-2xl sm:rounded-2xl border border-black/5 bg-[hsl(var(--background))] shadow-[0_24px_60px_rgba(17,17,17,0.18)]">
                <div className="sticky top-0 bg-[hsl(var(--background))] border-b border-black/5 px-6 py-4 flex items-start justify-between gap-4">
                    <div>
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                            <TicketStatusBadge status={ticket.status} />
                            <span className="text-xs text-[hsl(var(--muted-foreground))]">{ticket.category} · {ticket.company}</span>
                        </div>
                        <div className="font-medium">{ticket.subject}</div>
                        <div className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{ticket.contact_name} · {ticket.email}</div>
                    </div>
                    <button onClick={onClose} className="shrink-0 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] text-sm">✕</button>
                </div>

                <div className="px-6 py-4 space-y-4">
                    {/* Thread */}
                    <div className="space-y-3">
                        <div className="rounded-xl bg-[hsl(var(--card))] border border-black/5 px-4 py-3 text-sm leading-[1.65]">
                            <div className="text-[11px] text-[hsl(var(--muted-foreground))] mb-1">Client · {formatDate(ticket.created_at)}</div>
                            {ticket.description}
                        </div>
                        {ticket.messages.map((m) => (
                            <div key={m.id} className={`rounded-xl border border-black/5 px-4 py-3 text-sm leading-[1.65] ${
                                m.author === 'admin' ? 'bg-[hsl(var(--primary)/0.06)] border-[hsl(var(--primary)/0.15)]' : 'bg-[hsl(var(--card))]'
                            }`}>
                                <div className="text-[11px] text-[hsl(var(--muted-foreground))] mb-1">
                                    {m.author === 'admin' ? 'Équipe Beaver' : 'Client'} · {formatDate(m.created_at)}
                                </div>
                                {m.content}
                            </div>
                        ))}
                    </div>

                    {/* Satisfaction */}
                    {ticket.satisfaction && (
                        <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm">
                            <div className="text-[11px] text-green-600 font-medium mb-1">Satisfaction soumise</div>
                            <div className="flex gap-4">
                                <span>NPS : <strong>{ticket.satisfaction.nps}/10</strong></span>
                                <span>CSAT : <strong>{ticket.satisfaction.csat}/5 ★</strong></span>
                            </div>
                            {ticket.satisfaction.comment && (
                                <div className="mt-2 text-[hsl(var(--muted-foreground))] italic">"{ticket.satisfaction.comment}"</div>
                            )}
                        </div>
                    )}

                    {/* Change status */}
                    <div>
                        <div className="label-caps mb-2">Changer le statut</div>
                        <div className="flex flex-wrap gap-2">
                            {TICKET_STATUSES.map((s) => (
                                <button key={s.value} onClick={() => changeStatus(s.value)}
                                    disabled={updatingStatus || ticket.status === s.value}
                                    className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors disabled:opacity-50 ${
                                        ticket.status === s.value ? `${s.cls} border-transparent` : 'border-black/10 hover:bg-[hsl(var(--card))]'
                                    }`}>
                                    {s.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Reply */}
                    {ticket.status !== 'closed' && (
                        <form onSubmit={sendReply} className="flex gap-3 items-end pt-2">
                            <Textarea rows={3} value={reply} onChange={(e) => setReply(e.target.value)}
                                placeholder="Répondre au client…"
                                className="flex-1 bg-[hsl(var(--background))]" />
                            <button type="submit" disabled={sending || !reply.trim()}
                                className="shrink-0 inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-50 text-[hsl(var(--primary-foreground))] h-11 w-11 transition-colors">
                                {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}

function StatusBadge({ status }) {
    const styles = {
        unused: 'bg-amber-100 text-amber-700',
        active: 'bg-green-100 text-green-700',
        expired: 'bg-red-100 text-red-600',
        revoked: 'bg-gray-100 text-gray-500',
    };
    const labels = { unused: 'Disponible', active: 'Utilisée', expired: 'Expirée', revoked: 'Révoquée' };
    return (
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status] ?? 'bg-gray-100 text-gray-600'}`}>
            {labels[status] ?? status}
        </span>
    );
}

function MaskedKey({ keyStr }) {
    const [revealed, setRevealed] = useState(false);
    const masked = keyStr.slice(0, 4) + '-****-****-****';
    return (
        <div className="flex items-center gap-1">
            <span className="font-mono text-xs tracking-wider">{revealed ? keyStr : masked}</span>
            <button
                onClick={() => setRevealed((v) => !v)}
                className="inline-flex items-center rounded px-1.5 py-1 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-black/5 transition-colors"
                title={revealed ? 'Masquer' : 'Révéler'}
            >
                {revealed ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
            </button>
            {revealed && <CopyButton text={keyStr} />}
        </div>
    );
}

function CopyButton({ text }) {
    const [copied, setCopied] = useState(false);
    const copy = async () => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    return (
        <button
            onClick={copy}
            className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-black/5 transition-colors"
        >
            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            {copied ? 'Copié' : 'Copier'}
        </button>
    );
}

function GenerateKeyModal({ onClose, onCreated }) {
    const [form, setForm] = useState({ company: '', notes: '', expires_at: '' });
    const [loading, setLoading] = useState(false);
    const [generatedKey, setGeneratedKey] = useState(null);

    const handleChange = (f) => (e) => setForm((s) => ({ ...s, [f]: e.target.value }));

    const submit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            const data = await adminGenerateKey({
                company: form.company || null,
                notes: form.notes || null,
                expires_at: form.expires_at || null,
            });
            setGeneratedKey(data.key);
            onCreated();
        } catch {
            toast.error('Erreur lors de la génération de la clé.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-2xl border border-black/5 bg-[hsl(var(--background))] shadow-[0_24px_60px_rgba(17,17,17,0.18)] p-6">
                {generatedKey ? (
                    <div className="text-center">
                        <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-green-100 mb-4">
                            <Key className="h-6 w-6 text-green-700" />
                        </div>
                        <h2 className="font-heading text-2xl mb-2">Clé générée</h2>
                        <p className="text-sm text-[hsl(var(--muted-foreground))] mb-5">
                            Copiez cette clé et envoyez-la par email au client. Elle ne sera visible qu'une seule fois ici.
                        </p>
                        <div className="flex items-center justify-between gap-2 rounded-xl border border-black/10 bg-[hsl(var(--card))] px-4 py-3 font-mono text-lg font-medium tracking-widest">
                            {generatedKey}
                            <CopyButton text={generatedKey} />
                        </div>
                        <button
                            onClick={onClose}
                            className="mt-6 w-full rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] h-11 text-sm font-medium transition-colors"
                        >
                            Fermer
                        </button>
                    </div>
                ) : (
                    <>
                        <h2 className="font-heading text-2xl mb-5">Générer une clé beta</h2>
                        <form onSubmit={submit} className="space-y-4">
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">Entreprise (optionnel)</Label>
                                <Input
                                    value={form.company}
                                    onChange={handleChange('company')}
                                    placeholder="Scierie Dupont"
                                    className="bg-[hsl(var(--background))]"
                                />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">Notes (optionnel)</Label>
                                <Input
                                    value={form.notes}
                                    onChange={handleChange('notes')}
                                    placeholder="Envoyée le 15/06/2026"
                                    className="bg-[hsl(var(--background))]"
                                />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">Expiration (optionnel)</Label>
                                <Input
                                    type="date"
                                    value={form.expires_at}
                                    onChange={handleChange('expires_at')}
                                    className="bg-[hsl(var(--background))]"
                                />
                            </div>
                            <div className="flex gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="flex-1 rounded-full border border-black/10 h-11 text-sm font-medium hover:bg-[hsl(var(--card))] transition-colors"
                                >
                                    Annuler
                                </button>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex-1 inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] h-11 text-sm font-medium transition-colors"
                                >
                                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Générer'}
                                </button>
                            </div>
                        </form>
                    </>
                )}
            </div>
        </div>
    );
}

function BarRow({ label, value, max, color = 'bg-[hsl(var(--primary))]' }) {
    const pct = max > 0 ? Math.round((value / max) * 100) : 0;
    return (
        <div className="flex items-center gap-3 text-sm">
            <span className="w-36 shrink-0 text-[hsl(var(--muted-foreground))] truncate">{label}</span>
            <div className="flex-1 h-2 rounded-full bg-black/5 overflow-hidden">
                <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
            </div>
            <span className="w-6 text-right font-medium">{value}</span>
        </div>
    );
}

function StatCard({ label, value, sub, color = 'text-[hsl(var(--primary))]' }) {
    return (
        <div className="rounded-xl border border-black/5 bg-[hsl(var(--card))] p-4 sm:p-5">
            <div className="label-caps mb-2">{label}</div>
            <div className={`font-heading italic text-4xl leading-none ${color}`}>
                {value ?? <span className="text-[hsl(var(--muted-foreground))] text-2xl not-italic font-normal">—</span>}
            </div>
            {sub && <div className="mt-1.5 text-xs text-[hsl(var(--muted-foreground))]">{sub}</div>}
        </div>
    );
}

function StatsPanel({ stats, formatDate }) {
    if (!stats) return (
        <div className="flex items-center justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" />
        </div>
    );

    const { nps_score, nps_avg, csat_avg, satisfaction_count, nps_distribution,
            ticket_count, ticket_by_status, ticket_by_category,
            feedback_count, feedback_by_category, client_count,
            key_conversion_rate, satisfaction_comments } = stats;

    const { promoters = 0, passives = 0, detractors = 0 } = nps_distribution ?? {};
    const npsTotal = promoters + passives + detractors;

    const ticketStatuses = [
        { key: 'open',        label: 'Ouverts',   color: 'bg-blue-400' },
        { key: 'in_progress', label: 'En cours',  color: 'bg-amber-400' },
        { key: 'resolved',    label: 'Résolus',   color: 'bg-green-400' },
        { key: 'closed',      label: 'Fermés',    color: 'bg-gray-300' },
    ];
    const maxTicketStatus = Math.max(...ticketStatuses.map((s) => ticket_by_status?.[s.key] ?? 0), 1);
    const maxTicketCat = Math.max(...Object.values(ticket_by_category ?? {}), 1);
    const maxFbCat = Math.max(...Object.values(feedback_by_category ?? {}), 1);

    const npsColor = nps_score === null ? 'text-[hsl(var(--muted-foreground))]'
        : nps_score >= 50 ? 'text-green-600'
        : nps_score >= 0 ? 'text-amber-600'
        : 'text-red-500';

    const csatColor = csat_avg === null ? 'text-[hsl(var(--muted-foreground))]'
        : csat_avg >= 4 ? 'text-green-600'
        : csat_avg >= 3 ? 'text-amber-600'
        : 'text-red-500';

    return (
        <div className="space-y-6">
            {/* KPI cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <StatCard
                    label="NPS Score"
                    value={nps_score !== null ? nps_score : null}
                    sub={`${satisfaction_count} réponse${satisfaction_count !== 1 ? 's' : ''}`}
                    color={npsColor}
                />
                <StatCard
                    label="NPS moyen"
                    value={nps_avg !== null ? `${nps_avg}/10` : null}
                    sub="Recommandation"
                />
                <StatCard
                    label="CSAT moyen"
                    value={csat_avg !== null ? `${csat_avg}/5` : null}
                    sub="Satisfaction tickets"
                    color={csatColor}
                />
                <StatCard
                    label="Conversion clés"
                    value={`${key_conversion_rate}%`}
                    sub={`${client_count} client${client_count !== 1 ? 's' : ''} actif${client_count !== 1 ? 's' : ''}`}
                    color="text-[hsl(var(--primary))]"
                />
            </div>

            {/* NPS distribution */}
            {npsTotal > 0 && (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-5">
                    <div className="label-caps mb-4">Répartition NPS</div>
                    <div className="flex h-4 rounded-full overflow-hidden gap-0.5 mb-3">
                        {detractors > 0 && (
                            <div className="bg-red-400 transition-all" style={{ width: `${(detractors / npsTotal) * 100}%` }} title={`Détracteurs (0-6): ${detractors}`} />
                        )}
                        {passives > 0 && (
                            <div className="bg-amber-300 transition-all" style={{ width: `${(passives / npsTotal) * 100}%` }} title={`Passifs (7-8): ${passives}`} />
                        )}
                        {promoters > 0 && (
                            <div className="bg-green-400 transition-all" style={{ width: `${(promoters / npsTotal) * 100}%` }} title={`Promoteurs (9-10): ${promoters}`} />
                        )}
                    </div>
                    <div className="flex gap-4 text-xs text-[hsl(var(--muted-foreground))]">
                        <span className="flex items-center gap-1.5"><span className="inline-block w-2.5 h-2.5 rounded-full bg-red-400" />Détracteurs (0-6) : {detractors}</span>
                        <span className="flex items-center gap-1.5"><span className="inline-block w-2.5 h-2.5 rounded-full bg-amber-300" />Passifs (7-8) : {passives}</span>
                        <span className="flex items-center gap-1.5"><span className="inline-block w-2.5 h-2.5 rounded-full bg-green-400" />Promoteurs (9-10) : {promoters}</span>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Tickets by status */}
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-5">
                    <div className="label-caps mb-4">Tickets par statut <span className="text-[hsl(var(--muted-foreground))] font-normal normal-case">(total {ticket_count})</span></div>
                    <div className="space-y-2.5">
                        {ticketStatuses.map((s) => (
                            <BarRow key={s.key} label={s.label} value={ticket_by_status?.[s.key] ?? 0} max={maxTicketStatus} color={s.color} />
                        ))}
                    </div>
                </div>

                {/* Tickets by category */}
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-5">
                    <div className="label-caps mb-4">Tickets par catégorie</div>
                    <div className="space-y-2.5">
                        {Object.entries(ticket_by_category ?? {}).sort((a, b) => b[1] - a[1]).map(([cat, count]) => (
                            <BarRow key={cat} label={cat} value={count} max={maxTicketCat} />
                        ))}
                        {Object.keys(ticket_by_category ?? {}).length === 0 && (
                            <p className="text-sm text-[hsl(var(--muted-foreground))]">Aucun ticket.</p>
                        )}
                    </div>
                </div>

                {/* Feedback by category */}
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-5">
                    <div className="label-caps mb-4">Feedbacks par catégorie <span className="text-[hsl(var(--muted-foreground))] font-normal normal-case">(total {feedback_count})</span></div>
                    <div className="space-y-2.5">
                        {Object.entries(feedback_by_category ?? {}).sort((a, b) => b[1] - a[1]).map(([cat, count]) => (
                            <BarRow key={cat} label={cat} value={count} max={maxFbCat} color="bg-purple-400" />
                        ))}
                        {Object.keys(feedback_by_category ?? {}).length === 0 && (
                            <p className="text-sm text-[hsl(var(--muted-foreground))]">Aucun feedback.</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Satisfaction comments */}
            <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
                <div className="px-5 py-4 border-b border-black/5">
                    <div className="label-caps">Commentaires de satisfaction</div>
                </div>
                {satisfaction_comments.length === 0 ? (
                    <div className="py-12 text-center text-sm text-[hsl(var(--muted-foreground))]">Aucun commentaire pour l'instant.</div>
                ) : (
                    <div className="divide-y divide-black/5">
                        {satisfaction_comments.map((c, i) => (
                            <div key={i} className="px-5 py-4">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-sm font-medium">{c.company}</span>
                                    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700">NPS {c.nps}/10</span>
                                    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700">CSAT {c.csat}/5 ★</span>
                                    {c.submitted_at && <span className="ml-auto text-xs text-[hsl(var(--muted-foreground))]">{formatDate(c.submitted_at)}</span>}
                                </div>
                                <p className="text-sm leading-[1.65] text-[hsl(var(--muted-foreground))] italic">"{c.comment}"</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default function Admin() {
    const navigate = useNavigate();
    const [tab, setTab] = useState('keys');
    const [keys, setKeys] = useState([]);
    const [clients, setClients] = useState([]);
    const [tickets, setTickets] = useState([]);
    const [feedback, setFeedback] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [ticketFilter, setTicketFilter] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('beaver_admin_token');
        if (!token) {
            navigate('/admin/login', { replace: true });
        }
    }, [navigate]);

    const refresh = useCallback(async () => {
        setLoading(true);
        try {
            const [k, c, t, fb, st] = await Promise.all([adminListKeys(), adminListClients(), adminListTickets(), adminListFeedback(), adminGetStats()]);
            setKeys(k);
            setClients(c);
            setTickets(t);
            setFeedback(fb);
            setStats(st);
        } catch (err) {
            if (err?.response?.status === 401) {
                localStorage.removeItem('beaver_admin_token');
                navigate('/admin/login', { replace: true });
            } else {
                toast.error('Erreur de chargement des données.');
            }
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    useEffect(() => {
        refresh();
    }, [refresh]);

    const logout = () => {
        localStorage.removeItem('beaver_admin_token');
        navigate('/admin/login', { replace: true });
    };

    const formatDate = (iso) => {
        if (!iso) return '—';
        return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    };

    const deleteClient = async (clientId) => {
        if (!window.confirm('Supprimer ce client et révoquer sa clé ?')) return;
        try {
            await adminDeleteClient(clientId);
            toast.success('Client supprimé, clé révoquée.');
            refresh();
        } catch {
            toast.error('Erreur lors de la suppression.');
        }
    };

    const unusedCount = keys.filter((k) => k.status === 'unused').length;
    const activeCount = keys.filter((k) => k.status === 'active').length;
    const openTickets = tickets.filter((t) => t.status === 'open' || t.status === 'in_progress').length;
    const filteredTickets = ticketFilter ? tickets.filter((t) => t.status === ticketFilter) : tickets;

    return (
        <section className="max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
            {showModal && (
                <GenerateKeyModal
                    onClose={() => setShowModal(false)}
                    onCreated={() => refresh()}
                />
            )}

            <div className="flex items-start justify-between gap-4 mb-8">
                <div>
                    <div className="label-caps mb-1">
                        <span className="text-[hsl(var(--primary))]">Admin</span> · Beaver
                    </div>
                    <h1 className="font-heading text-3xl sm:text-4xl tracking-[-0.02em]">
                        Dashboard beta
                    </h1>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={refresh}
                        className="inline-flex items-center gap-1.5 rounded-full border border-black/10 px-3 h-9 text-sm hover:bg-[hsl(var(--card))] transition-colors"
                    >
                        <RefreshCw className="h-3.5 w-3.5" />
                        Actualiser
                    </button>
                    <button
                        onClick={logout}
                        className="inline-flex items-center gap-1.5 rounded-full border border-black/10 px-3 h-9 text-sm hover:bg-[hsl(var(--card))] transition-colors text-[hsl(var(--muted-foreground))]"
                    >
                        <LogOut className="h-3.5 w-3.5" />
                        Déconnexion
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                {[
                    { label: 'Clés générées', value: keys.length },
                    { label: 'Beta testeurs', value: activeCount },
                    { label: 'Tickets ouverts', value: openTickets },
                    { label: 'Feedbacks', value: feedback.length },
                ].map((s) => (
                    <div
                        key={s.label}
                        className="rounded-xl border border-black/5 bg-[hsl(var(--card))] p-4 sm:p-5"
                    >
                        <div className="label-caps">{s.label}</div>
                        <div className="mt-2 font-heading italic text-[hsl(var(--primary))] text-4xl leading-none">
                            {s.value}
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex items-center justify-between mb-4">
                <div className="flex rounded-xl border border-black/5 bg-[hsl(var(--card))] p-1 gap-1">
                    {[
                        { id: 'keys', label: 'Clés', icon: Key },
                        { id: 'clients', label: 'Clients', icon: Users },
                        { id: 'tickets', label: 'Tickets', icon: Ticket, badge: openTickets },
                        { id: 'feedback', label: 'Feedback', icon: MessageSquare },
                        { id: 'indicateurs', label: 'Indicateurs', icon: BarChart2 },
                    ].map(({ id, label, icon: Icon, badge }) => (
                        <button
                            key={id}
                            onClick={() => setTab(id)}
                            className={`inline-flex items-center gap-2 rounded-lg px-4 h-9 text-sm font-medium transition-colors ${
                                tab === id
                                    ? 'bg-[hsl(var(--background))] shadow-sm text-[hsl(var(--foreground))]'
                                    : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
                            }`}
                        >
                            <Icon className="h-3.5 w-3.5" />
                            {label}
                            {badge > 0 && (
                                <span className="ml-1 inline-flex items-center justify-center h-4 min-w-4 rounded-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] text-[10px] font-bold px-1">
                                    {badge}
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {tab === 'keys' && (
                    <button
                        onClick={() => setShowModal(true)}
                        className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-4 h-9 text-sm font-medium transition-colors"
                    >
                        <Plus className="h-3.5 w-3.5" />
                        Générer une clé
                    </button>
                )}
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" />
                </div>
            ) : tab === 'keys' ? (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
                    {keys.length === 0 ? (
                        <div className="py-16 text-center text-sm text-[hsl(var(--muted-foreground))]">
                            Aucune clé générée pour l'instant.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-black/5 bg-[hsl(38_45%_94%)]">
                                        <th className="text-left px-4 py-3 label-caps font-medium">Clé</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Statut</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Entreprise</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Créée</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Utilisée</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Expire</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {keys.map((k) => (
                                        <tr key={k.id} className="border-b border-black/5 last:border-0 hover:bg-black/[0.02]">
                                            <td className="px-4 py-3">
                                                <MaskedKey keyStr={k.key} />
                                                        {k.notes && (
                                                    <div className="text-[10px] text-[hsl(var(--muted-foreground))] mt-0.5">{k.notes}</div>
                                                )}
                                            </td>
                                            <td className="px-4 py-3">
                                                <StatusBadge status={k.status} />
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {k.company || '—'}
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {formatDate(k.created_at)}
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {formatDate(k.used_at)}
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {formatDate(k.expires_at)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            ) : tab === 'clients' ? (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
                    {clients.length === 0 ? (
                        <div className="py-16 text-center text-sm text-[hsl(var(--muted-foreground))]">
                            Aucun client enregistré pour l'instant.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-black/5 bg-[hsl(38_45%_94%)]">
                                        <th className="text-left px-4 py-3 label-caps font-medium">Entreprise</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Contact</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Email</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Téléphone</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Clé</th>
                                        <th className="text-left px-4 py-3 label-caps font-medium">Enregistré</th>
                                        <th className="px-4 py-3" />
                                    </tr>
                                </thead>
                                <tbody>
                                    {clients.map((c) => (
                                        <tr key={c.id} className="border-b border-black/5 last:border-0 hover:bg-black/[0.02]">
                                            <td className="px-4 py-3 font-medium">{c.company}</td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">{c.contact_name}</td>
                                            <td className="px-4 py-3">
                                                <a
                                                    href={`mailto:${c.email}`}
                                                    className="text-[hsl(var(--primary))] underline underline-offset-4"
                                                >
                                                    {c.email}
                                                </a>
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {c.phone || '—'}
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="font-mono text-xs tracking-wider">{c.key}</span>
                                            </td>
                                            <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                                                {formatDate(c.registered_at)}
                                            </td>
                                            <td className="px-4 py-3">
                                                <button
                                                    onClick={() => deleteClient(c.id)}
                                                    className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                                                    title="Supprimer ce client et révoquer sa clé"
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                    Supprimer
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            ) : tab === 'tickets' ? (
                <>
                    {selectedTicket && (
                        <TicketModal
                            ticket={selectedTicket}
                            onClose={() => setSelectedTicket(null)}
                            onUpdated={() => { refresh(); setSelectedTicket(null); }}
                        />
                    )}
                    <div className="flex flex-wrap gap-2 mb-4">
                        {[{ value: '', label: 'Tous' }, ...TICKET_STATUSES].map((s) => (
                            <button key={s.value} onClick={() => setTicketFilter(s.value)}
                                className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
                                    ticketFilter === s.value
                                        ? 'bg-[hsl(var(--foreground))] text-[hsl(var(--background))] border-transparent'
                                        : 'border-black/10 hover:bg-[hsl(var(--card))]'
                                }`}>{s.label}</button>
                        ))}
                    </div>
                    <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
                        {filteredTickets.length === 0 ? (
                            <div className="py-16 text-center text-sm text-[hsl(var(--muted-foreground))]">Aucun ticket.</div>
                        ) : (
                            <div className="divide-y divide-black/5">
                                {filteredTickets.map((t) => (
                                    <button key={t.id} onClick={() => setSelectedTicket(t)}
                                        className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-black/[0.02] transition-colors">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                                                <TicketStatusBadge status={t.status} />
                                                <span className="text-xs text-[hsl(var(--muted-foreground))]">{t.category} · {t.company}</span>
                                                {t.unread_for_client && (
                                                    <span className="text-xs text-[hsl(var(--primary))] font-medium">En attente du client</span>
                                                )}
                                            </div>
                                            <div className="font-medium text-sm truncate">{t.subject}</div>
                                            <div className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                                                {t.contact_name} · {t.messages.length} message{t.messages.length !== 1 ? 's' : ''} · {formatDate(t.updated_at)}
                                            </div>
                                        </div>
                                        {t.satisfaction && (
                                            <span className="shrink-0 text-xs text-green-600 font-medium">NPS {t.satisfaction.nps} · {t.satisfaction.csat}★</span>
                                        )}
                                        <ChevronDown className="h-4 w-4 text-[hsl(var(--muted-foreground))] shrink-0 -rotate-90" />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            ) : tab === 'feedback' ? (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden">
                    {feedback.length === 0 ? (
                        <div className="py-16 text-center text-sm text-[hsl(var(--muted-foreground))]">Aucun feedback pour l'instant.</div>
                    ) : (
                        <div className="divide-y divide-black/5">
                            {feedback.map((f) => (
                                <div key={f.id} className="px-5 py-4">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-purple-100 text-purple-700">{f.category}</span>
                                        <span className="text-xs text-[hsl(var(--muted-foreground))]">{f.company} · {f.contact_name}</span>
                                        <span className="ml-auto text-xs text-[hsl(var(--muted-foreground))]">{formatDate(f.created_at)}</span>
                                    </div>
                                    <p className="text-sm leading-[1.65]">{f.content}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ) : tab === 'indicateurs' ? (
                <StatsPanel stats={stats} formatDate={formatDate} />
            ) : null}
        </section>
    );
}
