const STATS = [
    { value: '3', unit: 'classes', label: 'Nœuds et fissures détectés' },
    { value: 'EN 975-1', unit: '', label: 'Classement normé' },
    { value: '< 7', unit: 'jours', label: 'Mise en service' },
];

export default function StatsBand() {
    return (
        <section data-testid="home-stats" className="relative bg-card/70 backdrop-blur-md border-b border-black/5">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <dl className="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-black/10">
                    {STATS.map((s) => (
                        <div key={s.label} data-animate="fade-up" className="py-8 sm:py-10 sm:px-8 text-center">
                            <dt className="font-mono-ui text-[0.6875rem] uppercase tracking-[0.14em] text-muted-foreground">{s.label}</dt>
                            <dd className="mt-3 font-display font-semibold tracking-[-0.04em] text-4xl sm:text-5xl text-foreground">
                                {s.value}
                                {s.unit && <span className="ml-2 text-base font-normal tracking-normal text-muted-foreground">{s.unit}</span>}
                            </dd>
                        </div>
                    ))}
                </dl>
            </div>
        </section>
    );
}
