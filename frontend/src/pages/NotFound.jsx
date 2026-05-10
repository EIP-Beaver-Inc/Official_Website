export default function NotFound() {
    return (
        <section className="max-w-3xl mx-auto px-4 py-20 sm:py-32 text-center">
            <div className="label-caps">404 · Page introuvable</div>
            <h1 className="mt-4 font-heading text-4xl sm:text-5xl tracking-tight">
                Cette planche n’a pas passé le <span className="brick-italic">tracker.</span>
            </h1>
            <p className="mt-4 text-[hsl(var(--muted-foreground))]">
                La page demandée n’existe pas. Retour à l’accueil pour reprendre l’analyse.
            </p>
            <a
                href="/"
                data-testid="notfound-home-link"
                className="inline-flex mt-8 items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors"
            >
                Retour à l’accueil
            </a>
        </section>
    );
}
