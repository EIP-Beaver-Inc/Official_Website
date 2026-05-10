export default function LiveBadge({ label = 'Pipeline IA · Temps réel' }) {
    return (
        <span
            data-testid="live-pipeline-badge"
            className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--card))] border border-black/5 px-3 py-1.5 text-[11px] tracking-[0.18em] uppercase text-[hsl(var(--foreground))]"
        >
            <span className="relative inline-flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full rounded-full bg-[hsl(var(--primary))] beaver-pulse-ring" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-[hsl(var(--primary))]" />
            </span>
            {label}
        </span>
    );
}
