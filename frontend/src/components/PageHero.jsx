import Kicker from '@/components/Kicker';

export default function PageHero({ kicker, title, subtitle, align = 'left', size = 'lg', className = '', children }) {
    const center = align === 'center';
    const titleSize =
        size === 'lg' ? 'text-5xl sm:text-6xl lg:text-7xl leading-[0.95] tracking-[-0.045em]' : 'text-4xl sm:text-5xl leading-[1] tracking-[-0.04em]';

    return (
        <header className={`relative isolate ${center ? 'text-center' : ''} ${className}`} data-animate="fade-up">
            <div
                className="absolute -inset-x-40 -top-40 h-[32rem] -z-10 pointer-events-none"
                aria-hidden
                style={{
                    background:
                        'radial-gradient(40% 55% at 30% 45%, hsl(38 60% 86%) 0%, transparent 100%), radial-gradient(hsl(25 18% 11% / 0.07) 1px, transparent 1px)',
                    backgroundSize: 'auto, 1.375rem 1.375rem',
                    maskImage: 'radial-gradient(60% 60% at 40% 40%, black, transparent)',
                    WebkitMaskImage: 'radial-gradient(60% 60% at 40% 40%, black, transparent)',
                }}
            />
            {kicker && <Kicker className={center ? 'justify-center' : ''}>{kicker}</Kicker>}
            <h1 className={`mt-5 [text-wrap:balance] font-display font-semibold text-foreground ${titleSize} ${center ? 'mx-auto' : ''} max-w-4xl`}>
                {title}
            </h1>
            {subtitle && (
                <p className={`mt-6 max-w-2xl text-base sm:text-lg leading-relaxed text-muted-foreground ${center ? 'mx-auto' : ''}`}>{subtitle}</p>
            )}
            {children}
        </header>
    );
}
