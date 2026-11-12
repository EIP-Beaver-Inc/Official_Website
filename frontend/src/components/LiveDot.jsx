export default function LiveDot({ color = 'bg-primary' }) {
    return (
        <span className="relative flex h-1.5 w-1.5">
            <span className={`absolute inline-flex h-full w-full rounded-full beaver-pulse-ring ${color}`} />
            <span className={`relative inline-flex h-1.5 w-1.5 rounded-full ${color}`} />
        </span>
    );
}
