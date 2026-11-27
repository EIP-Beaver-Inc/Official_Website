import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, FileText, Loader2, Mail, PackageCheck, RefreshCw, Send, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
    adminDeliver,
    adminListRequests,
    adminReleaseInfo,
    adminResendDelivery,
    adminSendQuote,
    adminSetRequestStatus,
} from '@/lib/api';

// Du devis à la livraison : nouveau → devis envoyé → commandé → livré (ou annulé).
const STATUS = {
    nouveau: { label: 'Nouveau', cls: 'bg-blue-100 text-blue-800' },
    devis_envoye: { label: 'Devis envoyé', cls: 'bg-amber-100 text-amber-800' },
    commande: { label: 'Commandé', cls: 'bg-violet-100 text-violet-800' },
    livre: { label: 'Livré', cls: 'bg-green-100 text-green-800' },
    annule: { label: 'Annulé', cls: 'bg-gray-100 text-gray-600' },
};

const btn = 'inline-flex items-center gap-1.5 rounded-full px-3 h-8 text-xs font-medium transition-colors disabled:opacity-50';
const primaryBtn = `${btn} bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))]`;
const ghostBtn = `${btn} border border-black/10 hover:bg-[hsl(var(--background))]`;

// Le message du serveur ; une erreur de validation (422) arrive en liste de champs.
const FIELD_NAMES = { amount_ht: 'Montant', details: 'Détail', validity_days: 'Validité', seats: 'Postes',
    licence_months: 'Durée de la licence', licence_expires: 'Fin de la licence' };
const errorText = (err, fallback) => {
    const detail = err?.response?.data?.detail;
    if (Array.isArray(detail)) {
        return detail.map((d) => `${FIELD_NAMES[d.loc?.[d.loc.length - 1]] || d.loc?.join('.')} : valeur invalide`).join(' · ');
    }
    return typeof detail === 'string' && detail ? detail : fallback;
};

// « 4 500 », « 4500,50 € », « 4 500 € HT » -> 4500.5 ; NaN si ce n'est pas un montant.
const parseAmount = (text) => {
    const cleaned = String(text).replace(/[\s\u00a0\u202f€]|HT/gi, '').replace(',', '.');
    return cleaned && /^\d+(\.\d+)?$/.test(cleaned) ? Number(cleaned) : NaN;
};
const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString('fr-FR') : '-');
const PLATFORMS = { windows: 'Windows', linux: 'Linux' };
// "Windows 2.1.0 · Linux 2.1.0": the installers the delivery will link to.
const installerNames = (release) => Object.entries(release?.installers || {})
    .filter(([, info]) => info)
    .map(([platform, info]) => `${PLATFORMS[platform] || platform} ${info.version}`)
    .join(' · ');
const oneYearFromNow = () => {
    const d = new Date();
    d.setFullYear(d.getFullYear() + 1);
    return d.toISOString().slice(0, 10);
};

function Modal({ title, children, onClose }) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-2xl border border-black/5 bg-[hsl(var(--background))] shadow-[0_24px_60px_rgba(17,17,17,0.18)] p-6">
                <div className="flex items-start justify-between mb-5">
                    <h2 className="font-heading text-2xl">{title}</h2>
                    <button onClick={onClose} className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">
                        <XCircle className="h-5 w-5" />
                    </button>
                </div>
                {children}
            </div>
        </div>
    );
}

// « 1 an, 2 postes », comme dans le mail du devis.
function licenceTerms(months, seats = 1) {
    const duration = !months ? 'sans limite de durée'
        : months % 12 === 0 ? `${months / 12} an${months >= 24 ? 's' : ''}` : `${months} mois`;
    return `${duration}, ${seats} poste${seats > 1 ? 's' : ''}`;
}

function QuoteModal({ request, onClose, onDone }) {
    const [form, setForm] = useState({ amount_ht: '', details: '', validity_days: 30, licence_months: '12', seats: 1 });
    const [busy, setBusy] = useState(false);
    const set = (f) => (e) => setForm((s) => ({ ...s, [f]: e.target.value }));

    const submit = async (e) => {
        e.preventDefault();
        const amount = parseAmount(form.amount_ht);
        if (!(amount > 0)) {
            toast.error('Montant invalide : saisissez un nombre, par exemple 4500 ou 4 500,50.');
            return;
        }
        setBusy(true);
        try {
            const r = await adminSendQuote(request.id, {
                amount_ht: amount,
                details: form.details,
                validity_days: Number(form.validity_days) || 30,
                licence_months: form.licence_months ? Number(form.licence_months) : null,
                seats: Number(form.seats) || 1,
            });
            toast[r.email_status === 'sent' ? 'success' : 'warning'](
                r.email_status === 'sent' ? `Devis envoyé à ${request.email}.` : `Devis enregistré, mais le mail n'est pas parti (${r.email_status}).`,
            );
            onDone();
        } catch (err) {
            toast.error(errorText(err, "Envoi du devis impossible."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <Modal title={`Devis · ${request.entreprise}`} onClose={onClose}>
            <form onSubmit={submit} className="space-y-4">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                    Envoyé par mail à {request.email}. Le client répond à ce mail pour commander (copie dans la boîte Beaver).
                    Quand vous cochez « Commande reçue », il reçoit aussitôt le logiciel avec cette licence.
                </p>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Montant HT (€)</Label>
                        <Input required inputMode="decimal" value={form.amount_ht} onChange={set('amount_ht')} placeholder="4500" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Validité (jours)</Label>
                        <Input type="number" min="1" max="365" value={form.validity_days} onChange={set('validity_days')} />
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Durée de la licence</Label>
                        <select value={form.licence_months} onChange={set('licence_months')}
                            className="h-10 rounded-md border border-black/10 bg-transparent px-3 text-sm">
                            <option value="12">1 an</option>
                            <option value="24">2 ans</option>
                            <option value="36">3 ans</option>
                            <option value="">Sans limite</option>
                        </select>
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Postes</Label>
                        <Input type="number" min="1" max="100" value={form.seats} onChange={set('seats')} />
                    </div>
                </div>
                <div className="flex flex-col gap-1.5">
                    <Label className="label-caps">Détail de l'offre</Label>
                    <Textarea required rows={5} value={form.details} onChange={set('details')}
                        placeholder="Licence logiciel 1 an, 1 poste · Installation et réglage sur site · Support par mail" />
                </div>
                <button type="submit" disabled={busy} className={`${primaryBtn} h-10 px-5 text-sm`}>
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    Envoyer le devis
                </button>
            </form>
        </Modal>
    );
}

function DeliverModal({ request, release, onClose, onDone }) {
    const [unlimited, setUnlimited] = useState(false);
    const [form, setForm] = useState({ licence_expires: oneYearFromNow(), seats: 1, customer: request.entreprise });
    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState(null);
    const set = (f) => (e) => setForm((s) => ({ ...s, [f]: e.target.value }));
    const blocked = !release?.licensing_configured || !release?.latest;
    const installers = installerNames(release);

    const submit = async (e) => {
        e.preventDefault();
        setBusy(true);
        try {
            const r = await adminDeliver(request.id, {
                licence_expires: unlimited ? null : form.licence_expires,
                seats: Number(form.seats) || 1,
                customer: form.customer || null,
            });
            setResult(r);
            onDone();
        } catch (err) {
            toast.error(errorText(err, 'Livraison impossible.'));
        } finally {
            setBusy(false);
        }
    };

    if (result) {
        return (
            <Modal title="Commande livrée" onClose={onClose}>
                <p className="text-sm mb-4">
                    {result.email_status === 'sent'
                        ? `Licence (qui ouvre aussi l'espace client) et lien de téléchargement envoyés à ${request.email}.`
                        : `Le mail n'est pas parti (${result.email_status}) : transmettez ces éléments au client.`}
                </p>
                <div className="space-y-3 text-xs">
                    <div>
                        <div className="label-caps mb-1">Licence {result.licence_id}</div>
                        <div className="font-mono break-all rounded-lg border border-black/10 bg-[hsl(var(--card))] p-2">{result.licence_key}</div>
                    </div>
                    {Object.entries(result.downloads || { windows: result.download }).map(([platform, link]) => (
                        <div key={platform}>
                            <div className="label-caps mb-1">Téléchargement {PLATFORMS[platform]} (Beaver {link.version})</div>
                            <div className="font-mono break-all rounded-lg border border-black/10 bg-[hsl(var(--card))] p-2">{link.url}</div>
                        </div>
                    ))}
                </div>
            </Modal>
        );
    }

    return (
        <Modal title={`Livrer · ${request.entreprise}`} onClose={onClose}>
            {blocked && (
                <div className="mb-4 flex gap-2 rounded-xl bg-amber-50 border border-amber-200 p-3 text-sm text-amber-900">
                    <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>
                        {!release?.licensing_configured
                            ? "La clé de signature des licences (LICENCE_PRIVATE_KEY) n'est pas configurée sur le serveur."
                            : `Aucun installateur (BeaverSetup-x.y.z.exe ou BeaverSetup-x.y.z-linux.run) dans ${release.releases_dir}.`}
                    </span>
                </div>
            )}
            <form onSubmit={submit} className="space-y-4">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                    Émet la licence, crée l'accès à l'espace client et envoie à {request.email} un lien de téléchargement
                    par installateur publié{installers ? ` (${installers})` : ''}.
                </p>
                <div className="flex flex-col gap-1.5">
                    <Label className="label-caps">Titulaire (affiché dans le logiciel)</Label>
                    <Input value={form.customer} onChange={set('customer')} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Fin de la licence</Label>
                        <Input type="date" disabled={unlimited} value={form.licence_expires} onChange={set('licence_expires')} />
                        <label className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
                            <input type="checkbox" checked={unlimited} onChange={(e) => setUnlimited(e.target.checked)} />
                            Sans limite de durée
                        </label>
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Postes</Label>
                        <Input type="number" min="1" max="100" value={form.seats} onChange={set('seats')} />
                    </div>
                </div>
                <button type="submit" disabled={busy || blocked} className={`${primaryBtn} h-10 px-5 text-sm`}>
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <PackageCheck className="h-4 w-4" />}
                    Livrer la commande
                </button>
            </form>
        </Modal>
    );
}

export default function OrdersPanel() {
    const [rows, setRows] = useState([]);
    const [release, setRelease] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [quoteFor, setQuoteFor] = useState(null);
    const [deliverFor, setDeliverFor] = useState(null);
    const [busyId, setBusyId] = useState(null);

    const refresh = useCallback(async () => {
        setLoading(true);
        try {
            const [r, rel] = await Promise.all([adminListRequests(), adminReleaseInfo()]);
            setRows(r);
            setRelease(rel);
        } catch (err) {
            toast.error(errorText(err, 'Chargement des commandes impossible.'));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refresh();
    }, [refresh]);

    const act = async (id, fn, ok) => {
        setBusyId(id);
        try {
            await fn();
            toast.success(ok);
            refresh();
        } catch (err) {
            toast.error(errorText(err, 'Action impossible.'));
        } finally {
            setBusyId(null);
        }
    };

    // « Commande reçue » : le serveur livre aussitôt (licence du devis, qui ouvre aussi l'espace client, et lien).
    const confirmOrder = async (r) => {
        const terms = r.quote ? licenceTerms(r.quote.licence_months, r.quote.seats) : 'licence 1 an, 1 poste';
        if (!window.confirm(`Commande reçue de ${r.entreprise} ?

${r.email} recevra aussitôt par mail le lien de `
            + `téléchargement et sa licence (${terms}), qui lui ouvre aussi son espace client.`)) return;
        setBusyId(r.id);
        try {
            const out = await adminSetRequestStatus(r.id, 'commande');
            if (!out.delivered) {
                toast.error(`Commande enregistrée, mais la livraison n'a pas pu partir : ${out.delivery_error}`);
            } else if (out.email_status !== 'sent') {
                toast.warning(`Commande livrée, mais le mail n'est pas parti (${out.email_status}) : renvoyez-le.`);
            } else {
                toast.success(`Commande livrée : logiciel et licence envoyés à ${r.email}.`);
            }
            refresh();
        } catch (err) {
            toast.error(errorText(err, 'Action impossible.'));
        } finally {
            setBusyId(null);
        }
    };

    const shown = filter ? rows.filter((r) => r.status === filter) : rows;

    return (
        <div>
            {quoteFor && <QuoteModal request={quoteFor} onClose={() => setQuoteFor(null)} onDone={() => { setQuoteFor(null); refresh(); }} />}
            {deliverFor && <DeliverModal request={deliverFor} release={release} onClose={() => setDeliverFor(null)} onDone={refresh} />}

            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div className="flex flex-wrap gap-2">
                    {[['', 'Toutes'], ...Object.entries(STATUS).map(([k, v]) => [k, v.label])].map(([k, label]) => (
                        <button key={k || 'all'} onClick={() => setFilter(k)}
                            className={`${btn} ${filter === k ? 'bg-[hsl(var(--foreground))] text-[hsl(var(--background))]' : 'border border-black/10'}`}>
                            {label}
                        </button>
                    ))}
                </div>
                <div className="flex items-center gap-3 text-xs text-[hsl(var(--muted-foreground))]">
                    {release && (
                        <span className="inline-flex items-center gap-1.5">
                            {release.latest && release.licensing_configured
                                ? <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                                : <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />}
                            {release.latest ? `Installateurs : ${installerNames(release)}` : 'Aucun installateur'}
                            {release.licensing_configured ? '' : ' · signature non configurée'}
                        </span>
                    )}
                    <button onClick={refresh} className={ghostBtn}><RefreshCw className="h-3.5 w-3.5" /> Actualiser</button>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center py-16"><Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--muted-foreground))]" /></div>
            ) : shown.length === 0 ? (
                <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-10 text-center text-sm text-[hsl(var(--muted-foreground))]">
                    Aucune demande de devis{filter ? ' dans cet état' : ''}.
                </div>
            ) : (
                <ul className="space-y-3">
                    {shown.map((r) => {
                        const st = STATUS[r.status] || STATUS.nouveau;
                        const busy = busyId === r.id;
                        return (
                            <li key={r.id} className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-4 sm:p-5">
                                <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <span className="font-heading text-lg">{r.entreprise}</span>
                                            <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${st.cls}`}>{st.label}</span>
                                        </div>
                                        <div className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                                            {r.nom} · <a className="underline" href={`mailto:${r.email}`}>{r.email}</a>
                                            {r.telephone ? ` · ${r.telephone}` : ''} · reçue le {fmtDate(r.created_at)}
                                        </div>
                                        {(r.taille_scierie || r.volume) && (
                                            <div className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                                                {[r.taille_scierie, r.volume].filter(Boolean).join(' · ')}
                                            </div>
                                        )}
                                        {r.message && <p className="mt-2 text-sm whitespace-pre-wrap">{r.message}</p>}
                                        {r.quote && (
                                            <div className="mt-2 text-xs inline-flex items-center gap-1.5 text-[hsl(var(--muted-foreground))]">
                                                <FileText className="h-3.5 w-3.5" />
                                                Devis {r.quote.amount_ht.toLocaleString('fr-FR')} € HT ({licenceTerms(r.quote.licence_months, r.quote.seats)}), envoyé le {fmtDate(r.quote.sent_at)}, valable jusqu'au {fmtDate(r.quote.valid_until)}
                                            </div>
                                        )}
                                        {r.delivery_error && r.status === 'commande' && (
                                            <div className="mt-2 flex gap-1.5 rounded-lg bg-amber-50 border border-amber-200 px-2 py-1.5 text-xs text-amber-900">
                                                <AlertTriangle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                                                <span>Livraison automatique impossible : {r.delivery_error} Corrigez puis cliquez « Livrer ».</span>
                                            </div>
                                        )}
                                        {r.delivery && (
                                            <div className="mt-1 text-xs inline-flex items-center gap-1.5 text-[hsl(var(--muted-foreground))]">
                                                <PackageCheck className="h-3.5 w-3.5" />
                                                Licence {r.delivery.licence_id}, {r.delivery.licence_expires ? `jusqu'au ${fmtDate(r.delivery.licence_expires)}` : 'sans limite'}, {r.delivery.seats} poste(s) · livrée le {fmtDate(r.delivery.delivered_at)}
                                                {r.delivery.email_status !== 'sent' ? ` · mail : ${r.delivery.email_status}` : ''}
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {['nouveau', 'devis_envoye', 'commande'].includes(r.status) && (
                                            <button className={ghostBtn} disabled={busy} onClick={() => setQuoteFor(r)}>
                                                <Send className="h-3.5 w-3.5" /> {r.quote ? 'Renvoyer un devis' : 'Envoyer un devis'}
                                            </button>
                                        )}
                                        {['nouveau', 'devis_envoye'].includes(r.status) && (
                                            <button className={primaryBtn} disabled={busy} onClick={() => confirmOrder(r)}>
                                                {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
                                                Commande reçue : livrer
                                            </button>
                                        )}
                                        {r.status === 'commande' && (
                                            <button className={primaryBtn} disabled={busy} onClick={() => setDeliverFor(r)}>
                                                <PackageCheck className="h-3.5 w-3.5" /> Livrer
                                            </button>
                                        )}
                                        {r.status === 'livre' && (
                                            <button className={ghostBtn} disabled={busy}
                                                onClick={() => act(r.id, () => adminResendDelivery(r.id), `Mail de livraison renvoyé à ${r.email}.`)}>
                                                <Mail className="h-3.5 w-3.5" /> Renvoyer le mail
                                            </button>
                                        )}
                                        {!['livre', 'annule'].includes(r.status) && (
                                            <button className={ghostBtn} disabled={busy}
                                                onClick={() => window.confirm('Annuler ce dossier ?') &&
                                                    act(r.id, () => adminSetRequestStatus(r.id, 'annule'), 'Dossier annulé.')}>
                                                <XCircle className="h-3.5 w-3.5" /> Annuler
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
}
