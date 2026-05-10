import DemoDialog from '@/components/DemoDialog';
import PillButton from '@/components/PillButton';

export default function FinalCTA() {
    return (
        <section
            data-testid="home-final-cta"
            className="relative overflow-hidden border-t border-black/5"
        >
            <div
                className="absolute inset-0 noise-overlay opacity-50 pointer-events-none"
                aria-hidden
            />
            <div
                className="absolute inset-0 pointer-events-none"
                aria-hidden
                style={{
                    background:
                        'radial-gradient(700px 360px at 80% 20%, hsla(14, 64%, 42%, 0.08) 0%, transparent 60%), linear-gradient(180deg, hsl(38 30% 90%) 0%, hsl(42 36% 93%) 100%)',
                }}
            />
            <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 lg:py-32 text-center">
                <div data-animate="fade-up" className="label-caps mb-6">
                    <span className="text-[hsl(var(--primary))]">04</span> · Passer à l'action
                </div>
                <h2
                    data-animate="fade-up"
                    className="font-heading text-4xl sm:text-5xl lg:text-6xl leading-[1.04] tracking-[-0.015em] max-w-3xl mx-auto"
                >
                    Branchez Beaver sur votre <span className="brick-italic">ligne de sciage</span> en moins de 30 jours.
                </h2>
                <p
                    data-animate="fade-up"
                    className="mt-6 max-w-2xl mx-auto text-base sm:text-lg leading-[1.65] text-[hsl(var(--muted-foreground))]"
                >
                    Audit ligne, calibration ROI, fine-tuning BOBER sur vos essences, intégration backend & PyQt6. Vos rapports planche par planche, dès la mise en route.
                </p>
                <div data-animate="fade-up" className="mt-10 flex flex-wrap justify-center gap-3 sm:gap-4">
                    <DemoDialog
                        triggerClassName="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-6 sm:px-7 h-12 sm:h-[54px] text-sm sm:text-base font-medium transition-colors shadow-[0_8px_24px_rgba(168,65,42,0.18)]"
                        triggerLabel="Demander une démo"
                        testId="final-cta-demo-button"
                    />
                    <PillButton to="/contact" variant="outline" size="lg" testId="final-cta-contact">
                        Nous contacter
                    </PillButton>
                </div>
            </div>
        </section>
    );
}
