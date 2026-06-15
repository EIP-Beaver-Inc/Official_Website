import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Key, Users, Copy, Check, LogOut, Loader2, RefreshCw, Eye, EyeOff, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { adminListKeys, adminListClients, adminGenerateKey, adminDeleteClient } from '@/lib/api';

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

export default function Admin() {
    const navigate = useNavigate();
    const [tab, setTab] = useState('keys');
    const [keys, setKeys] = useState([]);
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('beaver_admin_token');
        if (!token) {
            navigate('/admin/login', { replace: true });
        }
    }, [navigate]);

    const refresh = useCallback(async () => {
        setLoading(true);
        try {
            const [k, c] = await Promise.all([adminListKeys(), adminListClients()]);
            setKeys(k);
            setClients(c);
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

            <div className="grid grid-cols-3 gap-4 mb-8">
                {[
                    { label: 'Clés générées', value: keys.length },
                    { label: 'Clés disponibles', value: unusedCount },
                    { label: 'Beta testeurs', value: activeCount },
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
                    ].map(({ id, label, icon: Icon }) => (
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
            ) : (
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
            )}
        </section>
    );
}
