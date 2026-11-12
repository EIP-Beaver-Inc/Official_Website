import PageHero from '@/components/PageHero';
import PillButton from '@/components/PillButton';
import { PLANK_IMAGE } from '@/lib/plank';

export default function NotFound() {
    return (
        <section className="max-w-4xl mx-auto px-4 sm:px-6 py-16 sm:py-24 text-center">
            <PageHero
                align="center"
                kicker="404 · Page introuvable"
                title={
                    <>
                        Cette planche n’a pas passé le <span className="text-primary">tracker.</span>
                    </>
                }
                subtitle="La page demandée n’existe pas. Retour à l’accueil pour reprendre l’analyse."
            />

            <div
                className="relative mt-12 mx-auto aspect-[3/1] max-w-2xl overflow-hidden rounded-3xl shadow-[0_30px_70px_-35px_rgba(60,35,20,0.5)]"
                data-animate="fade-up"
                aria-hidden
            >
                <div
                    className="absolute inset-0 bg-no-repeat"
                    style={{ backgroundImage: `url(${PLANK_IMAGE})`, backgroundSize: '300% auto', backgroundPosition: '48% 40%' }}
                />
                <div className="absolute left-1/2 top-1/2 h-[48%] w-[28%] -translate-x-1/2 -translate-y-1/2 rounded-lg border-2 border-dashed border-primary bg-primary/10">
                    <span className="absolute bottom-full left-0 mb-1.5 whitespace-nowrap rounded bg-primary px-2 py-1 font-mono-ui text-[0.6875rem] leading-none text-primary-foreground">
                        404 · Page introuvable
                    </span>
                </div>
            </div>

            <PillButton to="/" size="lg" className="mt-12" testId="notfound-home-link">
                Retour à l’accueil
            </PillButton>
        </section>
    );
}
