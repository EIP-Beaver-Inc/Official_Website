import LiveBadge from '@/components/LiveBadge';
import PillButton from '@/components/PillButton';
import DemoDialog from '@/components/DemoDialog';
import { LOGO_URL } from '@/lib/assets';

export default function Hero() {
    return (
        <section data-testid="home-hero" className="relative overflow-hidden hero-bg">
            <div className="absolute inset-0 noise-overlay opacity-60 pointer-events-none" aria-hidden />
            <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 sm:pt-20 sm:pb-28 lg:pt-28 lg:pb-32">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
                    <div className="lg:col-span-7">
                        <div data-animate="fade-up">
                            <LiveBadge />
                        </div>
                        <h1
                            data-animate="fade-up"
                            className="mt-6 font-heading text-[44px] leading-[1.02] tracking-[-0.025em] sm:text-6xl lg:text-7xl xl:text-[80px] font-light"
                        >
                            La vision par<br />
                            ordinateur<br className="hidden sm:block" />
                            <span className="sm:inline"> au service des </span>
                            <span className="brick-italic font-normal">scieries.</span>
                        </h1>
                        <p
                            data-animate="fade-up"
                            className="mt-6 max-w-xl text-base sm:text-lg leading-[1.65] text-[hsl(var(--muted-foreground))]"
                        >
                            Beaver analyse le flux vidéo de votre ligne de production planche par planche, localise <span className="text-[hsl(var(--foreground))] font-medium">9 types de défauts</span> et produit un rapport qualité conforme à la norme <span className="text-[hsl(var(--foreground))] font-medium">EN 975-1</span>.
                        </p>

                        <div data-animate="fade-up" className="mt-8 flex flex-wrap items-center gap-3 sm:gap-4">
                            <PillButton to="/quiz" size="lg" testId="hero-cta-quiz">
                                Tester le quiz EN 975-1
                            </PillButton>
                            <DemoDialog
                                triggerClassName="inline-flex items-center justify-center rounded-full bg-transparent border border-black/15 text-[hsl(var(--foreground))] hover:bg-[hsl(var(--card))] h-12 sm:h-[54px] px-6 sm:px-7 text-sm sm:text-base font-medium transition-colors"
                                triggerLabel="Parler à un ingénieur"
                                testId="hero-cta-engineer"
                            />
                        </div>

                        <div
                            data-testid="hero-stats"
                            data-animate="fade-up"
                            className="mt-12 sm:mt-16 grid grid-cols-3 gap-6 sm:gap-10 max-w-md"
                        >
                            {[
                                { label: 'Défauts', value: '9' },
                                { label: 'Frames min.', value: '40' },
                                { label: 'Classes', value: '4' },
                            ].map((s) => (
                                <div key={s.label}>
                                    <div className="label-caps">{s.label}</div>
                                    <div className="mt-2 font-heading italic text-[hsl(var(--primary))] text-5xl sm:text-6xl leading-none">
                                        {s.value}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="lg:col-span-5">
                        <div data-animate="fade-up" className="relative">
                            <div
                                data-testid="hero-annotated-media"
                                className="relative overflow-hidden rounded-3xl bg-[hsl(var(--card))] border border-black/5 shadow-[0_24px_60px_rgba(17,17,17,0.12)]"
                            >
                                <div className="flex items-center justify-between px-4 sm:px-5 pt-4 pb-3 border-b border-black/5">
                                    <div className="flex items-center gap-2">
                                        <span className="inline-flex h-2 w-2 rounded-full bg-[hsl(var(--primary))]" />
                                        <span className="text-[10px] tracking-[0.2em] uppercase text-[hsl(var(--muted-foreground))]">
                                            Session en cours · ROI / BOBER
                                        </span>
                                    </div>
                                    <span className="text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--muted-foreground))]">#2471</span>
                                </div>

                                <div className="aspect-[4/3] bg-[hsl(38_45%_92%)]">
                                    <img
                                        src="/assets/wood_7_Q-B_1.jpg"
                                        alt="Planche de chêne Q-B 1"
                                        className="h-full w-full object-contain"
                                    />
                                </div>

                                <div className="grid grid-cols-3 gap-2 border-t border-black/5 bg-[hsl(38_50%_94%)] p-4">
                                    <div>
                                        <div className="label-caps">Planche</div>
                                        <div className="mt-1 font-heading text-xl">#2471</div>
                                    </div>
                                    <div>
                                        <div className="label-caps">Classe</div>
                                        <div className="mt-1 font-heading text-xl">Q-B 1</div>
                                    </div>
                                    <div>
                                        <div className="label-caps">Norme</div>
                                        <div className="mt-1 font-heading text-xl">EN 975-1</div>
                                    </div>
                                </div>
                            </div>

                            <div className="absolute -top-6 -left-6 sm:-top-8 sm:-left-8 h-16 w-16 sm:h-20 sm:w-20 rounded-full overflow-hidden ring-2 ring-[hsl(var(--card))] shadow-lg">
                                <img src={LOGO_URL} alt="" className="h-full w-full object-cover" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
