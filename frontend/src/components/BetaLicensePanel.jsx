import { useState } from 'react';
import { ArrowRight, Check, Clock, Copy, Download, Loader2, ShieldCheck } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { betaLicenseDownload, betaLicenseInfo } from '@/lib/api';

const CONTACT = 'betatest.beaver@gmail.com';
const PLATFORM_LABELS = { windows: 'Windows', macos: 'macOS', linux: 'Linux' };

function errorMessage(err) {
    const status = err?.response?.status;
    const data = err?.response?.data || {};
    if (status === 403 && data.status === 'expired') return 'Votre clé BETA a expiré.';
    if (status === 403 && data.status === 'revoked') return 'Votre clé BETA a été révoquée.';
    if (status === 403) return 'Clé BETA invalide. Vérifiez-la (format BETA-XXXX-XXXX-XXXX-XXXX).';
    if (status === 400) return 'Format de clé invalide : BETA-XXXX-XXXX-XXXX-XXXX.';
    if (status === 429 && data.detail === 'download_limit') return 'Nombre maximal de téléchargements atteint pour cette clé.';
    if (status === 429) {
        const minutes = Math.ceil(Number(err.response.headers?.['retry-after'] || 60) / 60);
        return `Trop de tentatives. Réessayez dans ${minutes} minute${minutes > 1 ? 's' : ''}.`;
    }
    if (status === 404) return 'Aucune version disponible pour cette plateforme pour le moment.';
    return 'Service momentanément indisponible. Réessayez plus tard.';
}

function formatDate(iso) {
    return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

function formatSize(bytes) {
    return bytes >= 1e9 ? `${(bytes / 1e9).toFixed(1)} Go` : `${Math.max(1, Math.round(bytes / 1e6))} Mo`;
}

function Sha({ value }) {
    const [copied, setCopied] = useState(false);
    const copy = async () => {
        try {
            await navigator.clipboard.writeText(value);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
        } catch {
            /* clipboard unavailable */
        }
    };
    return (
        <div className="mt-3 flex items-start gap-2">
            <code className="flex-1 break-all rounded-lg bg-background px-2.5 py-1.5 font-mono text-[11px] leading-relaxed text-muted-foreground">
                SHA-256 {value}
            </code>
            <button type="button" onClick={copy} aria-label="Copier l'empreinte SHA-256" className="mt-1 text-muted-foreground hover:text-foreground">
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </button>
        </div>
    );
}

export default function BetaLicensePanel() {
    // The key lives only in this component's state (never URL / cookie / localStorage).
    const [key, setKey] = useState('');
    const [info, setInfo] = useState(null);
    const [error, setError] = useState('');
    const [checking, setChecking] = useState(false);
    const [downloading, setDownloading] = useState('');

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!key.trim()) return;
        setError('');
        setInfo(null);
        try {
            setChecking(true);
            setInfo(await betaLicenseInfo(key));
        } catch (err) {
            setError(errorMessage(err));
        } finally {
            setChecking(false);
        }
    };

    const download = async (platform) => {
        try {
            setDownloading(platform);
            const d = await betaLicenseDownload(key, platform);
            setInfo((s) => ({ ...s, downloads_remaining: Math.max(0, s.downloads_remaining - 1) }));
            window.location.assign(d.url);
        } catch (err) {
            toast.error(errorMessage(err));
        } finally {
            setDownloading('');
        }
    };

    return (
        <div className="space-y-6">
            <form onSubmit={onSubmit} className="space-y-4">
                <div className="flex flex-col gap-1.5">
                    <Label htmlFor="beta-license-key" className="label-caps">
                        Entrez votre clé BETA <span className="text-[hsl(var(--primary))]">*</span>
                    </Label>
                    <Input
                        id="beta-license-key"
                        value={key}
                        onChange={(e) => setKey(e.target.value)}
                        placeholder="BETA-XXXX-XXXX-XXXX-XXXX"
                        autoComplete="off"
                        spellCheck={false}
                        className="font-mono tracking-widest uppercase bg-[hsl(var(--background))]"
                        required
                        autoFocus
                    />
                </div>
                <div className="flex justify-end pt-2">
                    <button
                        type="submit"
                        disabled={checking}
                        className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-6 h-12 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                    >
                        {checking ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Vérification…</> : <>Vérifier ma clé <ArrowRight className="ml-2 h-4 w-4" /></>}
                    </button>
                </div>
            </form>

            {error && (
                <div role="alert" className="rounded-2xl border border-[hsl(var(--primary)/0.25)] bg-[hsl(var(--primary)/0.06)] p-4 text-sm">
                    <p className="font-medium">{error}</p>
                    <p className="mt-1 text-muted-foreground">
                        Besoin d'aide ? Écrivez-nous à{' '}
                        <a href={`mailto:${CONTACT}`} className="text-primary underline underline-offset-4">{CONTACT}</a>
                    </p>
                </div>
            )}

            {info && (
                <div className="space-y-4">
                    <div className="flex items-start gap-3 rounded-2xl border border-[hsl(120_28%_34%/0.25)] bg-[hsl(120_28%_34%/0.06)] p-4 text-sm">
                        {info.activated ? <Clock className="h-4 w-4 mt-0.5 text-[hsl(120_30%_32%)]" /> : <ShieldCheck className="h-4 w-4 mt-0.5 text-[hsl(120_30%_32%)]" />}
                        <div>
                            {info.activated ? (
                                <p className="font-medium">
                                    Clé active : il vous reste {info.days_remaining} jour{info.days_remaining > 1 ? 's' : ''} d'accès
                                    {info.expires_at ? ` (jusqu'au ${formatDate(info.expires_at)})` : ''}.
                                </p>
                            ) : (
                                <p className="font-medium">
                                    Clé valide. La durée de {info.duration_days} jours démarre à la première ouverture du logiciel.
                                </p>
                            )}
                            {!info.activated && info.redeem_by && (
                                <p className="mt-1 text-muted-foreground">À activer avant le {formatDate(info.redeem_by)}.</p>
                            )}
                            <p className="mt-1 text-muted-foreground">
                                Téléchargements restants : {info.downloads_remaining}
                            </p>
                        </div>
                    </div>

                    {info.releases.length === 0 ? (
                        <p className="text-sm text-muted-foreground">Aucune version n'est disponible pour le moment. Revenez bientôt.</p>
                    ) : (
                        info.releases.map((r) => (
                            <div key={r.platform} className="rounded-2xl border border-black/5 bg-card/70 p-4">
                                <div className="flex items-center justify-between gap-4">
                                    <div>
                                        <div className="font-display font-semibold tracking-[-0.02em]">
                                            Beaver pour {PLATFORM_LABELS[r.platform] || r.platform}
                                        </div>
                                        <div className="text-sm text-muted-foreground">
                                            Version {r.version} · {formatSize(r.size)}
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => download(r.platform)}
                                        disabled={!!downloading || info.downloads_remaining <= 0}
                                        className="inline-flex shrink-0 items-center gap-2 rounded-full bg-primary text-primary-foreground hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 px-5 h-11 text-sm font-medium transition-colors"
                                    >
                                        {downloading === r.platform ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                                        Télécharger
                                    </button>
                                </div>
                                <Sha value={r.sha256} />
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
