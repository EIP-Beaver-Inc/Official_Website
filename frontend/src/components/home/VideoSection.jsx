import { useRef, useState } from 'react';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import SectionHeader from '@/components/SectionHeader';
import { DEMO_VIDEO_URL, DEMO_VIDEO_FALLBACK_URL, VIDEO_POSTER_URL } from '@/lib/assets';

export default function VideoSection() {
    const videoRef = useRef(null);
    const [playing, setPlaying] = useState(false);
    const [muted, setMuted] = useState(true);
    const [errored, setErrored] = useState(false);

    const togglePlay = () => {
        const v = videoRef.current;
        if (!v) return;
        if (v.paused) {
            v.play().then(() => setPlaying(true)).catch(() => setErrored(true));
        } else {
            v.pause();
            setPlaying(false);
        }
    };
    const toggleMute = () => {
        const v = videoRef.current;
        if (!v) return;
        v.muted = !v.muted;
        setMuted(v.muted);
    };
    const onError = () => {
        // try fallback once
        const v = videoRef.current;
        if (!v) return;
        const sources = v.querySelectorAll('source');
        if (sources.length > 1 && v.currentSrc.includes(sources[0].src)) {
            v.src = sources[1].src;
            v.load();
        } else {
            setErrored(true);
        }
    };

    return (
        <section data-testid="home-video" className="py-16 sm:py-24 lg:py-32">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <SectionHeader
                    kicker="03 · Démo vidéo"
                    title={
                        <>
                            Le pipeline en <span className="brick-italic">conditions réelles.</span>
                        </>
                    }
                    subtitle="Captation sur ligne de sciage avec détections superposées — ROI redresse, BOBER classe, le tracker confirme."
                />

                <div
                    data-animate="fade-up"
                    className="mt-10 sm:mt-12 relative rounded-3xl overflow-hidden bg-[hsl(var(--card))] border border-black/5 shadow-[0_24px_60px_rgba(17,17,17,0.08)]"
                >
                    <div className="flex items-center justify-between px-4 sm:px-5 pt-4 pb-3 border-b border-black/5">
                        <div className="flex items-center gap-2">
                            <span className="inline-flex h-2 w-2 rounded-full bg-[hsl(var(--primary))]" />
                            <span className="text-[10px] tracking-[0.2em] uppercase text-[hsl(var(--muted-foreground))]">
                                Démo · BEAVER pipeline
                            </span>
                        </div>
                        <span className="text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--muted-foreground))]">
                            HD · 1080p
                        </span>
                    </div>
                    <div className="relative aspect-video bg-[hsl(38_45%_92%)]">
                        <video
                            ref={videoRef}
                            data-testid="demo-video-player"
                            poster={VIDEO_POSTER_URL}
                            controls
                            playsInline
                            preload="metadata"
                            className="absolute inset-0 h-full w-full object-cover"
                            onError={onError}
                            onPlay={() => setPlaying(true)}
                            onPause={() => setPlaying(false)}
                        >
                            <source src={DEMO_VIDEO_URL} type="video/mp4" />
                            <source src={DEMO_VIDEO_FALLBACK_URL} type="video/mp4" />
                            Votre navigateur ne supporte pas la vidéo HTML5.
                        </video>
                    </div>
                    <div className="flex flex-wrap items-center gap-3 sm:gap-5 border-t border-black/5 bg-[hsl(38_45%_94%)] px-4 sm:px-5 py-3">
                        <button
                            type="button"
                            data-testid="video-play-toggle"
                            onClick={togglePlay}
                            className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(10_62%_36%)] text-[hsl(var(--primary-foreground))] px-4 h-9 text-xs font-medium transition-colors"
                        >
                            {playing ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                            {playing ? 'Pause' : 'Lecture'}
                        </button>
                        <button
                            type="button"
                            data-testid="video-mute-toggle"
                            onClick={toggleMute}
                            className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--card))] border border-black/5 px-4 h-9 text-xs font-medium"
                        >
                            {muted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
                            {muted ? 'Activer le son' : 'Couper le son'}
                        </button>
                        <span className="ml-auto text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--muted-foreground))]">
                            {errored ? 'Vidéo indisponible' : 'Échantillon de démonstration'}
                        </span>
                    </div>
                </div>
            </div>
        </section>
    );
}
