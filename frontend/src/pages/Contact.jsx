import { useState } from 'react';
import { ArrowRight, Check, Mail, MapPin, Phone } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { submitContact } from '@/lib/api';
import PageHero from '@/components/PageHero';
import BrickPanel from '@/components/BrickPanel';

export default function Contact() {
    const [form, setForm] = useState({ nom: '', entreprise: '', email: '', telephone: '', message: '' });
    const [submitting, setSubmitting] = useState(false);
    const [done, setDone] = useState(false);

    const handleChange = (key) => (e) => setForm((s) => ({ ...s, [key]: e.target.value }));

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!form.nom || !form.email || !form.message) {
            toast.error('Nom, email et message sont requis.');
            return;
        }
        try {
            setSubmitting(true);
            await submitContact(form);
            toast.success('Message envoyé, merci !');
            setDone(true);
            setForm({ nom: '', entreprise: '', email: '', telephone: '', message: '' });
        } catch (err) {
            const detail = err?.response?.data?.detail || "Erreur d'envoi du message.";
            toast.error(typeof detail === 'string' ? detail : 'Erreur de validation.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <section data-testid="contact-page" className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
            <PageHero
                kicker="Contact · Équipe Beaver"
                title={
                    <>
                        Une question, un cas <span className="text-primary">complexe&nbsp;?</span>
                    </>
                }
                subtitle="Écrivez-nous : nos ingénieurs répondent en moins de 48h. Pour toute demande de devis ligne de production, utilisez le bouton « Demander un devis » en haut de page."
            />

            <div className="mt-14 sm:mt-20 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
                <div className="lg:col-span-7" data-animate="fade-up">
                    <form
                        data-testid="contact-form"
                        onSubmit={onSubmit}
                        className="rounded-[2rem] border border-black/5 bg-card p-6 sm:p-10 shadow-[0_30px_70px_-40px_rgba(60,35,20,0.35)]"
                    >
                        <div className="font-mono-ui text-[11px] uppercase tracking-[0.14em] text-muted-foreground">Votre message</div>
                        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div className="flex flex-col gap-2">
                                <Label htmlFor="c-nom" className="label-caps">Nom complet</Label>
                                <Input id="c-nom" data-testid="contact-input-nom" value={form.nom} onChange={handleChange('nom')} required className="bg-background" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <Label htmlFor="c-ent" className="label-caps">Entreprise</Label>
                                <Input id="c-ent" data-testid="contact-input-entreprise" value={form.entreprise} onChange={handleChange('entreprise')} className="bg-background" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <Label htmlFor="c-email" className="label-caps">Email</Label>
                                <Input id="c-email" type="email" data-testid="contact-input-email" value={form.email} onChange={handleChange('email')} required className="bg-background" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <Label htmlFor="c-tel" className="label-caps">Téléphone</Label>
                                <Input id="c-tel" data-testid="contact-input-telephone" value={form.telephone} onChange={handleChange('telephone')} className="bg-background" />
                            </div>
                            <div className="sm:col-span-2 flex flex-col gap-2">
                                <Label htmlFor="c-msg" className="label-caps">Message</Label>
                                <Textarea
                                    id="c-msg"
                                    data-testid="contact-input-message"
                                    rows={6}
                                    value={form.message}
                                    onChange={handleChange('message')}
                                    required
                                    className="bg-background"
                                    placeholder="Décrivez votre besoin, votre ligne de production, vos essences…"
                                />
                            </div>
                        </div>
                        <div className="mt-8 flex items-center justify-between gap-4">
                            <span className="hidden sm:block font-mono-ui text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Réponse sous 48h ouvrées</span>
                            <button
                                type="submit"
                                disabled={submitting}
                                data-testid="contact-form-submit-button"
                                className="ml-auto inline-flex items-center justify-center rounded-full bg-primary hover:bg-[hsl(14_66%_38%)] hover:scale-[1.02] disabled:opacity-60 disabled:hover:scale-100 text-primary-foreground px-7 h-12 text-sm font-medium transition-[background-color,transform] shadow-[0_8px_24px_rgba(168,65,42,0.25)]"
                            >
                                {submitting ? 'Envoi…' : 'Envoyer le message'}
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </button>
                        </div>
                        {done && (
                            <div
                                data-testid="contact-success-message"
                                className="mt-6 flex items-start gap-3 rounded-2xl border border-[hsl(120_28%_34%/0.25)] bg-[hsl(120_28%_34%/0.06)] p-4 text-sm"
                            >
                                <Check className="h-4 w-4 mt-0.5 text-[hsl(120_30%_32%)]" />
                                Merci, votre message a bien été envoyé. Nous reviendrons vers vous sous 48h.
                            </div>
                        )}
                    </form>
                </div>

                <aside className="lg:col-span-5 flex flex-col gap-6" data-animate="fade-up">
                    <BrickPanel className="p-6 sm:p-8">
                        <div>
                            <div className="font-mono-ui text-[11px] uppercase tracking-[0.14em] text-primary-foreground/70">Coordonnées</div>
                            <ul className="mt-6 space-y-5">
                                {[
                                    { Icon: Mail, main: <a href="mailto:beaver.eip@gmail.com" className="hover:underline underline-offset-4">beaver.eip@gmail.com</a>, sub: 'Réponse sous 48h ouvrées' },
                                    { Icon: Phone, main: <span className="opacity-80">Bientôt disponible</span>, sub: 'Lun – Ven · 9h – 18h' },
                                    { Icon: MapPin, main: 'Lyon, 69007', sub: 'Rhône-Alpes · France' },
                                ].map(({ Icon, main, sub }, i) => (
                                    <li key={i} className="flex items-start gap-4">
                                        <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-foreground/10 border border-primary-foreground/20">
                                            <Icon className="h-4 w-4" />
                                        </span>
                                        <div>
                                            <div className="font-display font-semibold text-lg tracking-[-0.02em]">{main}</div>
                                            <div className="text-sm text-primary-foreground/70">{sub}</div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </BrickPanel>

                    <div className="rounded-[2rem] border border-black/5 bg-card p-6 sm:p-8">
                        <div className="font-mono-ui text-[11px] uppercase tracking-[0.14em] text-muted-foreground">Notre promesse</div>
                        <ul className="mt-5 space-y-3">
                            {[
                                'Réponse personnalisée par un ingénieur',
                                'Confidentialité totale (NDA sur demande)',
                                'Pas de prospection commerciale automatique',
                            ].map((p) => (
                                <li key={p} className="flex items-start gap-3 text-[15px]">
                                    <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                                        <Check className="h-3 w-3" strokeWidth={3} />
                                    </span>
                                    <span>{p}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </aside>
            </div>
        </section>
    );
}
