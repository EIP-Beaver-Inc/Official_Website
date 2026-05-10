import { useState } from 'react';
import { ArrowRight, Mail, MapPin, Phone } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { submitContact } from '@/lib/api';

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
            toast.success('Message envoyé — merci !');
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
            <div data-animate="fade-up">
                <div className="label-caps">
                    <span className="text-[hsl(var(--primary))]">Contact</span> · Équipe Beaver
                </div>
                <h1 className="mt-3 font-heading text-4xl sm:text-5xl lg:text-6xl leading-[1.04] tracking-[-0.02em] max-w-3xl">
                    Une question, un cas <span className="brick-italic">complexe ?</span>
                </h1>
                <p className="mt-5 max-w-2xl text-[hsl(var(--muted-foreground))] leading-[1.7]">
                    Écrivez-nous : nos ingénieurs répondent en moins de 48h. Pour toute demande de démo ligne de production, utilisez le bouton « Demander une démo » en haut de page.
                </p>
            </div>

            <div className="mt-10 sm:mt-14 grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-7" data-animate="fade-up">
                    <form
                        data-testid="contact-form"
                        onSubmit={onSubmit}
                        className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-8 lg:p-10 shadow-[0_18px_44px_rgba(17,17,17,0.06)]"
                    >
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="flex flex-col gap-1.5">
                                <Label htmlFor="c-nom" className="label-caps">Nom complet</Label>
                                <Input id="c-nom" data-testid="contact-input-nom" value={form.nom} onChange={handleChange('nom')} required className="bg-[hsl(var(--background))]" />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label htmlFor="c-ent" className="label-caps">Entreprise</Label>
                                <Input id="c-ent" data-testid="contact-input-entreprise" value={form.entreprise} onChange={handleChange('entreprise')} className="bg-[hsl(var(--background))]" />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label htmlFor="c-email" className="label-caps">Email</Label>
                                <Input id="c-email" type="email" data-testid="contact-input-email" value={form.email} onChange={handleChange('email')} required className="bg-[hsl(var(--background))]" />
                            </div>
                            <div className="flex flex-col gap-1.5">
                                <Label htmlFor="c-tel" className="label-caps">Téléphone</Label>
                                <Input id="c-tel" data-testid="contact-input-telephone" value={form.telephone} onChange={handleChange('telephone')} className="bg-[hsl(var(--background))]" />
                            </div>
                            <div className="sm:col-span-2 flex flex-col gap-1.5">
                                <Label htmlFor="c-msg" className="label-caps">Message</Label>
                                <Textarea
                                    id="c-msg"
                                    data-testid="contact-input-message"
                                    rows={6}
                                    value={form.message}
                                    onChange={handleChange('message')}
                                    required
                                    className="bg-[hsl(var(--background))]"
                                    placeholder="Décrivez votre besoin, votre ligne de production, vos essences…"
                                />
                            </div>
                        </div>
                        <div className="mt-7 flex items-center justify-end">
                            <button
                                type="submit"
                                disabled={submitting}
                                data-testid="contact-form-submit-button"
                                className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(10_62%_36%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-6 h-12 text-sm font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                            >
                                {submitting ? 'Envoi…' : 'Envoyer le message'}
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </button>
                        </div>
                        {done && (
                            <div
                                data-testid="contact-success-message"
                                className="mt-5 rounded-xl border border-[hsla(120,28%,34%,0.3)] bg-[hsla(120,28%,34%,0.06)] p-4 text-sm"
                            >
                                Merci, votre message a bien été envoyé. Nous reviendrons vers vous sous 48h.
                            </div>
                        )}
                    </form>
                </div>

                <aside className="lg:col-span-5" data-animate="fade-up">
                    <div className="rounded-2xl border border-black/5 bg-[hsl(38_45%_94%)] p-6 sm:p-8">
                        <div className="label-caps">Coordonnées</div>
                        <div className="mt-4 space-y-4 text-sm">
                            <div className="flex items-start gap-3">
                                <Mail className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                                <div>
                                    <div className="font-medium">contact@beaver-vision.fr</div>
                                    <div className="text-[hsl(var(--muted-foreground))]">Réponse sous 48h ouvrées</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Phone className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                                <div>
                                    <div className="font-medium">+33 (0)4 79 00 00 00</div>
                                    <div className="text-[hsl(var(--muted-foreground))]">Lun – Ven · 9h – 18h</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <MapPin className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                                <div>
                                    <div className="font-medium">Chambéry, Savoie</div>
                                    <div className="text-[hsl(var(--muted-foreground))]">Rhône-Alpes · France</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="mt-4 rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-8">
                        <div className="label-caps">Promesse</div>
                        <ul className="mt-4 space-y-3 text-sm">
                            {[
                                'Réponse personnalisée par un ingénieur',
                                'Confidentialité totale (NDA sur demande)',
                                'Pas de prospection commerciale automatique',
                            ].map((p) => (
                                <li key={p} className="flex items-start gap-3">
                                    <span className="mt-2 h-1.5 w-1.5 rounded-full bg-[hsl(var(--primary))]" />
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
