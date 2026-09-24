import { useEffect, useRef, useState } from 'react';
import { ArrowDown } from 'lucide-react';
import PillButton from '@/components/PillButton';
import DemoDialog from '@/components/DemoDialog';
import { HERO_VIDEOS } from '@/lib/assets';

const ERROR_SKIP_DELAY_MS = 6000;

export default function Hero() {
    const [active, setActive] = useState(0);
    const videoRefs = useRef([]);
    const sectionRef = useRef(null);
    const next = () => setActive((i) => (i + 1) % HERO_VIDEOS.length);

    useEffect(() => {
        videoRefs.current.forEach((video, i) => {
            if (!video) return;
            if (i === active) {
                video.currentTime = 0;
                video.play().catch(() => {});
            } else {
                video.pause();
            }
        });
    }, [active]);

    const handleError = (i) => {
        if (i !== active || HERO_VIDEOS.length < 2) return;
        setTimeout(next, ERROR_SKIP_DELAY_MS);
    };

    const scrollDown = () => {
        const el = sectionRef.current;
        if (el) window.scrollTo({ top: el.offsetTop + el.offsetHeight, behavior: 'smooth' });
    };

    return (
        <section
            ref={sectionRef}
            data-testid="home-hero"
            className="relative overflow-hidden min-h-[100svh] flex items-center justify-center bg-[#111]"
        >
            <div className="absolute inset-0" aria-hidden>
                {HERO_VIDEOS.map((video, i) => (
                    <video
                        key={video.src}
                        ref={(el) => (videoRefs.current[i] = el)}
                        src={video.src}
                        poster={video.poster}
                        muted
                        playsInline
                        autoPlay={i === 0}
                        loop={HERO_VIDEOS.length === 1}
                        preload={i === 0 ? 'auto' : 'metadata'}
                        onEnded={next}
                        onError={() => handleError(i)}
                        className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-1000 ease-out ${
                            i === active ? 'opacity-100' : 'opacity-0'
                        }`}
                    />
                ))}
                <div className="absolute inset-0 bg-gradient-to-b from-[hsl(25_35%_8%/0.65)] via-[hsl(25_35%_8%/0.45)] to-[hsl(25_35%_8%/0.75)]" />
            </div>

            <div className="relative w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-28 text-center text-white">
                <h1
                    data-animate="fade-up"
                    className="font-display font-bold uppercase text-[2.5rem] leading-[0.95] tracking-[-0.04em] sm:text-6xl lg:text-7xl xl:text-[5.5rem]"
                >
                    L'œil qui ne laisse
                    <br />
                    <span className="text-[hsl(var(--brick-light))]">rien</span> passer.
                </h1>
                <p
                    data-animate="fade-up"
                    className="mt-6 mx-auto max-w-2xl text-lg sm:text-xl leading-[1.5] text-white/75"
                >
                    L'IA qui trie le bois <span className="text-white font-medium">plus vite qu'un œil humain ne cligne.</span>
                </p>

                <div data-animate="fade-up" className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
                    <PillButton to="/quiz" size="lg" testId="hero-cta-quiz">
                        Tester le quiz EN 975-1
                    </PillButton>
                    <DemoDialog
                        triggerClassName="inline-flex items-center justify-center rounded-full bg-white/5 backdrop-blur-sm border border-white/30 text-white hover:bg-white/15 h-12 sm:h-[3.375rem] px-6 sm:px-7 text-sm sm:text-base font-medium transition-colors"
                        triggerLabel="Parler à un ingénieur"
                        testId="hero-cta-engineer"
                    />
                </div>
            </div>

            {HERO_VIDEOS.length > 1 && (
                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-2" data-testid="hero-video-dots">
                    {HERO_VIDEOS.map((video, i) => (
                        <button
                            key={video.src}
                            type="button"
                            onClick={() => setActive(i)}
                            aria-label={`Vidéo ${i + 1}`}
                            className={`h-2.5 w-2.5 rounded-full border border-white transition-colors ${
                                i === active ? 'bg-white' : 'bg-transparent hover:bg-white/40'
                            }`}
                        />
                    ))}
                </div>
            )}

            <button
                type="button"
                onClick={scrollDown}
                aria-label="Défiler vers le bas"
                className="absolute bottom-6 right-6 sm:bottom-8 sm:right-8 inline-flex h-11 w-11 items-center justify-center rounded-lg border border-white/60 text-white hover:bg-white/10 transition-colors"
            >
                <ArrowDown className="h-4 w-4" />
            </button>
        </section>
    );
}
