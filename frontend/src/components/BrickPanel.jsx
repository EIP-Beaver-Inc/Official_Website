export default function BrickPanel({ glow = '90% 0%', className = '', children }) {
    return (
        <div className={`relative overflow-hidden rounded-[2rem] bg-primary text-primary-foreground ${className}`}>
            <div className="absolute inset-0 noise-overlay opacity-40 pointer-events-none" aria-hidden />
            <div
                className="absolute inset-0 pointer-events-none"
                aria-hidden
                style={{
                    background: `radial-gradient(50% 70% at ${glow}, hsl(32 90% 70% / 0.35) 0%, transparent 100%), radial-gradient(50% 60% at 10% 110%, hsl(14 70% 25% / 0.55) 0%, transparent 100%)`,
                }}
            />
            <div className="relative">{children}</div>
        </div>
    );
}
