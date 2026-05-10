export default function SectionHeader({ kicker, title, subtitle, align = 'left', testId }) {
    return (
        <div
            data-testid={testId || 'section-header'}
            data-animate="fade-up"
            className={align === 'center' ? 'text-center max-w-3xl mx-auto' : 'max-w-3xl'}
        >
            {kicker && (
                <div className="text-[11px] tracking-[0.22em] uppercase text-[hsl(var(--muted-foreground))]">
                    <span className="text-[hsl(var(--primary))] font-medium">{kicker.split(' · ')[0]}</span>
                    {kicker.includes(' · ') && <span> · {kicker.split(' · ').slice(1).join(' · ')}</span>}
                </div>
            )}
            {title && (
                <h2 className="mt-3 font-heading text-3xl sm:text-4xl lg:text-5xl leading-[1.05] tracking-[-0.015em]">
                    {title}
                </h2>
            )}
            {subtitle && (
                <p className="mt-4 text-sm sm:text-base leading-[1.7] text-[hsl(var(--muted-foreground))]">
                    {subtitle}
                </p>
            )}
        </div>
    );
}
