import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, ArrowRight, Award, CheckCircle2, Lock, RotateCcw, XCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import DemoDialog from '@/components/DemoDialog';
import PillButton from '@/components/PillButton';
import PageHero from '@/components/PageHero';
import { fetchQuiz, submitQuiz } from '@/lib/api';

const STAGE = {
    INTRO: 'intro',
    QUESTION: 'question',
    EMAIL: 'email',
    RESULT: 'result',
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const letter = (optionId) => optionId.toUpperCase();

function OptionList({ options, selectedId, onSelect }) {
    return (
        <ul className="grid grid-cols-1 gap-3">
            {options.map((opt) => {
                const active = selectedId === opt.id;
                return (
                    <li key={opt.id}>
                        <button
                            type="button"
                            data-testid="quiz-answer-option"
                            data-key={opt.id}
                            onClick={() => onSelect(opt.id)}
                            aria-pressed={active}
                            className={`group w-full flex items-center gap-4 rounded-2xl border px-4 py-4 text-left transition-[border-color,background-color,box-shadow] duration-200 ${
                                active
                                    ? 'border-primary bg-primary/5 shadow-[0_0_0_4px_hsl(var(--primary)/0.08)]'
                                    : 'border-black/10 bg-background hover:border-black/25'
                            }`}
                        >
                            <span
                                className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl font-display font-semibold transition-colors ${
                                    active ? 'bg-primary text-primary-foreground' : 'bg-card border border-black/10 text-muted-foreground group-hover:text-foreground'
                                }`}
                            >
                                {letter(opt.id)}
                            </span>
                            <span className={`text-[15px] leading-snug ${active ? 'text-foreground font-medium' : 'text-foreground/90'}`}>{opt.text}</span>
                        </button>
                    </li>
                );
            })}
        </ul>
    );
}

export default function Quiz() {
    const [stage, setStage] = useState(STAGE.INTRO);
    const [data, setData] = useState({ title: '', description: '', questions: [], total: 0 });
    const [loading, setLoading] = useState(true);
    const [idx, setIdx] = useState(0);
    const [answers, setAnswers] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [contact, setContact] = useState({ nom: '', email: '', entreprise: '' });

    useEffect(() => {
        let mounted = true;
        fetchQuiz()
            .then((d) => {
                if (mounted) setData(d);
            })
            .catch(() => toast.error('Impossible de charger le quiz.'))
            .finally(() => mounted && setLoading(false));
        return () => {
            mounted = false;
        };
    }, []);

    const total = data.questions.length;
    const current = data.questions[idx];
    const answeredCount = Object.keys(answers).length;
    const progressPct = total ? Math.round((answeredCount / total) * 100) : 0;
    const emailValid = EMAIL_PATTERN.test(contact.email.trim());

    const scrollTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    const setAnswer = (qid, value) => setAnswers((s) => ({ ...s, [qid]: value }));

    const goNext = () => {
        if (!current) return;
        if (!answers[current.id]) {
            toast.error('Choisissez une réponse avant de continuer.');
            return;
        }
        if (idx + 1 < total) setIdx(idx + 1);
        else setStage(STAGE.EMAIL);
        scrollTop();
    };
    const goPrev = () => {
        if (idx > 0) setIdx(idx - 1);
        else setStage(STAGE.INTRO);
        scrollTop();
    };

    const send = async (e) => {
        e.preventDefault();
        if (!emailValid) {
            toast.error('Entrez une adresse email valide pour voir vos résultats.');
            return;
        }
        try {
            setSubmitting(true);
            const res = await submitQuiz({
                answers: Object.entries(answers).map(([question_id, selected]) => ({ question_id, selected })),
                email: contact.email.trim(),
                nom: contact.nom.trim() || null,
                entreprise: contact.entreprise.trim() || null,
            });
            setResult(res);
            setStage(STAGE.RESULT);
            scrollTop();
        } catch {
            toast.error("Échec de l'envoi du quiz. Réessayez.");
        } finally {
            setSubmitting(false);
        }
    };

    const restart = () => {
        setIdx(0);
        setAnswers({});
        setResult(null);
        setStage(STAGE.INTRO);
        scrollTop();
    };

    if (loading) {
        return (
            <section className="max-w-5xl mx-auto px-4 py-20">
                <div className="animate-pulse h-8 w-48 bg-muted rounded" />
                <div className="mt-6 h-64 bg-muted rounded-2xl" />
            </section>
        );
    }

    return (
        <section data-testid="quiz-page" className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
            {stage === STAGE.INTRO && (
                <div data-animate="fade-up" className="mt-6">
                    <PageHero kicker={`Quiz EN 975-1 · ${total} questions`} title={data.title} subtitle={data.description} />

                    <dl className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 max-w-3xl">
                        {[
                            ['Questions', total],
                            ['Choix par question', 4],
                            ['Correction', 'Détaillée'],
                        ].map(([label, value]) => (
                            <div key={label} className="rounded-3xl border border-black/5 bg-card p-5">
                                <dt className="label-caps">{label}</dt>
                                <dd className="mt-2 font-display font-semibold text-3xl tracking-[-0.04em] text-foreground">{value}</dd>
                            </div>
                        ))}
                    </dl>

                    <div className="mt-10 flex flex-wrap gap-3">
                        <PillButton onClick={() => setStage(STAGE.QUESTION)} size="lg" testId="quiz-start-button">
                            Commencer le quiz
                        </PillButton>
                        <PillButton to="/" variant="outline" size="lg" icon={false} testId="quiz-back-home">
                            Retour à l'accueil
                        </PillButton>
                    </div>
                </div>
            )}

            {stage === STAGE.QUESTION && current && (
                <div className="mt-6 max-w-3xl mx-auto">
                    <div data-testid="quiz-progress" className="flex items-center gap-4">
                        <span className="font-display font-semibold text-sm sm:text-base whitespace-nowrap">
                            <span className="text-primary">{String(idx + 1).padStart(2, '0')}</span>
                            <span className="text-muted-foreground">&nbsp;/ {total}</span>
                        </span>
                        <Progress value={progressPct} className="h-1.5 bg-muted [&>div]:bg-primary" />
                    </div>

                    <div
                        key={current.id}
                        data-testid="quiz-question-card"
                        className="mt-8 rounded-[2rem] border border-black/5 bg-card p-6 sm:p-10 shadow-[0_30px_70px_-40px_rgba(60,35,20,0.35)]"
                    >
                        <div className="label-caps">Question {String(idx + 1).padStart(2, '0')}</div>
                        <h2 className="mt-4 [text-wrap:balance] font-display font-semibold text-2xl sm:text-3xl leading-[1.2] tracking-[-0.03em] text-foreground">
                            {current.question}
                        </h2>

                        <div className="mt-8">
                            <OptionList options={current.options} selectedId={answers[current.id]} onSelect={(id) => setAnswer(current.id, id)} />
                        </div>

                        <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                            <button
                                type="button"
                                data-testid="quiz-prev-button"
                                onClick={goPrev}
                                className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-background transition-colors"
                            >
                                <ArrowLeft className="h-4 w-4" /> Précédent
                            </button>
                            <div className="flex items-center gap-3">
                                <span className="text-xs text-muted-foreground">
                                    {answeredCount}/{total} répondues
                                </span>
                                <button
                                    type="button"
                                    data-testid="quiz-next-button"
                                    onClick={goNext}
                                    className="inline-flex items-center justify-center gap-2 rounded-full bg-primary hover:bg-[hsl(14_66%_38%)] text-primary-foreground px-5 h-11 text-sm font-medium transition-colors"
                                >
                                    {idx + 1 === total ? 'Terminer' : 'Suivant'}
                                    <ArrowRight className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {stage === STAGE.EMAIL && (
                <form
                    onSubmit={send}
                    data-testid="quiz-email-card"
                    data-animate="fade-up"
                    className="mt-6 max-w-3xl mx-auto rounded-[2rem] border border-black/5 bg-card p-6 sm:p-10 shadow-[0_30px_70px_-40px_rgba(60,35,20,0.35)]"
                >
                    <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                        <Lock className="h-5 w-5" />
                    </span>
                    <h2 className="mt-6 font-display font-semibold text-3xl sm:text-4xl tracking-[-0.04em] text-foreground">
                        Votre score est <span className="text-primary">prêt.</span>
                    </h2>
                    <p className="mt-3 max-w-xl text-muted-foreground">
                        Entrez votre email pour débloquer votre score et la correction détaillée des {total} questions.
                    </p>

                    <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-5">
                        <div className="sm:col-span-2 flex flex-col gap-2">
                            <Label htmlFor="q-email" className="label-caps">
                                Email <span className="text-primary">*</span>
                            </Label>
                            <Input
                                id="q-email"
                                type="email"
                                required
                                autoFocus
                                autoComplete="email"
                                data-testid="quiz-email-input-email"
                                value={contact.email}
                                onChange={(e) => setContact((s) => ({ ...s, email: e.target.value }))}
                                placeholder="vous@scierie.fr"
                                className="bg-background"
                            />
                        </div>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="q-nom" className="label-caps">
                                Nom
                            </Label>
                            <Input
                                id="q-nom"
                                autoComplete="name"
                                data-testid="quiz-email-input-nom"
                                value={contact.nom}
                                onChange={(e) => setContact((s) => ({ ...s, nom: e.target.value }))}
                                className="bg-background"
                            />
                        </div>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="q-ent" className="label-caps">
                                Entreprise
                            </Label>
                            <Input
                                id="q-ent"
                                autoComplete="organization"
                                data-testid="quiz-email-input-entreprise"
                                value={contact.entreprise}
                                onChange={(e) => setContact((s) => ({ ...s, entreprise: e.target.value }))}
                                className="bg-background"
                            />
                        </div>
                    </div>

                    <div className="mt-10 flex flex-wrap items-center justify-between gap-3">
                        <button
                            type="button"
                            onClick={() => setStage(STAGE.QUESTION)}
                            className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-background transition-colors"
                        >
                            <ArrowLeft className="h-4 w-4" /> Revenir aux questions
                        </button>
                        <button
                            type="submit"
                            data-testid="quiz-submit-with-email-button"
                            disabled={submitting || !emailValid}
                            className="inline-flex items-center justify-center gap-2 rounded-full bg-primary hover:bg-[hsl(14_66%_38%)] disabled:opacity-50 disabled:cursor-not-allowed text-primary-foreground px-6 h-12 text-sm font-medium transition-colors"
                        >
                            {submitting ? 'Calcul…' : 'Voir mes résultats'}
                            <ArrowRight className="h-4 w-4" />
                        </button>
                    </div>
                </form>
            )}

            {stage === STAGE.RESULT && result && <ResultPanel result={result} onRestart={restart} />}
        </section>
    );
}

function ResultPanel({ result, onRestart }) {
    const tier = useMemo(() => {
        const p = result.percentage;
        if (p >= 85) return 'Expert EN 975-1';
        if (p >= 65) return 'Bonne maîtrise';
        if (p >= 40) return 'En progression';
        return 'Découverte';
    }, [result.percentage]);

    return (
        <div data-testid="quiz-result" data-animate="fade-up" className="mt-6">
            <div className="rounded-[2rem] overflow-hidden border border-black/5 bg-card shadow-[0_30px_70px_-40px_rgba(60,35,20,0.35)]">
                <div className="p-6 sm:p-10 lg:p-14 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                    <div className="lg:col-span-7">
                        <div className="label-caps">Résultat</div>
                        <div className="mt-3 font-display font-semibold text-6xl sm:text-7xl tracking-[-0.05em]">
                            <span data-testid="quiz-score-value" className="text-primary">
                                {result.score}
                            </span>
                            <span className="text-muted-foreground"> / {result.total}</span>
                        </div>
                        <div className="mt-3 font-display font-semibold text-2xl text-foreground">
                            <Award className="inline-block h-5 w-5 mr-2 -mt-1 text-primary" />
                            {tier}
                        </div>
                        <p className="mt-4 text-muted-foreground leading-relaxed max-w-xl">
                            Vous avez répondu correctement à <span className="text-foreground font-medium">{result.percentage}%</span> des questions sur le
                            classement d'aspect EN 975-1.
                        </p>
                    </div>
                    <div className="lg:col-span-5">
                        <div className="rounded-3xl border border-black/5 bg-background p-6">
                            <div className="label-caps">Pour aller plus loin</div>
                            <p className="mt-3 text-sm leading-relaxed">
                                Voyez ce que Beaver fait sur votre ligne de production : audit, calibration ROI, fine-tuning BOBER sur vos essences.
                            </p>
                            <div className="mt-5 flex flex-wrap gap-3">
                                <DemoDialog
                                    triggerClassName="inline-flex items-center justify-center rounded-full bg-primary hover:bg-[hsl(14_66%_38%)] text-primary-foreground px-5 h-11 text-sm font-medium transition-colors"
                                    triggerLabel="Demander un devis"
                                    testId="quiz-result-demo-button"
                                />
                                <button
                                    type="button"
                                    onClick={onRestart}
                                    data-testid="quiz-restart-button"
                                    className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-card transition-colors"
                                >
                                    <RotateCcw className="h-4 w-4" /> Recommencer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-12">
                <h3 className="font-display font-semibold text-2xl sm:text-3xl tracking-[-0.03em]">Correction détaillée</h3>
                <ol className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {result.details.map((d, i) => (
                        <li key={d.question_id} data-testid="quiz-result-item" className="rounded-3xl border border-black/5 bg-card p-5 sm:p-6">
                            <div className="flex items-center justify-between">
                                <span className="label-caps">Question {String(i + 1).padStart(2, '0')}</span>
                                {d.is_correct ? (
                                    <span className="inline-flex items-center gap-1.5 label-caps !text-[hsl(142_38%_30%)]">
                                        <CheckCircle2 className="h-3.5 w-3.5" /> Correct
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 label-caps !text-primary">
                                        <XCircle className="h-3.5 w-3.5" /> À revoir
                                    </span>
                                )}
                            </div>
                            <p className="mt-3 font-display font-semibold text-[15px] leading-snug text-foreground">{d.question}</p>
                            <div className="mt-4 grid grid-cols-1 gap-2">
                                {!d.is_correct && (
                                    <div className="rounded-xl border border-primary/20 bg-primary/5 px-3 py-2.5 text-sm">
                                        <span className="label-caps !text-primary">Votre réponse · </span>
                                        {d.selected ? `${letter(d.selected)}. ${d.selected_text}` : 'Non répondu'}
                                    </div>
                                )}
                                <div className="rounded-xl border border-[hsl(142_38%_30%/0.2)] bg-[hsl(142_38%_30%/0.06)] px-3 py-2.5 text-sm">
                                    <span className="label-caps !text-[hsl(142_38%_30%)]">Bonne réponse · </span>
                                    {letter(d.correct)}. {d.correct_text}
                                </div>
                            </div>
                            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{d.explanation}</p>
                        </li>
                    ))}
                </ol>
            </div>
        </div>
    );
}
