import { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { LOGO_URL, WORDMARK_URL } from '@/lib/assets';
import DemoDialog from '@/components/DemoDialog';

const NAV = [
    { to: '/', label: 'Accueil' },
    { to: '/quiz', label: 'Quiz · EN 975-1' },
    { to: '/beta', label: 'Accès beta' },
    { to: '/contact', label: 'Contact' },
];

export default function Header() {
    const [open, setOpen] = useState(false);
    const location = useLocation();

    return (
        <header
            data-testid="site-header"
            className="fixed inset-x-0 top-3 sm:top-5 z-40 px-3 sm:px-6 pointer-events-none"
        >
            <div className="pointer-events-auto max-w-5xl mx-auto rounded-2xl bg-[hsla(42,36%,97%,0.92)] backdrop-blur-md border border-black/5 shadow-[0_12px_40px_rgba(17,17,17,0.18)] px-3 sm:px-4 h-14 sm:h-16 flex items-center justify-between gap-4">
                <Link
                    to="/"
                    data-testid="site-logo"
                    className="flex items-center gap-3 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] rounded-full pr-2"
                >
                    <span className="h-11">
                        <img
                            src={LOGO_URL}
                            alt="Beaver logo"
                            className="h-full w-full object-cover"
                            loading="eager"
                        />
                    </span>
                    <img src={WORDMARK_URL} alt="Beaver" className="h-6 sm:h-7 w-auto" loading="eager" />
                </Link>

                <nav
                    data-testid="site-nav"
                    className="hidden md:flex items-center gap-7 text-sm"
                >
                    {NAV.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.to === '/'}
                            data-testid={`nav-link-${item.label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`}
                            className={({ isActive }) =>
                                `transition-colors duration-150 ease-out hover:text-[hsl(var(--primary))] ${
                                    isActive
                                        ? 'text-[hsl(var(--primary))] font-medium'
                                        : 'text-[hsl(var(--foreground))]'
                                }`
                            }
                        >
                            {item.label}
                        </NavLink>
                    ))}
                </nav>

                <div className="flex items-center gap-2">
                    <DemoDialog
                        triggerClassName="hidden sm:inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-4 lg:px-5 h-10 lg:h-11 text-sm font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--background))]"
                        triggerLabel="Demander un devis"
                        testId="header-request-demo-button"
                    />
                    <button
                        type="button"
                        data-testid="mobile-menu-toggle"
                        onClick={() => setOpen((v) => !v)}
                        className="md:hidden inline-flex items-center justify-center h-10 w-10 rounded-full border border-black/5 bg-[hsl(var(--card))] text-[hsl(var(--foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
                        aria-label="Ouvrir le menu"
                    >
                        {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                    </button>
                </div>
            </div>

            {open && (
                <div
                    className="pointer-events-auto md:hidden max-w-5xl mx-auto mt-2 rounded-2xl border border-black/5 bg-[hsl(var(--background))] shadow-[0_12px_40px_rgba(17,17,17,0.18)]"
                    data-testid="mobile-menu"
                >
                    <nav className="px-3 py-3 flex flex-col gap-1">
                        {NAV.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end={item.to === '/'}
                                onClick={() => setOpen(false)}
                                className={({ isActive }) =>
                                    `px-3 py-2 rounded-lg text-sm transition-colors ${
                                        isActive
                                            ? 'bg-[hsl(var(--card))] text-[hsl(var(--primary))]'
                                            : 'text-[hsl(var(--foreground))] hover:bg-[hsl(var(--card))]'
                                    }`
                                }
                                key2={location.pathname}
                            >
                                {item.label}
                            </NavLink>
                        ))}
                        <div className="pt-2">
                            <DemoDialog
                                triggerClassName="w-full inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium"
                                triggerLabel="Demander un devis"
                                testId="mobile-request-demo-button"
                            />
                        </div>
                    </nav>
                </div>
            )}
        </header>
    );
}
