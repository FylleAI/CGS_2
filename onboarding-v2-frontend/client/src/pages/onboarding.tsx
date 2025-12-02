import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2 } from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import { OnboardingGoal, SessionState } from '@shared/types/onboarding';
const fylleLogo = '/assets/fylle-logotipo-green.png';
import type { QuestionResponse, SnapshotSummary } from '@shared/types/onboarding';

type WizardStep = 
  | 'brand_name' 
  | 'website' 
  | 'email' 
  | 'goal' 
  | 'context' 
  | 'research' 
  | 'quiz' 
  | 'generate' 
  | 'result';

const FORM_STEPS: WizardStep[] = ['brand_name', 'website', 'email', 'goal', 'context'];
const ALL_STEPS: WizardStep[] = ['brand_name', 'website', 'email', 'goal', 'context', 'research', 'quiz', 'generate', 'result'];

const stepConfig: Record<WizardStep, { label: string; optional?: boolean }> = {
  brand_name: { label: 'Azienda' },
  website: { label: 'Sito Web', optional: true },
  email: { label: 'Email' },
  goal: { label: 'Obiettivo' },
  context: { label: 'Contesto', optional: true },
  research: { label: 'Ricerca' },
  quiz: { label: 'Domande' },
  generate: { label: 'Generazione' },
  result: { label: 'Completato' },
};

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export default function OnboardingPage() {
  const [, navigate] = useLocation();
  const [currentStep, setCurrentStep] = useState<WizardStep>('brand_name');
  
  const [brandName, setBrandName] = useState('');
  const [website, setWebsite] = useState('');
  const [email, setEmail] = useState('');
  const [goal, setGoal] = useState<OnboardingGoal>(OnboardingGoal.CONTENT_GENERATION);
  const [additionalContext, setAdditionalContext] = useState('');
  
  const [snapshotSummary, setSnapshotSummary] = useState<SnapshotSummary | null>(null);
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [cardIds, setCardIds] = useState<string[]>([]);
  const [researchProgress, setResearchProgress] = useState(0);
  const [generateProgress, setGenerateProgress] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  
  const [brandNameError, setBrandNameError] = useState('');
  const [emailError, setEmailError] = useState('');

  const {
    sessionId,
    setSessionId,
    clearSession,
    startOnboarding,
    submitAnswers,
    useSessionStatus,
    useSessionDetails,
  } = useOnboarding();

  const [isRestoring, setIsRestoring] = useState(true);

  const { data: sessionDetails } = useSessionDetails(sessionId, {
    enabled: isRestoring && !!sessionId
  });

  const { data: sessionStatus } = useSessionStatus(sessionId, {
    enabled: !isRestoring && (currentStep === 'research' || currentStep === 'generate')
  });

  useEffect(() => {
    if (!sessionId) {
      setIsRestoring(false);
      return;
    }

    if (sessionDetails && isRestoring) {
      const state = sessionDetails.state as SessionState;
      
      if (sessionDetails.snapshot) {
        setSnapshotSummary({
          company_name: sessionDetails.snapshot.company.name,
          industry: sessionDetails.snapshot.company.industry,
          description: sessionDetails.snapshot.company.description,
          target_audience: sessionDetails.snapshot.audience.primary,
          tone: sessionDetails.snapshot.voice.tone,
          questions_count: sessionDetails.snapshot.clarifying_questions.length,
        });
        setQuestions(sessionDetails.snapshot.clarifying_questions);
        if (sessionDetails.snapshot.clarifying_answers) {
          setAnswers(sessionDetails.snapshot.clarifying_answers);
        }
      }

      if (state === SessionState.AWAITING_USER) {
        setCurrentStep('quiz');
        setCurrentQuestionIndex(0);
        setResearchProgress(100);
      } else if (state === SessionState.RESEARCHING || state === SessionState.SYNTHESIZING) {
        setCurrentStep('research');
        setResearchProgress(state === SessionState.RESEARCHING ? 33 : 66);
      } else if (state === SessionState.PAYLOAD_READY || state === SessionState.EXECUTING || state === SessionState.DELIVERING) {
        setCurrentStep('generate');
        setGenerateProgress(state === SessionState.PAYLOAD_READY ? 25 : state === SessionState.EXECUTING ? 50 : 75);
      } else if (state === SessionState.DONE) {
        setCurrentStep('result');
        setGenerateProgress(100);
        if (sessionDetails.cgs_response?.card_ids) {
          setCardIds(sessionDetails.cgs_response.card_ids);
        }
      } else if (state === SessionState.FAILED) {
        clearSession();
        setCurrentStep('brand_name');
      }

      setIsRestoring(false);
    }
  }, [sessionId, sessionDetails, isRestoring, clearSession]);

  useEffect(() => {
    if (isRestoring || !sessionStatus?.state) return;
    
    const state = sessionStatus.state as SessionState;
    
    if (state === SessionState.RESEARCHING) {
      setResearchProgress(33);
    } else if (state === SessionState.SYNTHESIZING) {
      setResearchProgress(66);
    } else if (state === SessionState.AWAITING_USER && currentStep === 'research') {
      setResearchProgress(100);
      setTimeout(() => setCurrentStep('quiz'), 500);
    } else if (state === SessionState.PAYLOAD_READY && currentStep === 'generate') {
      setGenerateProgress(25);
    } else if (state === SessionState.EXECUTING) {
      setGenerateProgress(50);
    } else if (state === SessionState.DELIVERING) {
      setGenerateProgress(75);
    } else if (state === SessionState.DONE && currentStep === 'generate') {
      setGenerateProgress(100);
      setTimeout(() => setCurrentStep('result'), 500);
    } else if (state === SessionState.FAILED) {
      setCurrentStep('brand_name');
    }
  }, [sessionStatus?.state, currentStep, isRestoring]);

  const validateEmail = (value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  };

  const currentIndex = ALL_STEPS.indexOf(currentStep);

  const handleNext = () => {
    const stepIndex = ALL_STEPS.indexOf(currentStep);
    if (stepIndex < FORM_STEPS.length - 1) {
      setCurrentStep(ALL_STEPS[stepIndex + 1]);
    }
  };

  const handleBack = () => {
    const stepIndex = ALL_STEPS.indexOf(currentStep);
    if (stepIndex > 0) {
      setCurrentStep(ALL_STEPS[stepIndex - 1]);
    }
  };

  const handleSkip = () => {
    if (currentStep === 'context') {
      handleStartOnboarding();
    } else {
      handleNext();
    }
  };

  const canProceed = (): boolean => {
    switch (currentStep) {
      case 'brand_name':
        return brandName.trim().length >= 2;
      case 'website':
        return true;
      case 'email':
        return validateEmail(email);
      case 'goal':
        return !!goal;
      case 'context':
        return true;
      default:
        return false;
    }
  };

  const handleStartOnboarding = async () => {
    setCurrentStep('research');
    setResearchProgress(10);
    
    try {
      const result = await startOnboarding.mutateAsync({
        brand_name: brandName,
        website: website || undefined,
        goal,
        user_email: email,
        additional_context: additionalContext || undefined,
      });
      setSessionId(result.session_id);
      setSnapshotSummary(result.snapshot_summary || null);
      setQuestions(result.clarifying_questions);
      
      if (result.state === SessionState.AWAITING_USER) {
        setResearchProgress(100);
        setTimeout(() => {
          setCurrentStep('quiz');
          setCurrentQuestionIndex(0);
        }, 500);
      }
    } catch (error) {
      setCurrentStep('brand_name');
    }
  };

  const handleSubmitAnswers = async () => {
    if (!sessionId) return;

    const requiredQuestions = questions.filter(q => q.required);
    const hasAllAnswers = requiredQuestions.every(q => answers[q.id]);

    if (!hasAllAnswers) {
      return;
    }

    setCurrentStep('generate');
    setGenerateProgress(25);

    try {
      const result = await submitAnswers.mutateAsync({ sessionId, answers });
      setCardIds(result.card_ids || []);
      
      if (result.state === SessionState.PAYLOAD_READY || result.state === SessionState.DONE) {
        setGenerateProgress(100);
        setTimeout(() => setCurrentStep('result'), 500);
      }
    } catch (error) {
      setCurrentStep('quiz');
      setCurrentQuestionIndex(0);
    }
  };

  const handleViewCards = () => {
    navigate('/cards');
  };

  const handleNewSession = () => {
    clearSession();
    setCurrentStep('brand_name');
    setBrandName('');
    setWebsite('');
    setEmail('');
    setGoal(OnboardingGoal.CONTENT_GENERATION);
    setAdditionalContext('');
    setSnapshotSummary(null);
    setQuestions([]);
    setAnswers({});
    setCardIds([]);
    setResearchProgress(0);
    setGenerateProgress(0);
    setCurrentQuestionIndex(0);
  };

  const renderStepCard = (
    title: string,
    subtitle: string,
    content: React.ReactNode,
    showBack: boolean = true,
    showNext: boolean = true,
    nextLabel: string = 'Continua',
    onNext?: () => void,
    isOptional: boolean = false,
    nextDisabled: boolean = false
  ) => {
    return (
      <motion.div
        key={currentStep}
        variants={cardVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ duration: 0.25, ease: 'easeOut' }}
      >
        <Card 
          className="bg-white border-neutral-200 shadow-sm rounded-3xl"
          data-testid={`card-${currentStep}`}
        >
          <CardContent className="pt-10 pb-8 px-8">
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-neutral-900 mb-1">
                {title}
              </h2>
              <p className="text-neutral-500 text-sm">{subtitle}</p>
            </div>

            <div className="mb-8">
              {content}
            </div>

            <div className="flex gap-3">
              {showBack && currentIndex > 0 && (
                <Button
                  variant="ghost"
                  className="flex-1 h-11 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 rounded-xl"
                  onClick={handleBack}
                  data-testid="button-back"
                >
                  Indietro
                </Button>
              )}
              {isOptional && (
                <Button
                  variant="ghost"
                  className="flex-1 h-11 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-xl"
                  onClick={handleSkip}
                  data-testid="button-skip"
                >
                  Salta
                </Button>
              )}
              {showNext && (
                <Button
                  className="flex-1 h-11 bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl font-medium"
                  onClick={onNext || handleNext}
                  disabled={nextDisabled || !canProceed()}
                  data-testid="button-next"
                >
                  {nextLabel}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderBrandNameStep = () => renderStepCard(
    "Come si chiama la tua azienda?",
    "Inserisci il nome del tuo brand",
    <div className="space-y-2">
      <Input
        value={brandName}
        onChange={(e) => {
          setBrandName(e.target.value);
          if (e.target.value.length >= 2) setBrandNameError('');
        }}
        placeholder="Es. Fylle AI"
        className="h-12 text-base bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl"
        data-testid="input-brand-name"
        autoFocus
      />
      {brandName.length > 0 && brandName.length < 2 && (
        <p className="text-sm text-amber-600">Il nome deve avere almeno 2 caratteri</p>
      )}
    </div>,
    false
  );

  const renderWebsiteStep = () => renderStepCard(
    "Qual è il sito web?",
    "Opzionale - ci aiuta a capire meglio il tuo brand",
    <Input
      value={website}
      onChange={(e) => setWebsite(e.target.value)}
      placeholder="https://esempio.com"
      type="url"
      className="h-12 text-base bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl"
      data-testid="input-website"
      autoFocus
    />,
    true,
    true,
    'Continua',
    undefined,
    true
  );

  const renderEmailStep = () => renderStepCard(
    "Qual è la tua email?",
    "Ti invieremo aggiornamenti",
    <div className="space-y-2">
      <Input
        value={email}
        onChange={(e) => {
          setEmail(e.target.value);
          if (validateEmail(e.target.value)) setEmailError('');
        }}
        placeholder="tuonome@azienda.com"
        type="email"
        className="h-12 text-base bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl"
        data-testid="input-email"
        autoFocus
      />
      {email.length > 0 && !validateEmail(email) && (
        <p className="text-sm text-amber-600">Inserisci un indirizzo email valido</p>
      )}
    </div>
  );

  const renderGoalStep = () => renderStepCard(
    "Qual è il tuo obiettivo?",
    "Scegli cosa vuoi ottenere",
    <RadioGroup
      value={goal}
      onValueChange={(value) => setGoal(value as OnboardingGoal)}
      className="space-y-3"
      data-testid="input-goal"
    >
      <div 
        className={`flex items-center space-x-4 border rounded-xl p-4 cursor-pointer transition-all ${
          goal === OnboardingGoal.CONTENT_GENERATION 
            ? 'border-neutral-900 bg-neutral-50' 
            : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
        }`}
        onClick={() => setGoal(OnboardingGoal.CONTENT_GENERATION)}
      >
        <RadioGroupItem 
          value={OnboardingGoal.CONTENT_GENERATION} 
          id="content" 
          className="border-neutral-300 text-neutral-900"
        />
        <Label htmlFor="content" className="cursor-pointer flex-1">
          <div className="font-medium text-neutral-900">
            Generazione Contenuti
          </div>
          <div className="text-sm text-neutral-500 mt-0.5">
            Blog, social media, marketing
          </div>
        </Label>
      </div>
      <div 
        className={`flex items-center space-x-4 border rounded-xl p-4 cursor-pointer transition-all ${
          goal === OnboardingGoal.COMPANY_SNAPSHOT 
            ? 'border-neutral-900 bg-neutral-50' 
            : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
        }`}
        onClick={() => setGoal(OnboardingGoal.COMPANY_SNAPSHOT)}
      >
        <RadioGroupItem 
          value={OnboardingGoal.COMPANY_SNAPSHOT} 
          id="snapshot"
          className="border-neutral-300 text-neutral-900"
        />
        <Label htmlFor="snapshot" className="cursor-pointer flex-1">
          <div className="font-medium text-neutral-900">
            Company Snapshot
          </div>
          <div className="text-sm text-neutral-500 mt-0.5">
            Panoramica del profilo aziendale
          </div>
        </Label>
      </div>
    </RadioGroup>
  );

  const renderContextStep = () => renderStepCard(
    "Contesto aggiuntivo",
    "Opzionale - personalizza i risultati",
    <Textarea
      value={additionalContext}
      onChange={(e) => setAdditionalContext(e.target.value)}
      placeholder="Es. Focus su B2B, tono professionale, target PMI..."
      rows={4}
      className="bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 resize-none text-base rounded-xl"
      data-testid="input-context"
      autoFocus
    />,
    true,
    true,
    'Avvia Analisi',
    handleStartOnboarding,
    true,
    startOnboarding.isPending
  );

  const renderResearchCard = () => (
    <motion.div
      key="research"
      variants={cardVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl" data-testid="card-research">
        <CardContent className="pt-10 pb-8 px-8">
          <div className="text-center">
            <div className="mb-6">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-neutral-400" />
            </div>
            <h2 className="text-xl font-semibold text-neutral-900 mb-1">
              Analisi in corso
            </h2>
            <p className="text-neutral-500 text-sm mb-8">
              Stiamo analizzando {brandName}
            </p>
            
            <div className="space-y-3">
              <div className="relative h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                <motion.div
                  className="absolute h-full rounded-full bg-neutral-900"
                  initial={{ width: 0 }}
                  animate={{ width: `${researchProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <p className="text-xs text-neutral-400">
                {researchProgress < 30 && "Raccolta informazioni..."}
                {researchProgress >= 30 && researchProgress < 60 && "Analisi del brand..."}
                {researchProgress >= 60 && researchProgress < 90 && "Sintesi dei dati..."}
                {researchProgress >= 90 && "Preparazione domande..."}
              </p>
            </div>

            {snapshotSummary && (
              <div className="text-left bg-neutral-50 rounded-xl p-4 border border-neutral-100 mt-6">
                <p className="text-xs text-neutral-400 mb-1">Trovato:</p>
                <p className="text-neutral-900 font-medium">{snapshotSummary.company_name}</p>
                <p className="text-sm text-neutral-500">{snapshotSummary.industry}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderQuestionCard = () => {
    if (questions.length === 0) return null;
    
    const question = questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const hasAnswer = !!answers[question.id];
    const canContinue = !question.required || hasAnswer;

    const handleQuestionNext = () => {
      if (isLastQuestion) {
        handleSubmitAnswers();
      } else {
        setCurrentQuestionIndex(prev => prev + 1);
      }
    };

    const handleQuestionBack = () => {
      if (currentQuestionIndex > 0) {
        setCurrentQuestionIndex(prev => prev - 1);
      } else {
        setCurrentStep('research');
      }
    };

    return (
      <motion.div
        key={`quiz-${currentQuestionIndex}`}
        variants={cardVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ duration: 0.25, ease: 'easeOut' }}
      >
        <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl" data-testid={`card-question-${currentQuestionIndex}`}>
          <CardContent className="pt-10 pb-8 px-8">
            <div className="mb-8">
              <p className="text-neutral-400 text-xs mb-2">
                Domanda {currentQuestionIndex + 1} di {questions.length}
              </p>
              <h2 className="text-xl font-semibold text-neutral-900 mb-1">
                {question.question}
              </h2>
              {!question.required && (
                <p className="text-neutral-400 text-sm">Opzionale</p>
              )}
            </div>

            <div className="mb-8">
              {question.expected_response_type === 'select' && question.options ? (
                <RadioGroup
                  value={answers[question.id] || ''}
                  onValueChange={(value) => setAnswers(prev => ({ ...prev, [question.id]: value }))}
                  className="grid gap-2"
                >
                  {question.options.map((option) => (
                    <div
                      key={option}
                      className={`flex items-center space-x-3 border rounded-xl p-3 cursor-pointer transition-all ${
                        answers[question.id] === option
                          ? 'border-neutral-900 bg-neutral-50'
                          : 'border-neutral-200 hover:border-neutral-300'
                      }`}
                      onClick={() => setAnswers(prev => ({ ...prev, [question.id]: option }))}
                    >
                      <RadioGroupItem value={option} className="border-neutral-300 text-neutral-900" />
                      <span className="text-neutral-700 text-sm">{option}</span>
                    </div>
                  ))}
                </RadioGroup>
              ) : (
                <Input
                  value={answers[question.id] || ''}
                  onChange={(e) => setAnswers(prev => ({ ...prev, [question.id]: e.target.value }))}
                  placeholder="La tua risposta..."
                  className="h-12 text-base bg-neutral-50 border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-300 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-xl"
                  autoFocus
                />
              )}
            </div>

            <div className="flex gap-3">
              <Button
                variant="ghost"
                className="flex-1 h-11 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 rounded-xl"
                onClick={handleQuestionBack}
                data-testid="button-question-back"
              >
                Indietro
              </Button>
              
              {!question.required && !hasAnswer && (
                <Button
                  variant="ghost"
                  className="flex-1 h-11 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-xl"
                  onClick={handleQuestionNext}
                  data-testid="button-question-skip"
                >
                  Salta
                </Button>
              )}
              
              <Button
                className="flex-1 h-11 bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl font-medium"
                onClick={handleQuestionNext}
                disabled={!canContinue || (isLastQuestion && submitAnswers.isPending)}
                data-testid="button-question-next"
              >
                {submitAnswers.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Invio...
                  </>
                ) : isLastQuestion ? (
                  'Genera'
                ) : (
                  'Continua'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderGenerateCard = () => (
    <motion.div
      key="generate"
      variants={cardVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl" data-testid="card-generate">
        <CardContent className="pt-10 pb-8 px-8">
          <div className="text-center">
            <div className="mb-6">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-neutral-400" />
            </div>
            <h2 className="text-xl font-semibold text-neutral-900 mb-1">
              Generazione in corso
            </h2>
            <p className="text-neutral-500 text-sm mb-8">
              Stiamo creando i tuoi contenuti
            </p>
            
            <div className="space-y-3">
              <div className="relative h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                <motion.div
                  className="absolute h-full rounded-full bg-neutral-900"
                  initial={{ width: 0 }}
                  animate={{ width: `${generateProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <p className="text-xs text-neutral-400">
                {generateProgress < 30 && "Preparazione..."}
                {generateProgress >= 30 && generateProgress < 60 && "Generazione contenuti..."}
                {generateProgress >= 60 && generateProgress < 90 && "Ottimizzazione..."}
                {generateProgress >= 90 && "Finalizzazione..."}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderResultCard = () => (
    <motion.div
      key="result"
      variants={cardVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl" data-testid="card-result">
        <CardContent className="pt-10 pb-8 px-8">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-neutral-900 mb-1">
              Completato
            </h2>
            <p className="text-neutral-500 text-sm">
              Abbiamo creato {cardIds.length} card per te
            </p>
          </div>

          {snapshotSummary && (
            <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-100 mb-6">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-neutral-500">Azienda</span>
                  <span className="text-neutral-900 font-medium">{snapshotSummary.company_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-500">Settore</span>
                  <span className="text-neutral-900">{snapshotSummary.industry}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-500">Card create</span>
                  <span className="text-neutral-900 font-medium">{cardIds.length}</span>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-3">
            <Button
              className="w-full h-11 bg-neutral-900 text-white hover:bg-neutral-800 rounded-xl font-medium"
              onClick={handleViewCards}
              data-testid="button-view-cards"
            >
              Visualizza Card
            </Button>
            <Button
              variant="ghost"
              className="w-full h-11 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 rounded-xl"
              onClick={handleNewSession}
              data-testid="button-new-session"
            >
              Nuova Sessione
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (isRestoring && sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-neutral-400" />
          <p className="text-neutral-500 text-sm">Ripristino sessione...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-neutral-100">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img 
            src={fylleLogo} 
            alt="Fylle" 
            className="h-11 mx-auto"
            data-testid="img-fylle-logo"
          />
        </div>

        <AnimatePresence mode="wait">
          {currentStep === 'brand_name' && renderBrandNameStep()}
          {currentStep === 'website' && renderWebsiteStep()}
          {currentStep === 'email' && renderEmailStep()}
          {currentStep === 'goal' && renderGoalStep()}
          {currentStep === 'context' && renderContextStep()}
          {currentStep === 'research' && renderResearchCard()}
          {currentStep === 'quiz' && renderQuestionCard()}
          {currentStep === 'generate' && renderGenerateCard()}
          {currentStep === 'result' && renderResultCard()}
        </AnimatePresence>
      </div>
    </div>
  );
}
