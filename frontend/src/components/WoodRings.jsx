import { useEffect, useRef } from 'react';

function mulberry32(seed) {
    return () => {
        seed |= 0;
        seed = (seed + 0x6d2b79f5) | 0;
        let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

function closedCurve(points) {
    const n = points.length;
    let d = `M${points[0][0].toFixed(1)} ${points[0][1].toFixed(1)}`;
    for (let i = 0; i < n; i++) {
        const p0 = points[(i - 1 + n) % n];
        const p1 = points[i];
        const p2 = points[(i + 1) % n];
        const p3 = points[(i + 2) % n];
        const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
        const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
        d += `C${c1[0].toFixed(1)} ${c1[1].toFixed(1)} ${c2[0].toFixed(1)} ${c2[1].toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
    }
    return `${d}Z`;
}

function growthRings(seed, count) {
    const rand = mulberry32(seed);
    const harmonics = [2, 3, 4, 5, 7].map((k) => ({ k, amp: 0.02 + rand() * 0.05, phase: rand() * Math.PI * 2 }));
    const knot = { angle: rand() * Math.PI * 2, strength: 0.18 + rand() * 0.1 };
    const rings = [];
    let radius = 14;
    for (let i = 0; i < count; i++) {
        radius += 16 + rand() * 20;
        const points = [];
        for (let j = 0; j < 96; j++) {
            const a = (j / 96) * Math.PI * 2;
            let r = 1;
            for (const h of harmonics) r += h.amp * Math.sin(h.k * a + h.phase + i * 0.08);
            const da = Math.atan2(Math.sin(a - knot.angle), Math.cos(a - knot.angle));
            r += knot.strength * Math.exp(-(da * da) / 0.05) * Math.exp(-i / 6);
            points.push([Math.cos(a) * radius * r, Math.sin(a) * radius * r]);
        }
        rings.push(closedCurve(points));
    }
    return rings;
}

const LAYERS = [
    { rings: growthRings(7, 16), className: 'left-[70%] top-[8%] w-[120vmax]', spin: 0.02, drift: 0.15 },
    { rings: growthRings(23, 12), className: 'left-[-2%] top-[72%] w-[85vmax]', spin: -0.026, drift: 0.15 },
    { rings: growthRings(41, 10), className: 'left-[40%] top-[125%] w-[70vmax]', spin: 0.03, drift: 0.5 },
];

export default function WoodRings() {
    const layerRefs = useRef([]);

    useEffect(() => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        let lastY = window.scrollY;
        let velocity = 0;
        let raf = 0;

        const tick = () => {
            const y = window.scrollY;
            velocity = velocity * 0.85 + (y - lastY) * 0.15;
            lastY = y;
            const squeeze = 1 - Math.min(0.08, Math.abs(velocity) * 0.002);

            LAYERS.forEach((layer, i) => {
                const el = layerRefs.current[i];
                if (!el) return;
                const travel = window.innerHeight * 2.2;
                const scrolled = y * layer.drift;
                const dy = -(layer.drift > 0.3 ? scrolled % travel : scrolled);
                el.style.transform = `translate(-50%, calc(-50% + ${dy}px)) rotate(${y * layer.spin}deg) scale(${squeeze})`;
            });
            raf = Math.abs(velocity) > 0.05 ? requestAnimationFrame(tick) : 0;
        };
        const onScroll = () => {
            if (!raf) raf = requestAnimationFrame(tick);
        };

        tick();
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', onScroll);
            cancelAnimationFrame(raf);
        };
    }, []);

    return (
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none" aria-hidden>
            {LAYERS.map((layer, i) => (
                <svg
                    key={i}
                    ref={(el) => (layerRefs.current[i] = el)}
                    viewBox="-500 -500 1000 1000"
                    className={`absolute aspect-square will-change-transform ${layer.className}`}
                    style={{ transform: 'translate(-50%, -50%)', overflow: 'visible' }}
                >
                    {layer.rings.map((d, j) => (
                        <path
                            key={j}
                            d={d}
                            pathLength="1"
                            fill="none"
                            stroke="hsl(25 40% 28%)"
                            strokeOpacity={j % 3 === 0 ? 0.2 : 0.11}
                            strokeWidth={j % 3 === 0 ? 1.4 : 0.9}
                            className="wood-ring-grow"
                            style={{ animationDelay: `${j * 80 + i * 250}ms` }}
                        />
                    ))}
                </svg>
            ))}
        </div>
    );
}
