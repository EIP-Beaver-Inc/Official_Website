import { useEffect, useRef, useState } from 'react';
import { Check } from 'lucide-react';
import Kicker from '@/components/Kicker';
import { DEFECT_TYPES as TYPES, PLANK_DEFECTS as DEFECTS, PLANK_IMAGE, PLANK_RATIO } from '@/lib/plank';


const OVERSIZE = 2;
const THICKNESS = `${1.125 * OVERSIZE}rem`;

const appearAt = (d) => 0.47 + (d.x / 100) * 0.28;
const isSmall = (d) => d.w < 2.5;

const KEYFRAMES = [
    { p: 0, rx: 62, rz: -24, s: 0.62, tx: 0, ty: 0 },
    { p: 0.2, rx: 55, rz: -14, s: 0.78, tx: 0, ty: 0 },
    { p: 0.38, rx: 28, rz: -4, s: 1, tx: 0, ty: 0 },
    { p: 0.52, rx: 0, rz: 0, s: 1.9, tx: 22, ty: 0 },
    { p: 0.64, rx: 0, rz: 0, s: 1.9, tx: -6, ty: 0 },
    { p: 0.76, rx: 0, rz: 0, s: 1.9, tx: -34, ty: 0 },
    { p: 0.88, rx: 0, rz: 0, s: 0.92, tx: 0, ty: -20 },
    { p: 1, rx: 0, rz: 0, s: 0.92, tx: 0, ty: -20 },
];

const SCAN = { from: 0.24, to: 0.46 };
const TRACK = { from: 0.45, to: 0.78, frames: 40 };
const VERDICT_AT = 0.84;

const STEPS = [
    {
        title: null,
        text: null,
    },
    {
        title: 'Au-delà du contrôle manuel',
        text: 'Pensé pour répondre aux limites du contrôle qualité manuel, Beaver combine caméras et modèles de vision par ordinateur entraînés spécifiquement pour l’analyse du bois.',
    },
    {
        title: 'Temps réel, embarqué',
        text: 'Le tout est exécuté en temps réel sur machine en scierie et directement connecté à un hardware embarqué.',
    },
    {
        title: 'Dès la ligne de production',
        text: 'Le système identifie les défauts dès la ligne de production, réduit les pertes matière et fiabilise le tri, au service des scieries et de leurs équipes.',
    },
];
const STEP_LABELS = ['Beaver', 'Vision', 'Temps réel', 'Production'];

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const smooth = (t) => t * t * (3 - 2 * t);
const range = (p, a, b) => clamp01((p - a) / (b - a));

function cameraAt(p) {
    let i = KEYFRAMES.findIndex((k) => k.p >= p);
    if (i <= 0) return KEYFRAMES[0];
    const a = KEYFRAMES[i - 1];
    const b = KEYFRAMES[i];
    const t = smooth((p - a.p) / (b.p - a.p));
    const lerp = (key) => a[key] + (b[key] - a[key]) * t;
    return { rx: lerp('rx'), rz: lerp('rz'), s: lerp('s'), tx: lerp('tx'), ty: lerp('ty') };
}

const stepAt = (p) => (p < 0.22 ? 0 : p < 0.45 ? 1 : p < 0.8 ? 2 : 3);

export default function ScanStory() {
    const sectionRef = useRef(null);
    const panRef = useRef(null);
    const plankRef = useRef(null);
    const beamRef = useRef(null);
    const scannedRef = useRef(null);
    const boxRefs = useRef([]);
    const frameRef = useRef(null);
    const trackRef = useRef(null);
    const verdictRef = useRef(null);
    const [step, setStep] = useState(0);

    useEffect(() => {
        let raf = 0;

        const render = () => {
            raf = 0;
            const el = sectionRef.current;
            if (!el) return;
            const rect = el.getBoundingClientRect();
            const p = clamp01(-rect.top / (rect.height - window.innerHeight));

            const c = cameraAt(p);
            const k = c.s / OVERSIZE;
            const tilted = Math.abs(c.rx) > 0.5 || Math.abs(c.rz) > 0.5;
            panRef.current.style.perspective = tilted ? '87.5rem' : 'none';
            panRef.current.style.transform = `translate3d(${c.tx * k}%, ${c.ty * k}%, 0)`;
            plankRef.current.style.transform = `rotateX(${c.rx}deg) rotateZ(${c.rz}deg) scale(${k})`;

            const scan = range(p, SCAN.from, SCAN.to);
            const scanning = p > SCAN.from && p < SCAN.to;
            beamRef.current.style.left = `${scan * 100}%`;
            beamRef.current.style.opacity = scanning ? '1' : '0';
            scannedRef.current.style.width = `${scan * 100}%`;
            scannedRef.current.style.opacity = p < TRACK.from + 0.05 ? '1' : '0';

            DEFECTS.forEach((d, i) => {
                const box = boxRefs.current[i];
                if (!box) return;
                const t = range(p, appearAt(d), appearAt(d) + 0.03);
                box.style.opacity = String(t);
                box.style.transform = `scale(${1.25 - 0.25 * t})`;
            });

            const frame = Math.max(1, Math.round(range(p, TRACK.from, TRACK.to) * TRACK.frames));
            frameRef.current.textContent = `${String(frame).padStart(2, '0')}/${TRACK.frames}`;
            trackRef.current.style.opacity = p > TRACK.from - 0.02 && p < VERDICT_AT ? '1' : '0';

            const v = range(p, VERDICT_AT, VERDICT_AT + 0.06);
            verdictRef.current.style.opacity = String(v);
            verdictRef.current.style.transform = `translate3d(-50%, ${(1 - v) * 24}px, 0)`;

            setStep(stepAt(p));
        };

        const onScroll = () => {
            if (!raf) raf = requestAnimationFrame(render);
        };
        render();
        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll);
        return () => {
            window.removeEventListener('scroll', onScroll);
            window.removeEventListener('resize', onScroll);
            cancelAnimationFrame(raf);
        };
    }, []);

    const counts = DEFECTS.reduce((acc, d) => ({ ...acc, [d.type]: (acc[d.type] || 0) + 1 }), {});
    const edge = {
        backgroundImage: `linear-gradient(hsl(25 40% 18% / 0.55), hsl(25 40% 12% / 0.7)), url(${PLANK_IMAGE})`,
        backgroundSize: 'cover',
    };

    return (
        <section ref={sectionRef} data-testid="home-scan-story" className="relative bg-background h-[650vh] [overflow-x:clip]">
            <div className="sticky top-0 h-[100svh]">
                <div
                    className="absolute inset-0 pointer-events-none"
                    aria-hidden
                    style={{
                        background:
                            'radial-gradient(60% 50% at 50% 65%, hsl(38 60% 88%) 0%, transparent 70%), radial-gradient(hsl(25 18% 11% / 0.08) 1px, transparent 1px)',
                        backgroundSize: 'auto, 1.375rem 1.375rem',
                    }}
                />

                <div className="relative h-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col pt-24 sm:pt-32 pb-8">
                    <div className="relative h-[13.125rem] sm:h-[14.375rem] shrink-0">
                        {STEPS.map((s, i) => (
                            <div
                                key={i}
                                aria-hidden={step !== i}
                                className={`absolute inset-0 transition-all duration-500 ease-out ${
                                    step === i ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
                                }`}
                            >
                                <Kicker index={`0${i}`}>{STEP_LABELS[i]}</Kicker>
                                {i === 0 ? (
                                    <h2 className="mt-5 max-w-4xl [text-wrap:balance] font-display font-semibold text-3xl sm:text-4xl lg:text-5xl leading-[1.08] tracking-[-0.035em] text-foreground">
                                        Un système d’intelligence artificielle embarqué, conçu pour détecter automatiquement{' '}
                                        <span className="text-primary">les défauts du bois</span> directement en scierie.
                                    </h2>
                                ) : (
                                    <>
                                        <h3 className="mt-5 font-display font-semibold text-3xl sm:text-5xl tracking-[-0.04em] text-foreground">
                                            {s.title}
                                        </h3>
                                        <p className="mt-4 max-w-xl text-base sm:text-lg leading-relaxed text-muted-foreground">{s.text}</p>
                                    </>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="relative flex-1 flex items-center justify-center">
                        <div ref={panRef} className="shrink-0 will-change-transform">
                            <div
                                ref={plankRef}
                                className="relative [transform-style:preserve-3d] will-change-transform"
                                style={{
                                    width: `min(${68.75 * OVERSIZE}rem, ${92 * OVERSIZE}vw)`,
                                    aspectRatio: String(PLANK_RATIO),
                                    flexShrink: 0,
                                }}
                            >
                                <div
                                    className="absolute left-0 right-0 top-full origin-top [transform:rotateX(-90deg)]"
                                    style={{ height: THICKNESS, ...edge }}
                                />
                                <div
                                    className="absolute left-0 right-0 bottom-full origin-bottom [transform:rotateX(90deg)]"
                                    style={{ height: THICKNESS, ...edge }}
                                />
                                <div
                                    className="absolute top-0 bottom-0 left-full origin-left [transform:rotateY(90deg)]"
                                    style={{ width: THICKNESS, ...edge }}
                                />
                                <div
                                    className="absolute top-0 bottom-0 right-full origin-right [transform:rotateY(-90deg)]"
                                    style={{ width: THICKNESS, ...edge }}
                                />

                                <div className="absolute inset-0 [transform-style:preserve-3d] shadow-[0_80px_160px_-60px_rgba(60,35,20,0.55)]">
                                    <img
                                        src={PLANK_IMAGE}
                                        alt="Planche de bois analysée par Beaver"
                                        draggable={false}
                                        className="absolute inset-0 h-full w-full select-none will-change-transform"
                                    />
                                    <div
                                        ref={scannedRef}
                                        className="absolute inset-y-0 left-0 bg-[hsl(var(--primary)/0.08)] transition-opacity duration-500"
                                        style={{
                                            backgroundImage:
                                                'linear-gradient(90deg, transparent 0 calc(100% - 1px), hsl(var(--primary) / 0.25) 0)',
                                            backgroundSize: '24px 100%',
                                        }}
                                    />
                                    <div ref={beamRef} className="absolute inset-y-0 w-0 opacity-0" aria-hidden>
                                        <div className="absolute inset-y-0 -left-[6%] w-[6%] bg-gradient-to-r from-transparent to-[hsl(var(--primary)/0.35)]" />
                                        <div className="absolute inset-y-0 -left-[0.1875rem] w-[0.375rem] bg-[hsl(14_90%_62%)] shadow-[0_0_36px_8px_hsl(14_90%_60%/0.7)]" />
                                    </div>
                                </div>

                                {DEFECTS.map((d, i) => (
                                    <div
                                        key={i}
                                        ref={(el) => (boxRefs.current[i] = el)}
                                        className="absolute opacity-0 origin-center"
                                        style={{ left: `${d.x}%`, top: `${d.y}%`, width: `${d.w}%`, height: `${d.h}%` }}
                                    >
                                        <div
                                            className="absolute inset-0 rounded-[0.375rem] border-4"
                                            style={{ borderColor: TYPES[d.type].color, background: 'rgba(255,255,255,0.08)' }}
                                        />
                                        <span
                                            className={`absolute bottom-full ${d.x > 80 ? 'right-0' : 'left-0'} mb-2 whitespace-nowrap rounded-[0.375rem] px-2 sm:px-3 py-1 font-mono-ui leading-none text-white ${isSmall(d) ? 'text-[0.5625rem] sm:text-[0.8125rem]' : 'text-[0.6875rem] sm:text-[1.125rem]'}`}
                                            style={{ background: TYPES[d.type].color }}
                                        >
                                            {TYPES[d.type].label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div
                            ref={trackRef}
                            className="absolute top-2 right-0 opacity-0 transition-opacity duration-300 rounded-full bg-card/90 backdrop-blur border border-black/5 px-3 py-1.5 font-mono-ui text-[0.6875rem] uppercase tracking-[0.12em] text-foreground flex items-center gap-2"
                        >
                            <span className="relative flex h-1.5 w-1.5">
                                <span className="absolute inline-flex h-full w-full rounded-full bg-primary beaver-pulse-ring" />
                                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-primary" />
                            </span>
                            Suivi · frame <span ref={frameRef}>01/40</span>
                        </div>

                        <div ref={verdictRef} className="absolute bottom-0 sm:bottom-4 left-1/2 w-[min(35rem,100%)] opacity-0">
                            <div className="rounded-2xl bg-card border border-black/5 shadow-[0_24px_60px_rgba(60,35,20,0.15)] p-4 sm:p-5 grid grid-cols-2 sm:grid-cols-4 gap-3 items-center">
                                {[
                                    ['Nœuds vifs', counts.vif],
                                    ['Nœuds morts', counts.mort],
                                    ['Fissures', counts.fissure],
                                ].map(([label, n]) => (
                                    <div key={label}>
                                        <div className="font-mono-ui text-[0.625rem] uppercase tracking-[0.12em] text-muted-foreground">
                                            {label}
                                        </div>
                                        <div className="mt-1 font-display font-semibold text-2xl tracking-[-0.03em] text-foreground">
                                            {n}
                                        </div>
                                    </div>
                                ))}
                                <div className="rounded-xl bg-primary text-primary-foreground px-3 py-2 text-center">
                                    <div className="font-mono-ui text-[0.625rem] uppercase tracking-[0.12em] opacity-80 flex items-center justify-center gap-1">
                                        <Check className="h-3 w-3" /> Classe
                                    </div>
                                    <div className="mt-0.5 font-display font-semibold text-xl tracking-[-0.03em]">Q-B 4</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <ol className="hidden lg:flex absolute right-8 top-1/2 -translate-y-1/2 flex-col gap-4" aria-hidden>
                    {STEP_LABELS.map((label, i) => (
                        <li
                            key={label}
                            className="flex items-center justify-end gap-3 font-mono-ui text-[0.6875rem] uppercase tracking-[0.12em]"
                        >
                            <span className={`transition-colors ${step === i ? 'text-foreground' : 'text-muted-foreground/50'}`}>
                                {label}
                            </span>
                            <span
                                className={`h-px transition-all duration-300 ${step === i ? 'w-8 bg-primary' : 'w-4 bg-muted-foreground/40'}`}
                            />
                        </li>
                    ))}
                </ol>
            </div>
        </section>
    );
}
