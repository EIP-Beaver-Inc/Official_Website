import { useEffect, useState } from 'react';
import SectionHeader from '@/components/SectionHeader';
import { fetchScoring } from '@/lib/api';

const CARD_TONE = {
    Premium: 'border-[hsla(14,64%,42%,0.35)] bg-[hsla(14,64%,42%,0.06)]',
    Standard: 'border-black/5 bg-[hsl(var(--card))]',
    Economy: 'border-black/5 bg-[hsl(var(--card))]',
    Reject: 'border-black/5 bg-[hsl(var(--card))]',
};

export default function ScoringSection() {
    const [classes, setClasses] = useState([]);

    useEffect(() => {
        fetchScoring()
            .then((d) => setClasses(d.classes || []))
            .catch(() => setClasses([]));
    }, []);

    return (
        <section data-testid="home-scoring" className="py-16 sm:py-24 lg:py-32">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-start">
                    <div className="lg:col-span-5">
                        <SectionHeader
                            kicker="03 · Classement"
                            title={
                                <>
                                    Score 0–100, classe <span className="brick-italic">en sortie.</span>
                                </>
                            }
                            subtitle="Le backend C++17 calcule un score qualité déterministe à partir des défauts confirmés par BOBER, leurs surfaces et leur criticité. Stockage SQLite3, exposition via API REST cpp-httplib."
                        />
                        <ul className="mt-8 space-y-3 text-sm">
                            {[
                                'Calcul de score déterministe par planche',
                                'Persistance SQLite3 + export JSON par session',
                                'Photos haute résolution de chaque défaut confirmé',
                                'Communication HTTP/JSON avec frontend opérateur PyQt6',
                            ].map((b) => (
                                <li key={b} className="flex items-start gap-3">
                                    <span className="mt-2 h-1.5 w-1.5 rounded-full bg-[hsl(var(--primary))]" />
                                    <span className="leading-relaxed">{b}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="lg:col-span-7">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                            {classes.map((c, idx) => (
                                <article
                                    key={c.name}
                                    data-testid="scoring-class-card"
                                    data-animate="fade-up"
                                    className={`rounded-2xl border p-5 sm:p-6 transition-shadow duration-200 hover:shadow-[0_14px_32px_rgba(17,17,17,0.07)] ${CARD_TONE[c.name] || ''}`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="label-caps">Classe {String(idx + 1).padStart(2, '0')}</span>
                                        <span className="text-[11px] tracking-[0.16em] uppercase text-[hsl(var(--primary))] font-medium">
                                            {c.range}
                                        </span>
                                    </div>
                                    <h3 className="mt-3 font-heading text-2xl tracking-tight">{c.name}</h3>
                                    <p className="mt-2 text-sm leading-[1.65] text-[hsl(var(--muted-foreground))]">
                                        {c.description}
                                    </p>
                                </article>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
