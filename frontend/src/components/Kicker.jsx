export default function Kicker({ index, children, className = '' }) {
    return (
        <div className={`font-mono-ui text-xs uppercase tracking-[0.14em] text-muted-foreground flex items-center gap-3 ${className}`}>
            {index && <span className="text-primary">[{index}]</span>}
            <span>{children}</span>
        </div>
    );
}
