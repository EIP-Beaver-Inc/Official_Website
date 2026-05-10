import { useEffect, useRef } from 'react';

/**
 * Activate fade-up entrance on any element marked with data-animate="fade-up".
 * Hooked once at the App level. Adds is-visible class once intersecting.
 */
export function useFadeUpObserver() {
    const observerRef = useRef(null);

    useEffect(() => {
        if (typeof window === 'undefined' || typeof IntersectionObserver === 'undefined') return;

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
        );
        observerRef.current = observer;

        const elements = document.querySelectorAll('[data-animate="fade-up"]:not(.is-visible)');
        elements.forEach((el) => observer.observe(el));

        // Re-scan when DOM changes (route changes, content swap)
        const mo = new MutationObserver(() => {
            const fresh = document.querySelectorAll('[data-animate="fade-up"]:not(.is-visible)');
            fresh.forEach((el) => {
                if (!el.dataset.observed) {
                    el.dataset.observed = '1';
                    observer.observe(el);
                }
            });
        });
        mo.observe(document.body, { childList: true, subtree: true });

        return () => {
            observer.disconnect();
            mo.disconnect();
        };
    }, []);
}
