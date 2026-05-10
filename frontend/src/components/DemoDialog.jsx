import { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowRight, BadgeCheck, FileText, Phone } from 'lucide-react';
import { toast } from 'sonner';
import { submitDemoRequest } from '@/lib/api';

export default function DemoDialog({ triggerClassName, triggerLabel = 'Demander un devis', testId = 'open-demo-dialog-button' }) {
    const [open, setOpen] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [form, setForm] = useState({
        nom: '',
        entreprise: '',
        email: '',
        telephone: '',
        taille_scierie: '',
        volume: '',
        message: '',
    });

    const handleChange = (key) => (e) => {
        setForm((s) => ({ ...s, [key]: e.target.value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.nom || !form.entreprise || !form.email) {
            toast.error('Merci de renseigner nom, entreprise et email.');
            return;
        }
        try {
            setSubmitting(true);
            await submitDemoRequest(form);
            toast.success('Demande envoyée — nous vous recontactons sous 48h.');
            setOpen(false);
            setForm({ nom: '', entreprise: '', email: '', telephone: '', taille_scierie: '', volume: '', message: '' });
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Erreur lors de l’envoi. Réessayez.';
            toast.error(typeof detail === 'string' ? detail : 'Erreur de validation.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <button type="button" className={triggerClassName} data-testid={testId}>
                    {triggerLabel}
                </button>
            </DialogTrigger>
            <DialogContent
                data-testid="demo-dialog"
                className="max-w-2xl bg-[hsl(var(--card))] border-black/10"
            >
                <DialogHeader>
                    <DialogTitle className="font-heading text-2xl sm:text-3xl tracking-tight">
                        Demander un <span className="brick-italic">devis</span>
                    </DialogTitle>
                    <DialogDescription className="text-sm text-[hsl(var(--muted-foreground))]">
                        On revient vers vous sous 48h avec un devis personnalisé et un sample d'analyse adapté à votre ligne de production.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4" data-testid="demo-form">
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-nom" className="label-caps">Nom complet</Label>
                        <Input id="d-nom" data-testid="demo-input-nom" value={form.nom} onChange={handleChange('nom')} required className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-entreprise" className="label-caps">Entreprise</Label>
                        <Input id="d-entreprise" data-testid="demo-input-entreprise" value={form.entreprise} onChange={handleChange('entreprise')} required className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-email" className="label-caps">Email</Label>
                        <Input id="d-email" type="email" data-testid="demo-input-email" value={form.email} onChange={handleChange('email')} required className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-tel" className="label-caps">Téléphone</Label>
                        <Input id="d-tel" data-testid="demo-input-telephone" value={form.telephone} onChange={handleChange('telephone')} className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-taille" className="label-caps">Taille scierie</Label>
                        <Input id="d-taille" placeholder="PME / ETI / Groupe" data-testid="demo-input-taille" value={form.taille_scierie} onChange={handleChange('taille_scierie')} className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <Label htmlFor="d-vol" className="label-caps">Volume / jour</Label>
                        <Input id="d-vol" placeholder="ex. 200 planches/h" data-testid="demo-input-volume" value={form.volume} onChange={handleChange('volume')} className="bg-[hsl(var(--background))]" />
                    </div>
                    <div className="sm:col-span-2 flex flex-col gap-1.5">
                        <Label htmlFor="d-msg" className="label-caps">Message (optionnel)</Label>
                        <Textarea id="d-msg" rows={3} data-testid="demo-input-message" value={form.message} onChange={handleChange('message')} className="bg-[hsl(var(--background))]" />
                    </div>

                    <div className="sm:col-span-2 mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3 rounded-xl border border-black/5 bg-[hsl(var(--background))] p-4">
                        <div className="flex items-start gap-2 text-sm">
                            <BadgeCheck className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                            <span>Réponse 48h</span>
                        </div>
                        <div className="flex items-start gap-2 text-sm">
                            <FileText className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                            <span>Rapport démo personnalisé</span>
                        </div>
                        <div className="flex items-start gap-2 text-sm">
                            <Phone className="h-4 w-4 mt-0.5 text-[hsl(var(--primary))]" />
                            <span>Appel ingénieur dédié</span>
                        </div>
                    </div>

                    <DialogFooter className="sm:col-span-2 mt-2">
                        <button
                            type="submit"
                            disabled={submitting}
                            data-testid="demo-request-submit-button"
                            className="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors"
                        >
                            {submitting ? 'Envoi…' : 'Envoyer ma demande'}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
