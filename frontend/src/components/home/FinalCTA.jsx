import { useEffect, useRef, useState } from 'react';
import { Check, FileText } from 'lucide-react';
import DemoDialog from '@/components/DemoDialog';
import PillButton from '@/components/PillButton';

const MARQUEE = ['Nœuds', 'Fissures', 'Temps réel', 'Embarqué', 'EN 975-1', 'Planche par planche'];
const ONBOARDING = ['Audit ligne', 'Calibration ROI', 'Fine-tuning BOBER', 'Intégration backend & PyQt6'];
const STEP_MS = 700;

function useSequence(ref, count) {
    const [started, setStarted] = useState(false);
    const [done, setDone] = useState(0);

    useEffect(() => {
        const io = new IntersectionObserver(
            ([e]) => {
                if (!e.isIntersecting) return;
                io.disconnect();
                if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) setDone(count + 1);
                setStarted(true);
            },
            { threshold: 0.5 },
        );
        io.observe(ref.current);
        return () => io.disconnect();
    }, [ref, count]);

    useEffect(() => {
        if (!started || done > count) return;
        const t = setTimeout(() => setDone((n) => n + 1), STEP_MS);
        return () => clearTimeout(t);
    }, [started, done, count]);

    return done;
}

function SetupPanel() {
    const ref = useRef(null);
    const done = useSequence(ref, ONBOARDING.length);
    const finished = done > ONBOARDING.length;
    const progress = Math.min(done, ONBOARDING.length) / ONBOARDING.length;

    return (
        <div ref={ref} className="rounded-3xl bg-card text-foreground p-5 sm:p-6 shadow-[0_40px_80px_-30px_rgba(40,15,5,0.6)] text-left">
            <div className="flex items-center justify-between font-mono-ui text-[0.6875rem] uppercase tracking-[0.14em]">
                <span className="text-muted-foreground">Mise en service · Ligne 1</span>
                <span className="text-primary">{Math.round(progress * 100)}%</span>
            </div>
            <div className="mt-3 h-1.5 rounded-full bg-black/5 overflow-hidden">
                <div className="h-full rounded-full bg-primary transition-[width] duration-500 ease-out" style={{ width: `${progress * 100}%` }} />
            </div>

            <ol className="mt-5 space-y-1">
                {ONBOARDING.map((step, i) => {
                    const checked = done > i;
                    const current = done === i;
                    return (
                        <li
                            key={step}
                            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors duration-300 ${current ? 'bg-background' : ''}`}
                        >
                            <span
                                className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition-all duration-300 ${
                                    checked ? 'bg-primary border-primary text-primary-foreground scale-100' : 'border-black/15 text-transparent scale-90'
                                }`}
                            >
                                <Check className="h-3.5 w-3.5" strokeWidth={3} />
                            </span>
                            <span className={`text-[0.9375rem] transition-colors ${checked ? 'text-foreground' : 'text-muted-foreground'}`}>{step}</span>
                            <span className="ml-auto font-mono-ui text-[0.625rem] text-muted-foreground">0{i + 1}</span>
                        </li>
                    );
                })}
            </ol>

            <div
                className={`mt-4 flex items-center gap-3 rounded-2xl border px-4 py-3 transition-all duration-500 ${
                    finished ? 'border-primary/30 bg-primary/5 opacity-100 translate-y-0' : 'border-transparent opacity-0 translate-y-2'
                }`}
            >
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                    <FileText className="h-4 w-4" />
                </span>
                <div>
                    <div className="font-display font-semibold text-[0.9375rem] tracking-[-0.02em]">Premier rapport généré</div>
                    <div className="font-mono-ui text-[0.625rem] uppercase tracking-[0.12em] text-muted-foreground">Planche par planche · EN 975-1</div>
                </div>
            </div>
        </div>
    );
}

export default function FinalCTA() {
    const words = [...MARQUEE, ...MARQUEE];

    return (
        <section data-testid="home-final-cta" className="bg-background pb-24 sm:pb-32 overflow-hidden">
            <div className="py-4 sm:py-5 mb-16 sm:mb-20 select-none border-y border-black/5" aria-hidden>
                <div className="beaver-marquee flex w-max whitespace-nowrap">
                    {words.map((w, i) => (
                        <span
                            key={i}
                            className={`font-display font-semibold uppercase tracking-[-0.02em] text-lg sm:text-xl px-3 sm:px-4 ${
                                i % 2 ? 'text-outline' : 'text-foreground'
                            }`}
                        >
                            {w}
                            <span className="ml-6 sm:ml-8 text-primary text-sm align-middle">✦</span>
                        </span>
                    ))}
                </div>
            </div>

            <div className="px-4 sm:px-6 lg:px-8" data-animate="fade-up">
                <div className="relative max-w-6xl mx-auto overflow-hidden rounded-[2rem] bg-primary text-primary-foreground px-6 py-14 sm:px-12 sm:py-16 lg:py-20">
                    <div className="absolute inset-0 noise-overlay opacity-40 pointer-events-none" aria-hidden />
                    <div
                        className="absolute inset-0 pointer-events-none"
                        aria-hidden
                        style={{
                            background:
                                'radial-gradient(50% 70% at 85% 30%, hsl(32 90% 70% / 0.35) 0%, transparent 100%), radial-gradient(50% 60% at 10% 110%, hsl(14 70% 25% / 0.55) 0%, transparent 100%)',
                        }}
                    />

                    <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
                        <div className="lg:col-span-7">
                            <div className="font-mono-ui text-xs uppercase tracking-[0.14em] text-primary-foreground/70">Passer à l'action</div>
                            <h2 className="mt-5 [text-wrap:balance] font-display font-semibold text-4xl sm:text-5xl lg:text-6xl leading-[1.02] tracking-[-0.04em]">
                                Branchez Beaver sur votre ligne de sciage en moins de 7 jours.
                            </h2>
                            <p className="mt-6 max-w-md text-base text-primary-foreground/80">Vos rapports planche par planche, dès la mise en route.</p>
                            <div className="mt-10 flex flex-wrap gap-3">
                                <DemoDialog
                                    triggerClassName="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary-foreground))] text-primary hover:bg-white hover:scale-[1.03] px-6 sm:px-7 h-12 text-sm font-medium transition-[background-color,transform]"
                                    triggerLabel="Demander un devis"
                                    testId="final-cta-demo-button"
                                />
                                <PillButton to="/contact" variant="light" size="md" className="!h-12 !px-6" testId="final-cta-contact">
                                    Nous contacter
                                </PillButton>
                            </div>
                        </div>
                        <div className="lg:col-span-5 lg:rotate-[2deg]">
                            <SetupPanel />
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
