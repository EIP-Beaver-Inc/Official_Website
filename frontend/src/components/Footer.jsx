import { Link } from 'react-router-dom';
import { LOGO_URL } from '@/lib/assets';

export default function Footer() {
    return (
        <footer
            data-testid="site-footer"
            className="mt-12 border-t border-black/5 bg-[hsl(var(--card))]"
        >
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="flex items-start gap-3">
                        <span className="inline-flex h-10 w-10 rounded-full overflow-hidden bg-[hsl(38_45%_92%)] ring-1 ring-black/5">
                            <img src={LOGO_URL} alt="" className="h-full w-full object-cover" />
                        </span>
                        <div>
                            <div className="font-heading text-[hsl(var(--primary))] text-xl">Beaver</div>
                            <div className="label-caps mt-1">Vision IA · Scieries</div>
                            <p className="mt-3 text-sm text-[hsl(var(--muted-foreground))] max-w-xs leading-relaxed">
                                Détection automatique de défauts sur planches de bois. Pipeline IA temps réel conforme à la norme EN 975-1.
                            </p>
                        </div>
                    </div>

                    <div>
                        <div className="label-caps">Navigation</div>
                        <ul className="mt-3 space-y-2 text-sm">
                            <li>
                                <Link to="/" className="hover:text-[hsl(var(--primary))] transition-colors">
                                    Accueil
                                </Link>
                            </li>
                            <li>
                                <Link to="/quiz" className="hover:text-[hsl(var(--primary))] transition-colors">
                                    Quiz EN 975-1
                                </Link>
                            </li>
                            <li>
                                <Link to="/contact" className="hover:text-[hsl(var(--primary))] transition-colors">
                                    Contact
                                </Link>
                            </li>
                        </ul>
                    </div>

                    <div>
                        <div className="label-caps">Légal</div>
                        <ul className="mt-3 space-y-2 text-sm text-[hsl(var(--muted-foreground))]">
                            <li>© {new Date().getFullYear()} BEAVER — Tous droits réservés.</li>
                            <li>Pipeline propriétaire · ROI · BOBER · DefectTracker</li>
                            <li>Conforme NF EN 975-1 (feuillus / chêne)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </footer>
    );
}
