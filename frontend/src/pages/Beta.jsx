import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, ArrowRight, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { validateBetaKey } from '@/lib/api';

export default function Beta() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        key: '',
        company: '',
        contact_name: '',
        email: '',
        phone: '',
    });
    const [submitting, setSubmitting] = useState(false);

    const handleChange = (field) => (e) =>
        setForm((s) => ({ ...s, [field]: e.target.value }));

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!form.key || !form.company || !form.contact_name || !form.email) {
            toast.error('Tous les champs obligatoires doivent être remplis.');
            return;
        }
        try {
            setSubmitting(true);
            const data = await validateBetaKey(form);
            sessionStorage.setItem('beaver_beta_token', data.session_token);
            navigate('/beta/download');
        } catch (err) {
            const status = err?.response?.status;
            const detail = err?.response?.data?.detail;
            if (status === 404) toast.error('Clé invalide. Vérifiez votre email de Beaver.');
            else if (status === 409) toast.error('Cette clé a déjà été activée.');
            else if (status === 410) toast.error('Cette clé est expirée. Contactez Beaver.');
            else toast.error(detail || 'Erreur lors de la validation.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <section className="max-w-2xl mx-auto px-4 sm:px-6 py-12 sm:py-20">
            <div data-animate="fade-up">
                <div className="label-caps">
                    <span className="text-[hsl(var(--primary))]">Accès beta</span> · Beaver
                </div>
                <h1 className="mt-3 font-heading text-4xl sm:text-5xl leading-[1.04] tracking-[-0.02em]">
                    Activer votre <span className="brick-italic">clé d'accès</span>
                </h1>
                <p className="mt-5 text-[hsl(var(--muted-foreground))] leading-[1.7]">
                    Vous avez reçu une clé beta par email. Entrez-la ci-dessous pour accéder au téléchargement de l'application et aux guides d'utilisation.
                </p>
            </div>

            <div
                data-animate="fade-up"
                className="mt-10 rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-8 shadow-[0_18px_44px_rgba(17,17,17,0.06)]"
            >
                <div className="flex items-center gap-3 mb-6">
                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[hsl(var(--primary)/0.1)]">
                        <KeyRound className="h-5 w-5 text-[hsl(var(--primary))]" />
                    </span>
                    <span className="font-medium">Validation de clé</span>
                </div>

                <form onSubmit={onSubmit} className="space-y-4">
                    <div className="flex flex-col gap-1.5">
                        <Label className="label-caps">
                            Clé beta <span className="text-[hsl(var(--primary))]">*</span>
                        </Label>
                        <Input
                            value={form.key}
                            onChange={handleChange('key')}
                            placeholder="XXXX-XXXX-XXXX-XXXX"
                            className="font-mono tracking-widest uppercase bg-[hsl(var(--background))]"
                            required
                            autoFocus
                        />
                    </div>

                    <div className="pt-2 border-t border-black/5">
                        <p className="label-caps mb-4">Informations d'enregistrement</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">
                                    Entreprise <span className="text-[hsl(var(--primary))]">*</span>
                                </Label>
                                <Input
                                    value={form.company}
                                    onChange={handleChange('company')}
                                    placeholder="Scierie Dupont"
                                    className="bg-[hsl(var(--background))]"
                                    required
                                />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">
                                    Nom du contact <span className="text-[hsl(var(--primary))]">*</span>
                                </Label>
                                <Input
                                    value={form.contact_name}
                                    onChange={handleChange('contact_name')}
                                    placeholder="Jean Martin"
                                    className="bg-[hsl(var(--background))]"
                                    required
                                />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">
                                    Email <span className="text-[hsl(var(--primary))]">*</span>
                                </Label>
                                <Input
                                    type="email"
                                    value={form.email}
                                    onChange={handleChange('email')}
                                    placeholder="contact@scierie.fr"
                                    className="bg-[hsl(var(--background))]"
                                    required
                                />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label className="label-caps">Téléphone</Label>
                                <Input
                                    value={form.phone}
                                    onChange={handleChange('phone')}
                                    placeholder="+33 6 12 34 56 78"
                                    className="bg-[hsl(var(--background))]"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="pt-2 flex justify-end">
                        <button
                            type="submit"
                            disabled={submitting}
                            className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-6 h-12 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                        >
                            {submitting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Validation…
                                </>
                            ) : (
                                <>
                                    Activer la clé
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>

            <p className="mt-6 text-center text-sm text-[hsl(var(--muted-foreground))]">
                Pas encore de clé ?{' '}
                <a href="/contact" className="text-[hsl(var(--primary))] underline underline-offset-4">
                    Contactez-nous
                </a>
            </p>
        </section>
    );
}
