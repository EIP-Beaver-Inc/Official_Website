import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, ArrowRight, Loader2, Download, BookOpen, LifeBuoy } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { validateBetaKey, betaLogin } from '@/lib/api';
import PageHero from '@/components/PageHero';

function KeyInput({ value, onChange }) {
    return (
        <div className="flex flex-col gap-1.5">
            <Label className="label-caps">
                Clé d'accès beta <span className="text-[hsl(var(--primary))]">*</span>
            </Label>
            <Input
                value={value}
                onChange={onChange}
                placeholder="XXXX-XXXX-XXXX-XXXX"
                className="font-mono tracking-widest uppercase bg-[hsl(var(--background))]"
                required
                autoFocus
            />
        </div>
    );
}

function LoginForm() {
    const navigate = useNavigate();
    const [key, setKey] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!key.trim()) return;
        try {
            setSubmitting(true);
            const data = await betaLogin(key);
            localStorage.setItem('beaver_beta_token', data.session_token);
            navigate('/account');
        } catch (err) {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail;
            if (status === 400) toast.error('Clé non encore activée, utilisez l\'onglet "Première connexion".');
            else if (status === 404) toast.error('Clé invalide. Vérifiez votre email de Beaver.');
            else if (status === 403) toast.error('Cette clé a été révoquée. Contactez Beaver.');
            else if (status === 410) toast.error('Cette clé est expirée. Contactez Beaver.');
            else toast.error(detail || 'Erreur de connexion.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <KeyInput value={key} onChange={(e) => setKey(e.target.value)} />
            <div className="flex justify-end pt-2">
                <button
                    type="submit" disabled={submitting}
                    className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-6 h-12 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                >
                    {submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Connexion…</> : <>Accéder à mon espace <ArrowRight className="ml-2 h-4 w-4" /></>}
                </button>
            </div>
        </form>
    );
}

function RegisterForm() {
    const navigate = useNavigate();
    const [form, setForm] = useState({ key: '', company: '', contact_name: '', email: '', phone: '' });
    const [submitting, setSubmitting] = useState(false);

    const set = (field) => (e) => setForm((s) => ({ ...s, [field]: e.target.value }));

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!form.key || !form.company || !form.contact_name || !form.email) {
            toast.error('Tous les champs obligatoires doivent être remplis.');
            return;
        }
        try {
            setSubmitting(true);
            const data = await validateBetaKey(form);
            localStorage.setItem('beaver_beta_token', data.session_token);
            navigate('/account');
        } catch (err) {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail;
            if (status === 404) toast.error('Clé invalide. Vérifiez votre email de Beaver.');
            else if (status === 409) toast.error('Cette clé a déjà été activée, utilisez l\'onglet "Se connecter".');
            else if (status === 410) toast.error('Cette clé est expirée. Contactez Beaver.');
            else if (status === 403) toast.error('Cette clé a été révoquée. Contactez Beaver.');
            else toast.error(detail || 'Erreur lors de l\'activation.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <KeyInput value={form.key} onChange={set('key')} />
            <div className="pt-2 border-t border-black/5">
                <p className="label-caps mb-4">Informations d'enregistrement</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Entreprise <span className="text-[hsl(var(--primary))]">*</span></Label>
                        <Input value={form.company} onChange={set('company')} placeholder="Scierie Dupont" className="bg-[hsl(var(--background))]" required />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Nom du contact <span className="text-[hsl(var(--primary))]">*</span></Label>
                        <Input value={form.contact_name} onChange={set('contact_name')} placeholder="Jean Martin" className="bg-[hsl(var(--background))]" required />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Email <span className="text-[hsl(var(--primary))]">*</span></Label>
                        <Input type="email" value={form.email} onChange={set('email')} placeholder="contact@scierie.fr" className="bg-[hsl(var(--background))]" required />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">Téléphone</Label>
                        <Input value={form.phone} onChange={set('phone')} placeholder="+33 6 12 34 56 78" className="bg-[hsl(var(--background))]" />
                    </div>
                </div>
            </div>
            <div className="flex justify-end pt-2">
                <button
                    type="submit" disabled={submitting}
                    className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-6 h-12 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                >
                    {submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Activation…</> : <>Activer la clé <ArrowRight className="ml-2 h-4 w-4" /></>}
                </button>
            </div>
        </form>
    );
}

const PERKS = [
    { Icon: Download, title: "L'application Beaver", text: "Téléchargez la dernière version de l'application." },
    { Icon: BookOpen, title: 'Guides et tutoriels', text: 'La documentation pour installer et prendre en main Beaver.' },
    { Icon: LifeBuoy, title: 'Suivi des tickets', text: "Posez vos questions et suivez les réponses de l'équipe." },
];

export default function Beta() {
    const [tab, setTab] = useState('login');

    return (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
            <div className="lg:col-span-6">
                <PageHero
                    kicker="Accès beta · Beaver"
                    title={
                        <>
                            Votre espace <span className="text-primary">client.</span>
                        </>
                    }
                    subtitle="Connectez-vous avec votre clé d'accès beta pour télécharger l'application, consulter les guides et suivre vos tickets."
                />
                <ul className="mt-10 space-y-3" data-animate="fade-up">
                    {PERKS.map(({ Icon, title, text }) => (
                        <li key={title} className="flex items-start gap-4 rounded-2xl border border-black/5 bg-card/70 p-4">
                            <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                                <Icon className="h-4 w-4" />
                            </span>
                            <div>
                                <div className="font-display font-semibold tracking-[-0.02em]">{title}</div>
                                <div className="mt-0.5 text-sm text-muted-foreground">{text}</div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="lg:col-span-6 lg:sticky lg:top-32" data-animate="fade-up">
                <div className="rounded-[2rem] border border-black/5 bg-card p-6 sm:p-8 shadow-[0_30px_70px_-40px_rgba(60,35,20,0.4)]">
                    {/* Tabs */}
                    <div className="grid grid-cols-2 gap-1 rounded-full bg-background p-1 border border-black/5">
                        {[
                            { id: 'login', label: 'Se connecter' },
                            { id: 'register', label: 'Première connexion' },
                        ].map(({ id, label }) => (
                            <button
                                key={id}
                                type="button"
                                onClick={() => setTab(id)}
                                className={`rounded-full py-2.5 text-sm font-medium transition-all duration-300 ${
                                    tab === id ? 'bg-primary text-primary-foreground shadow-[0_6px_18px_rgba(168,65,42,0.25)]' : 'text-muted-foreground hover:text-foreground'
                                }`}
                            >
                                {label}
                            </button>
                        ))}
                    </div>

                    <div className="mt-8 flex items-center gap-3 mb-6">
                        <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                            <KeyRound className="h-5 w-5 text-primary" />
                        </span>
                        <span className="font-display font-semibold text-lg tracking-[-0.02em]">
                            {tab === 'login' ? 'Connexion avec votre clé' : 'Activation de votre clé'}
                        </span>
                    </div>

                    {tab === 'login' ? <LoginForm /> : <RegisterForm />}
                </div>

                <p className="mt-6 text-center text-sm text-muted-foreground">
                    Pas encore de clé ?{' '}
                    <a href="/contact" className="text-primary underline underline-offset-4">
                        Contactez-nous
                    </a>
                </p>
            </div>
        </section>
    );
}
