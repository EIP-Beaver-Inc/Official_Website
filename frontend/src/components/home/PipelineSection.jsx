import { Activity, Scan, Target } from 'lucide-react';
import SectionHeader from '@/components/SectionHeader';
import { useEffect, useState } from 'react';
import { fetchPipeline } from '@/lib/api';

const ICONS = { scan: Scan, target: Target, activity: Activity };

export default function PipelineSection() {
    const [steps, setSteps] = useState([]);

    useEffect(() => {
        fetchPipeline()
            .then((d) => setSteps(d.steps || []))
            .catch(() => setSteps([]));
    }, []);

    return (
        <section data-testid="home-pipeline" className="py-16 sm:py-24 lg:py-32">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <SectionHeader
                    kicker="01 · Pipeline"
                    title={
                        <>
                            Trois modèles, <span className="brick-italic">un rapport</span> par planche.
                        </>
                    }
                    subtitle="Chaque planche traverse une chaîne d’inférence déterministe. Une machine à états ouvre et ferme une session par planche selon sa présence dans le champ."
                />

                <div className="mt-10 sm:mt-14 grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
                    {steps.map((s) => {
                        const Icon = ICONS[s.icon] || Scan;
                        return (
                            <article
                                key={s.step}
                                data-testid="pipeline-step-card"
                                data-animate="fade-up"
                                className="group relative rounded-2xl bg-[hsl(var(--card))] border border-black/5 p-6 sm:p-7 shadow-[0_10px_30px_rgba(17,17,17,0.05)] transition-shadow duration-200 ease-out hover:shadow-[0_18px_44px_rgba(17,17,17,0.1)] hover:-translate-y-0.5 transition-transform"
                            >
                                <div className="flex items-start justify-between">
                                    <span className="font-heading text-xl text-[hsl(var(--muted-foreground))]">{s.step}</span>
                                    <Icon className="h-5 w-5 text-[hsl(var(--primary))]" />
                                </div>
                                <h3 className="mt-10 font-heading text-3xl sm:text-4xl tracking-tight">{s.name}</h3>
                                <div className="mt-3 label-caps text-[hsl(var(--primary))] !tracking-[0.18em]">
                                    {s.sub}
                                </div>
                                <p className="mt-4 text-sm leading-[1.7] text-[hsl(var(--muted-foreground))]">
                                    {s.description}
                                </p>
                            </article>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}
