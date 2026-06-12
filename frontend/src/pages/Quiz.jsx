import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, ArrowRight, CheckCircle2, XCircle, Lock, RotateCcw, Award, Image as ImageIcon } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import DemoDialog from '@/components/DemoDialog';
import PillButton from '@/components/PillButton';
import { fetchQuiz, submitQuiz } from '@/lib/api';

const STAGE = {
    INTRO: 'intro',
    QUESTION: 'question',
    EMAIL: 'email',
    RESULT: 'result',
};

function ProductTypesPanel({ types }) {
    return (
        <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-7">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="label-caps">01</span>
                    <span className="font-heading text-lg sm:text-xl tracking-tight">Type de produit</span>
                </div>
                <span className="label-caps">4 familles normatives</span>
            </div>
            <div className="mt-5 grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {types.map((t) => (
                    <div key={t.letter} className="rounded-xl border border-black/5 bg-[hsl(var(--background))] p-4 sm:p-5">
                        <div className="font-heading italic text-[hsl(var(--primary))] text-4xl sm:text-5xl leading-none">{t.letter}</div>
                        <div className="mt-3 font-heading text-base sm:text-lg leading-tight">{t.name}</div>
                        <p className="mt-2 text-xs leading-[1.6] text-[hsl(var(--muted-foreground))]">{t.desc}</p>
                        <div className="mt-3 text-[10px] tracking-[0.14em] uppercase text-[hsl(var(--muted-foreground))]">{t.specs}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function AnswerGrid({ groups, selectedKey, onSelect }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
            {groups.map((g) => (
                <fieldset key={g.label} className="rounded-2xl border border-black/5 bg-[hsl(var(--background))] p-4 sm:p-5">
                    <legend className="label-caps !tracking-[0.18em] px-2 text-[hsl(var(--primary))]">{g.label}</legend>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                        {g.options.map((opt) => {
                            const active = selectedKey === opt.key;
                            return (
                                <button
                                    key={opt.key}
                                    type="button"
                                    data-testid="quiz-answer-option"
                                    data-key={opt.key}
                                    onClick={() => onSelect(opt.key)}
                                    className={`group rounded-xl border px-3 py-3 text-left transition-colors duration-150 ease-out ${
                                        active
                                            ? 'border-[hsl(var(--primary))] bg-[hsla(14,64%,42%,0.08)]'
                                            : 'border-black/10 hover:border-black/30 bg-[hsl(var(--card))]'
                                    }`}
                                >
                                    <div className={`font-heading italic text-base leading-none ${active ? 'text-[hsl(var(--primary))]' : ''}`}>
                                        {opt.code}
                                    </div>
                                    <div className="mt-1.5 text-[10px] tracking-[0.08em] uppercase text-[hsl(var(--muted-foreground))] leading-tight">
                                        {opt.hint}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </fieldset>
            ))}
        </div>
    );
}

export default function Quiz() {
    const [stage, setStage] = useState(STAGE.INTRO);
    const [data, setData] = useState({ questions: [], product_types: [], answer_groups: [], total: 0 });
    const [loading, setLoading] = useState(true);
    const [idx, setIdx] = useState(0);
    const [answers, setAnswers] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [contact, setContact] = useState({ nom: '', email: '', entreprise: '' });

    useEffect(() => {
        let mounted = true;
        fetchQuiz()
            .then((d) => { if (mounted) setData(d); })
            .catch(() => toast.error('Impossible de charger le quiz.'))
            .finally(() => mounted && setLoading(false));
        return () => { mounted = false; };
    }, []);

    const total = data.questions.length;
    const current = data.questions[idx];
    const answeredCount = Object.keys(answers).length;
    const progressPct = total ? Math.round(((idx + (current && answers[current.id] ? 1 : 0)) / total) * 100) : 0;

    const setAnswer = (qid, value) => setAnswers((s) => ({ ...s, [qid]: value }));

    const goNext = () => {
        if (!current) return;
        if (!answers[current.id]) {
            toast.error('Sélectionnez une classe avant de continuer.');
            return;
        }
        if (idx + 1 < total) {
            setIdx(idx + 1);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            setStage(STAGE.EMAIL);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };
    const goPrev = () => {
        if (idx > 0) setIdx(idx - 1);
        else setStage(STAGE.INTRO);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const send = async (withContact = true) => {
        try {
            setSubmitting(true);
            const payload = {
                answers: Object.entries(answers).map(([question_id, selected]) => ({ question_id, selected })),
                ...(withContact ? contact : {}),
            };
            const res = await submitQuiz(payload);
            setResult(res);
            setStage(STAGE.RESULT);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (e) {
            toast.error("Échec de l'envoi du quiz. Réessayez.");
        } finally {
            setSubmitting(false);
        }
    };

    const restart = () => {
        setIdx(0);
        setAnswers({});
        setResult(null);
        setContact({ nom: '', email: '', entreprise: '' });
        setStage(STAGE.INTRO);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    if (loading) {
        return (
            <section className="max-w-5xl mx-auto px-4 py-20">
                <div className="animate-pulse h-8 w-48 bg-[hsl(var(--muted))] rounded" />
                <div className="mt-6 h-64 bg-[hsl(var(--muted))] rounded-2xl" />
            </section>
        );
    }

    return (
        <section data-testid="quiz-page" className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
            {/* Top bar */}
            <div className="flex items-center justify-between gap-3">
                <span data-testid="quiz-sample-badge" className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--card))] border border-black/5 px-3 py-1.5 text-[11px] tracking-[0.18em] uppercase">
                    <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--primary))]" />
                    Échantillon · Chêne · EN 975-1
                </span>
                <span className="hidden sm:inline-flex items-center gap-2 text-[11px] tracking-[0.18em] uppercase text-[hsl(var(--muted-foreground))]">
                    <Lock className="h-3.5 w-3.5" /> Essence verrouillée
                </span>
            </div>

            {/* Progress (only during questions) */}
            {stage === STAGE.QUESTION && (
                <div data-testid="quiz-progress" className="mt-6 flex items-center gap-4">
                    <span className="font-heading text-sm sm:text-base tracking-tight whitespace-nowrap">
                        <span className="text-[hsl(var(--primary))] italic">{idx + 1}</span>
                        <span className="text-[hsl(var(--muted-foreground))]">&nbsp;/ {total}</span>
                    </span>
                    <Progress value={progressPct} className="h-1.5 bg-[hsl(var(--muted))] [&>div]:bg-[hsl(var(--primary))]" />
                </div>
            )}

            {/* INTRO */}
            {stage === STAGE.INTRO && (
                <div data-animate="fade-up" className="mt-10">
                    <div className="label-caps">Quiz EN 975-1 · Classement visuel</div>
                    <h1 className="mt-3 font-heading text-4xl sm:text-5xl lg:text-6xl leading-[1.05] tracking-[-0.02em]">
                        Classez {total} planches selon la <span className="brick-italic">norme officielle.</span>
                    </h1>
                    <p className="mt-5 max-w-2xl text-[hsl(var(--muted-foreground))] leading-[1.7]">
                        Chaque image vous montre un échantillon de chêne. Choisissez la classe EN 975-1 qui lui correspond parmi les options Plots, Plateaux sélectionnés, Frises et avivés ou Pièces équarries. Durée estimée : 5 minutes.
                    </p>

                    <div className="mt-8">
                        <ProductTypesPanel types={data.product_types} />
                    </div>

                    <div className="mt-8 flex flex-wrap gap-3">
                        <PillButton onClick={() => setStage(STAGE.QUESTION)} size="lg" testId="quiz-start-button">
                            Commencer le quiz
                        </PillButton>
                        <PillButton to="/" variant="outline" size="lg" icon={false} testId="quiz-back-home">
                            Retour à l'accueil
                        </PillButton>
                    </div>
                </div>
            )}

            {/* QUESTION */}
            {stage === STAGE.QUESTION && current && (
                <div
                    key={current.id}
                    data-testid="quiz-question-card"
                    data-animate="fade-up"
                    className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8"
                >
                    {/* Image card */}
                    <div className="lg:col-span-5">
                        <div className="sticky top-24 rounded-2xl overflow-hidden border border-black/5 bg-[hsl(var(--card))] shadow-[0_18px_44px_rgba(17,17,17,0.08)]">
                            <div className="flex items-center justify-between px-4 py-3 border-b border-black/5">
                                <span className="label-caps">Échantillon Q{String(idx + 1).padStart(2, '0')}</span>
                                <span className="inline-flex items-center gap-1.5 text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--primary))]">
                                    <ImageIcon className="h-3 w-3" /> {current.product_type}
                                </span>
                            </div>
                            <div className="bg-[hsl(38_45%_92%)] flex items-center justify-center p-2">
                                <img
                                    src={current.image_url}
                                    alt={`Échantillon chêne ${idx + 1}`}
                                    data-testid="quiz-image"
                                    className="max-h-72 w-full object-contain"
                                    loading="eager"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Answer panel */}
                    <div className="lg:col-span-7">
                        <div className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-5 sm:p-7">
                            <div className="flex items-center justify-between">
                                <span className="label-caps text-[hsl(var(--primary))]">Choisissez la classe</span>
                                <span className="label-caps">EN 975-1</span>
                            </div>
                            <h2 className="mt-3 font-heading text-2xl sm:text-3xl leading-[1.15] tracking-tight">
                                Quelle classification pour cet <span className="brick-italic">échantillon</span> ?
                            </h2>

                            <div className="mt-5">
                                <AnswerGrid
                                    groups={data.answer_groups}
                                    selectedKey={answers[current.id]}
                                    onSelect={(k) => setAnswer(current.id, k)}
                                />
                            </div>

                            <div className="mt-7 flex flex-wrap items-center justify-between gap-3">
                                <button
                                    type="button"
                                    data-testid="quiz-prev-button"
                                    onClick={goPrev}
                                    className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-[hsl(var(--background))] transition-colors"
                                >
                                    <ArrowLeft className="h-4 w-4" /> Précédent
                                </button>
                                <div className="flex items-center gap-3">
                                    <span className="text-xs text-[hsl(var(--muted-foreground))]">{answeredCount}/{total} classées</span>
                                    <button
                                        type="button"
                                        data-testid="quiz-next-button"
                                        onClick={goNext}
                                        className="inline-flex items-center justify-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors"
                                    >
                                        {idx + 1 === total ? 'Terminer' : 'Suivant'}
                                        <ArrowRight className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* EMAIL */}
            {stage === STAGE.EMAIL && (
                <div data-testid="quiz-email-card" data-animate="fade-up" className="mt-8 rounded-2xl border border-black/5 bg-[hsl(var(--card))] p-6 sm:p-8 lg:p-10">
                    <div className="label-caps">Avant le score</div>
                    <h2 className="mt-3 font-heading text-3xl sm:text-4xl tracking-tight">
                        Souhaitez-vous recevoir un <span className="brick-italic">débrief</span> par email ?
                    </h2>
                    <p className="mt-3 text-sm text-[hsl(var(--muted-foreground))] max-w-2xl">
                        Optionnel — vous pouvez aussi voir vos résultats sans laisser de coordonnées.
                    </p>
                    <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div className="flex flex-col gap-1.5">
                            <Label htmlFor="q-nom" className="label-caps">Nom</Label>
                            <Input id="q-nom" data-testid="quiz-email-input-nom" value={contact.nom} onChange={(e) => setContact((s) => ({ ...s, nom: e.target.value }))} className="bg-[hsl(var(--background))]" />
                        </div>
                        <div className="flex flex-col gap-1.5">
                            <Label htmlFor="q-email" className="label-caps">Email</Label>
                            <Input id="q-email" type="email" data-testid="quiz-email-input-email" value={contact.email} onChange={(e) => setContact((s) => ({ ...s, email: e.target.value }))} className="bg-[hsl(var(--background))]" />
                        </div>
                        <div className="flex flex-col gap-1.5">
                            <Label htmlFor="q-ent" className="label-caps">Entreprise</Label>
                            <Input id="q-ent" data-testid="quiz-email-input-entreprise" value={contact.entreprise} onChange={(e) => setContact((s) => ({ ...s, entreprise: e.target.value }))} className="bg-[hsl(var(--background))]" />
                        </div>
                    </div>
                    <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                        <button type="button" onClick={() => setStage(STAGE.QUESTION)} className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-[hsl(var(--background))] transition-colors">
                            <ArrowLeft className="h-4 w-4" /> Revenir aux questions
                        </button>
                        <div className="flex flex-wrap gap-3">
                            <button type="button" data-testid="quiz-skip-email-button" onClick={() => send(false)} disabled={submitting} className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm font-medium hover:bg-[hsl(var(--background))] transition-colors">
                                Voir mes résultats
                            </button>
                            <button type="button" data-testid="quiz-submit-with-email-button" onClick={() => send(true)} disabled={submitting} className="inline-flex items-center justify-center gap-2 rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] disabled:opacity-60 text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors">
                                {submitting ? 'Calcul…' : 'Recevoir le débrief'}
                                <ArrowRight className="h-4 w-4" />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* RESULT */}
            {stage === STAGE.RESULT && result && (
                <ResultPanel result={result} onRestart={restart} />
            )}
        </section>
    );
}

function ResultPanel({ result, onRestart }) {
    const tier = useMemo(() => {
        const p = result.percentage;
        if (p >= 85) return { label: 'Expert EN 975-1', color: 'text-[hsl(var(--primary))]' };
        if (p >= 65) return { label: 'Bonne maîtrise', color: 'text-[hsl(var(--primary))]' };
        if (p >= 40) return { label: 'En progression', color: 'text-[hsl(35_45%_30%)]' };
        return { label: 'Découverte', color: 'text-[hsl(35_45%_30%)]' };
    }, [result.percentage]);

    return (
        <div data-testid="quiz-result" data-animate="fade-up" className="mt-8">
            <div className="rounded-3xl overflow-hidden border border-black/5 bg-[hsl(var(--card))] shadow-[0_24px_60px_rgba(17,17,17,0.08)]">
                <div className="p-6 sm:p-10 lg:p-14 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                    <div className="lg:col-span-7">
                        <div className="label-caps">Résultat</div>
                        <h2 className="mt-3 font-heading text-4xl sm:text-5xl lg:text-6xl leading-[1.04] tracking-[-0.02em]">
                            <span data-testid="quiz-score-value" className="brick-italic">{result.score}</span>
                            <span className="text-[hsl(var(--muted-foreground))]"> / {result.total}</span>
                        </h2>
                        <div className={`mt-3 font-heading text-2xl ${tier.color}`}>
                            <Award className="inline-block h-5 w-5 mr-2 -mt-1" />
                            {tier.label}
                        </div>
                        <p className="mt-4 text-[hsl(var(--muted-foreground))] leading-[1.7] max-w-xl">
                            Vous avez correctement classé <span className="text-[hsl(var(--foreground))] font-medium">{result.percentage}%</span> des échantillons selon la norme EN 975-1.
                        </p>
                    </div>
                    <div className="lg:col-span-5">
                        <div className="rounded-2xl border border-black/5 bg-[hsl(var(--background))] p-6">
                            <div className="label-caps">Pour aller plus loin</div>
                            <p className="mt-3 text-sm leading-[1.65]">
                                Voyez ce que BEAVER fait sur votre ligne de production : audit, calibration ROI, fine-tuning BOBER sur vos essences.
                            </p>
                            <div className="mt-5 flex flex-wrap gap-3">
                                <DemoDialog
                                    triggerClassName="inline-flex items-center justify-center rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(14_66%_38%)] text-[hsl(var(--primary-foreground))] px-5 h-11 text-sm font-medium transition-colors"
                                    triggerLabel="Demander un devis"
                                    testId="quiz-result-demo-button"
                                />
                                <button type="button" onClick={onRestart} data-testid="quiz-restart-button" className="inline-flex items-center justify-center gap-2 rounded-full border border-black/15 px-5 h-11 text-sm hover:bg-[hsl(var(--card))] transition-colors">
                                    <RotateCcw className="h-4 w-4" /> Recommencer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-10">
                <h3 className="font-heading text-2xl sm:text-3xl tracking-tight">Débrief par échantillon</h3>
                <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.details.map((d, i) => (
                        <div
                            key={d.question_id}
                            data-testid="quiz-result-item"
                            className="rounded-2xl border border-black/5 bg-[hsl(var(--card))] overflow-hidden"
                        >
                            <div className="flex items-center justify-between px-4 py-3 border-b border-black/5">
                                <span className="label-caps">Échantillon {String(i + 1).padStart(2, '0')}</span>
                                {d.is_correct ? (
                                    <span className="inline-flex items-center gap-1.5 text-[10px] tracking-[0.16em] uppercase text-[hsl(142_38%_30%)]">
                                        <CheckCircle2 className="h-3.5 w-3.5" /> Correct
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1.5 text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--primary))]">
                                        <XCircle className="h-3.5 w-3.5" /> À revoir
                                    </span>
                                )}
                            </div>
                            {d.image_url && (
                                <div className="aspect-[4/3] bg-[hsl(38_45%_92%)]">
                                    <img src={d.image_url} alt="" className="h-full w-full object-cover" />
                                </div>
                            )}
                            <div className="p-4 sm:p-5">
                                {d.product_type && (
                                    <div className="text-[10px] tracking-[0.16em] uppercase text-[hsl(var(--muted-foreground))]">{d.product_type}</div>
                                )}
                                <div className="mt-3 grid grid-cols-2 gap-2">
                                    <div className="rounded-lg border border-black/5 bg-[hsl(var(--background))] p-2.5">
                                        <div className="label-caps">Votre choix</div>
                                        <div className={`mt-1 font-heading italic text-base ${d.is_correct ? '' : 'text-[hsl(var(--primary))]'}`}>
                                            {d.selected_code || 'Non répondu'}
                                        </div>
                                    </div>
                                    <div className="rounded-lg border border-black/5 bg-[hsl(var(--background))] p-2.5">
                                        <div className="label-caps text-[hsl(var(--primary))]">Bonne réponse</div>
                                        <div className="mt-1 font-heading italic text-base">{d.correct_code}</div>
                                    </div>
                                </div>
                                <p className="mt-3 text-xs leading-[1.6] text-[hsl(var(--muted-foreground))]">{d.explanation}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
