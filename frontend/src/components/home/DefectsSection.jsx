import { useEffect, useState } from 'react';
import { Lock } from 'lucide-react';
import Kicker from '@/components/Kicker';
import PillButton from '@/components/PillButton';
import { fetchDefects } from '@/lib/api';
import { DEFECT_TYPES, PLANK_IMAGE, PLANK_SIZE } from '@/lib/plank';
import LiveDot from '@/components/LiveDot';
import { MASCOT_INSPECTOR_URL } from '@/lib/assets';

const SPECS = ['YOLOv8 fine-tuné', 'Images recadrées post-ROI', '40 frames minimum'];

const IMPACTS = {
    'Critique': 'bg-primary',
    'Modéré': 'bg-[hsl(35_55%_45%)]',
    'Mineur': 'bg-[hsl(120_25%_40%)]',
    'Esthétique': 'bg-[hsl(190_30%_40%)]',
};

const isLive = (d) => (d.status ? d.status === 'live' : /^(noeud_vif|noeud_mort|fissure)$/.test(d.key));

const PLANK_TYPE = { noeud_vif: 'vif', noeud_mort: 'mort', fissure: 'fissure' };
const SPECIMENS = {
    noeud_vif: { src: '/assets/defect-noeud-vif.jpg', box: { left: '36%', top: '21%', width: '25%', height: '62%' } },
    noeud_mort: { src: '/assets/defect-noeud-mort.jpg', box: { left: '33%', top: '27%', width: '38%', height: '56%' } },
    fissure: { src: '/assets/defect-fissure.jpg', box: { left: '3%', top: '59%', width: '94%', height: '15%' } },
};

const FAN = [
    { rot: -7, y: 28 },
    { rot: 0, y: 0 },
    { rot: 7, y: 28 },
];

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

function crop(spot, aspect) {
    const { w: W, h: H } = PLANK_SIZE;
    const bx = (spot.x / 100) * W;
    const by = (spot.y / 100) * H;
    const bw = (spot.w / 100) * W;
    const bh = (spot.h / 100) * H;
    const rw = Math.min(W, Math.max(150, bw * 2.4, (bh * 2.4) / aspect), H / aspect);
    const rh = rw * aspect;
    const rx = clamp(bx + bw / 2 - rw / 2, 0, W - rw);
    const ry = clamp(by + bh / 2 - rh / 2, 0, H - rh);
    return {
        image: {
            backgroundImage: `url(${PLANK_IMAGE})`,
            backgroundSize: `${(W / rw) * 100}% auto`,
            backgroundPosition: `${W === rw ? 0 : (rx / (W - rw)) * 100}% ${H === rh ? 0 : (ry / (H - rh)) * 100}%`,
        },
        box: {
            left: `${((bx - rx) / rw) * 100}%`,
            top: `${((by - ry) / rh) * 100}%`,
            width: `${(bw / rw) * 100}%`,
            height: `${(bh / rh) * 100}%`,
        },
    };
}

function SpecimenCard({ defect, index, total, fan, state, onEnter, onLeave }) {
    const type = PLANK_TYPE[defect.key];
    const specimen = SPECIMENS[defect.key];

    const [tilt, setTilt] = useState({ x: 0, y: 0, mx: 50 });
    const onMove = (e) => {
        if (e.pointerType !== 'mouse') return;
        const r = e.currentTarget.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        setTilt({ x: (0.5 - py) * 10, y: (px - 0.5) * 12, mx: px * 100 });
    };
    const lifted = state === 'hover';
    const shift = state === 'left' ? -28 : state === 'right' ? 28 : 0;
    const transform = lifted
        ? `translate3d(0, -18px, 40px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(1.04)`
        : `translate3d(${shift}px, ${fan.y}px, 0) rotate(${fan.rot}deg)`;

    return (
        <article
            data-testid="defect-card"
            onPointerEnter={onEnter}
            onPointerLeave={() => {
                setTilt({ x: 0, y: 0, mx: 50 });
                onLeave();
            }}
            onPointerMove={onMove}
            className={`relative shrink-0 snap-center w-[78vw] max-w-[20rem] sm:w-[18.75rem] rounded-[1.75rem] bg-card border border-black/5 p-3 transition-[transform,box-shadow] duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] lg:[transform:var(--t)] ${
                lifted ? 'z-10 shadow-[0_40px_80px_-24px_rgba(60,35,20,0.45)]' : 'shadow-[0_24px_50px_-24px_rgba(60,35,20,0.3)]'
            }`}
            style={{ '--t': transform }}
        >
            <div className="relative aspect-[4/3] overflow-hidden rounded-[1.25rem] bg-[hsl(25_18%_11%)]">
                {specimen && <img src={specimen.src} alt={defect.name} loading="lazy" className="absolute inset-0 h-full w-full object-cover" />}
                {specimen && type && (
                    <div className="absolute rounded-md border-2" style={{ ...specimen.box, borderColor: DEFECT_TYPES[type].color }}>
                        <span
                            className="absolute bottom-full left-0 mb-1 whitespace-nowrap rounded px-1.5 py-0.5 font-mono-ui text-[0.625rem] leading-none text-white"
                            style={{ background: DEFECT_TYPES[type].color }}
                        >
                            {DEFECT_TYPES[type].label}
                        </span>
                    </div>
                )}
                <div
                    className={`absolute inset-0 pointer-events-none transition-opacity duration-300 ${lifted ? 'opacity-100' : 'opacity-0'}`}
                    style={{
                        background: `linear-gradient(115deg, transparent ${tilt.mx - 30}%, rgba(255,255,255,0.35) ${tilt.mx}%, transparent ${tilt.mx + 30}%)`,
                    }}
                    aria-hidden
                />
            </div>

            <div className="px-2 pt-5 pb-3">
                <div className="flex items-center justify-between font-mono-ui text-[0.6875rem] uppercase tracking-[0.12em] text-muted-foreground">
                    <span>
                        <span className="text-primary">{String(index + 1).padStart(2, '0')}</span> / {String(total).padStart(2, '0')}
                    </span>
                    <span className="inline-flex items-center gap-1.5">
                        <span className={`h-1.5 w-1.5 rounded-full ${IMPACTS[defect.impact] || 'bg-muted-foreground'}`} />
                        {defect.impact}
                    </span>
                </div>
                <h3 className="mt-3 font-display font-semibold text-3xl tracking-[-0.04em] text-foreground">{defect.name}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground line-clamp-3">{defect.description}</p>
                <div className="mt-5 flex items-center gap-2 font-mono-ui text-[0.625rem] uppercase tracking-[0.14em] text-[hsl(120_30%_32%)]">
                    <LiveDot color="bg-[hsl(120_35%_40%)]" />
                    Détecté en production
                </div>
            </div>
        </article>
    );
}

function LockedTile({ defect, index }) {
    const view = crop({ x: 12 + index * 14, y: 30, w: 4, h: 30 }, 2 / 3);
    return (
        <li className="group relative overflow-hidden rounded-2xl bg-card border border-black/5">
            <div className="relative aspect-[3/2] overflow-hidden">
                <div className="absolute -inset-3 bg-no-repeat blur-md scale-110 opacity-70" style={view.image} />
                <div className="absolute inset-0 bg-[hsl(var(--card)/0.35)]" />
                <span className="absolute inset-0 m-auto inline-flex h-9 w-9 items-center justify-center rounded-full bg-card/90 text-muted-foreground shadow-sm transition-transform duration-300 group-hover:scale-110">
                    <Lock className="h-3.5 w-3.5" />
                </span>
            </div>
            <div className="px-3 py-2.5">
                <div className="font-display font-semibold text-sm tracking-[-0.02em] text-foreground truncate">{defect.name}</div>
                <div className="mt-0.5 font-mono-ui text-[0.5625rem] uppercase tracking-[0.14em] text-muted-foreground">Bientôt</div>
            </div>
        </li>
    );
}

export default function DefectsSection() {
    const [defects, setDefects] = useState([]);
    const [hovered, setHovered] = useState(null);

    useEffect(() => {
        fetchDefects()
            .then((d) => setDefects(d.defects || []))
            .catch(() => setDefects([]));
    }, []);

    const live = defects.filter(isLive);
    const soon = defects.filter((d) => !isLive(d));
    const cardState = (i) => (hovered === null ? 'idle' : i === hovered ? 'hover' : i < hovered ? 'left' : 'right');

    return (
        <section data-testid="home-defects" className="relative py-24 sm:py-32 overflow-hidden">
            <div
                className="absolute inset-x-0 top-40 h-[32.5rem] pointer-events-none"
                aria-hidden
                style={{ background: 'radial-gradient(45% 55% at 50% 50%, hsl(38 60% 86%) 0%, transparent 100%)' }}
            />

            <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <header className="relative text-center" data-animate="fade-up">
                    <img
                        src={MASCOT_INSPECTOR_URL}
                        alt="La mascotte Beaver inspecte une planche à la loupe"
                        loading="lazy"
                        className="mx-auto mb-6 w-36 sm:w-44 lg:absolute lg:-left-4 lg:-top-8 lg:mb-0 lg:w-40 xl:w-48 drop-shadow-[0_20px_30px_rgba(60,35,20,0.25)]"
                    />
                    <Kicker className="justify-center">Détection</Kicker>
                    <h2 className="mt-5 font-display font-semibold text-5xl sm:text-6xl lg:text-7xl leading-[0.95] tracking-[-0.045em] text-foreground">
                        Nœuds et fissures.
                        <br />
                        <span className="text-primary">Détectés aujourd’hui.</span>
                    </h2>
                    <ul className="mt-7 flex flex-wrap justify-center gap-2">
                        {SPECS.map((s) => (
                            <li
                                key={s}
                                className="rounded-full border border-black/10 bg-card/70 px-3.5 py-1.5 font-mono-ui text-[0.6875rem] uppercase tracking-[0.12em] text-muted-foreground"
                            >
                                {s}
                            </li>
                        ))}
                    </ul>
                </header>

                {live.length > 0 && (
                    <div className="mt-16 sm:mt-20 -mx-4 px-4 flex gap-4 overflow-x-auto snap-x snap-mandatory pb-6 lg:mx-0 lg:px-0 lg:overflow-visible lg:justify-center lg:gap-6 lg:pb-10 [perspective:87.5rem] [scrollbar-width:none]">
                        {live.map((d, i) => (
                            <SpecimenCard
                                key={d.key}
                                defect={d}
                                index={i}
                                total={defects.length}
                                fan={FAN[i] || FAN[1]}
                                state={cardState(i)}
                                onEnter={() => setHovered(i)}
                                onLeave={() => setHovered(null)}
                            />
                        ))}
                    </div>
                )}

                {soon.length > 0 && (
                    <div className="mt-16 sm:mt-20">
                        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                            <div>
                                <div className="font-mono-ui text-[0.6875rem] uppercase tracking-[0.14em] text-muted-foreground">En entraînement</div>
                                <h3 className="mt-2 font-display font-semibold text-2xl sm:text-3xl tracking-[-0.035em] text-foreground">
                                    {soon.length} singularités en développement, <span className="text-primary">avec votre aide ?</span>
                                </h3>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="w-40">
                                    <div className="flex justify-between font-mono-ui text-[0.625rem] uppercase tracking-[0.12em] text-muted-foreground">
                                        <span>Couverture</span>
                                        <span className="text-foreground">
                                            {live.length}/{defects.length}
                                        </span>
                                    </div>
                                    <div className="mt-1.5 h-1.5 rounded-full bg-black/5 overflow-hidden">
                                        <div className="h-full rounded-full bg-primary" style={{ width: `${(live.length / defects.length) * 100}%` }} />
                                    </div>
                                </div>
                                <PillButton to="/beta" size="md" className="shrink-0" testId="defects-join-beta">
                                    Rejoindre la beta
                                </PillButton>
                            </div>
                        </div>
                        <ul className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
                            {soon.map((d, i) => (
                                <LockedTile key={d.key} defect={d} index={i} />
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </section>
    );
}
