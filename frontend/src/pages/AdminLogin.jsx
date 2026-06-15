import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, ArrowRight, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { adminLogin } from '@/lib/api';

export default function AdminLogin() {
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!password) return;
        try {
            setSubmitting(true);
            const data = await adminLogin(password);
            localStorage.setItem('beaver_admin_token', data.token);
            navigate('/admin', { replace: true });
        } catch {
            toast.error('Mot de passe incorrect.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <section className="max-w-sm mx-auto px-4 py-20 sm:py-32">
            <div className="text-center mb-8">
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-[hsl(var(--primary)/0.1)] mb-4">
                    <Lock className="h-6 w-6 text-[hsl(var(--primary))]" />
                </span>
                <h1 className="font-heading text-3xl tracking-[-0.02em]">Administration</h1>
                <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">Accès réservé à l'équipe Beaver.</p>
            </div>

            <form
                onSubmit={onSubmit}
                className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 shadow-[0_18px_44px_rgba(17,17,17,0.06)]"
            >
                <div className="flex flex-col gap-1.5">
                    <Label className="label-caps">Mot de passe admin</Label>
                    <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="bg-[hsl(var(--background))]"
                        required
                        autoFocus
                    />
                </div>
                <button
                    type="submit"
                    disabled={submitting}
                    className="mt-5 w-full inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] h-11 text-sm font-medium transition-colors"
                >
                    {submitting ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                        <>
                            Connexion
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </>
                    )}
                </button>
            </form>
        </section>
    );
}
