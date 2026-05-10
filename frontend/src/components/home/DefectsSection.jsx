import { useEffect, useState } from 'react';
import SectionHeader from '@/components/SectionHeader';
import { fetchDefects } from '@/lib/api';

const IMPACT_COLOR = {
    'Critique': 'bg-[hsla(10,60%,40%,0.12)] text-[hsl(var(--primary))] border-[hsla(10,60%,40%,0.3)]',
    'Modéré': 'bg-[hsl(38_45%_92%)] text-[hsl(35_45%_30%)] border-black/5',
    'Mineur': 'bg-[hsl(120_22%_88%)] text-[hsl(120_28%_28%)] border-black/5',
    'Esthétique': 'bg-[hsl(190_25%_90%)] text-[hsl(190_30%_28%)] border-black/5',
};

export default function DefectsSection() {
    const [defects, setDefects] = useState([]);

    useEffect(() => {
        fetchDefects()
            .then((d) => setDefects(d.defects || []))
            .catch(() => setDefects([]));
    }, []);

    return (
        <section
            data-testid="home-defects"
            className="py-16 sm:py-24 lg:py-32 bg-[hsl(38_45%_94%)] border-y border-black/5"
        >
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <SectionHeader
                    kicker="02 · Détection"
                    title={
                        <>
                            <span className="brick-italic">9 classes</span> de défauts.
                        </>
                    }
                    subtitle="Dataset propriétaire · YOLOv8 fine-tuné sur images recadrées post-ROI. Chaque défaut est suivi sur 40 frames minimum avant confirmation."
                />

                <div className="mt-10 sm:mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
                    {defects.map((d, idx) => (
                        <article
                            key={d.key}
                            data-testid="defect-card"
                            data-animate="fade-up"
                            className="rounded-2xl bg-[hsl(var(--background))] border border-black/5 p-5 sm:p-6 transition-shadow duration-200 hover:shadow-[0_14px_32px_rgba(17,17,17,0.07)]"
                        >
                            <div className="flex items-center justify-between">
                                <span className="label-caps !tracking-[0.18em]">Défaut {String(idx + 1).padStart(2, '0')}</span>
                                <span
                                    className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] tracking-[0.14em] uppercase ${IMPACT_COLOR[d.impact] || ''}`}
                                >
                                    {d.impact}
                                </span>
                            </div>
                            <h3 className="mt-3 font-heading text-2xl sm:text-[26px] tracking-tight">{d.name}</h3>
                            <p className="mt-3 text-sm leading-[1.65] text-[hsl(var(--muted-foreground))]">
                                {d.description}
                            </p>
                        </article>
                    ))}
                </div>
            </div>
        </section>
    );
}
