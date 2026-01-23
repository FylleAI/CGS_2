/**
 * Onboarding Page for Fylle Onboarding v3
 * Clean implementation without hardcoding
 */

import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import { OnboardingGoal, type QuestionResponse } from '@shared/types/onboarding';

const fylleLogo = '/assets/fylle-logotipo-green.png';

type WizardStep = 'brand_name' | 'website' | 'email' | 'goal' | 'context' | 'research' | 'quiz' | 'generate' | 'result';

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
  const [goal, setGoal] = useState<OnboardingGoal>(OnboardingGoal.COMPANY_SNAPSHOT);
  const [additionalContext, setAdditionalContext] = useState('');
  
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  
  const { userId, sessionId, startOnboarding, submitAnswers } = useOnboarding();

  const handleStartOnboarding = async () => {
    setCurrentStep('research');
    
    try {
      const response = await startOnboarding.mutateAsync({
        brand_name: brandName,
        website: website || undefined,
        goal,
        user_email: email,
        additional_context: additionalContext || undefined,
      });
      
      setQuestions(response.clarifying_questions);
      setCurrentStep('quiz');
    } catch (error) {
      setCurrentStep('context');
    }
  };

  const handleAnswerChange = (questionId: string, value: any) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitAnswers = async () => {
    if (!sessionId) return;
    
    setCurrentStep('generate');
    
    try {
      const response = await submitAnswers.mutateAsync({
        sessionId,
        answers,
      });
      
      setCurrentStep('result');
      
      // Redirect to cards page after delay
      setTimeout(() => {
        navigate(`/cards?user_id=${userId}`);
      }, 2000);
    } catch (error) {
      setCurrentStep('quiz');
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  const renderBrandNameStep = () => (
    <motion.div key="brand_name" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Come si chiama la tua azienda?</h2>
          <p className="text-neutral-500 mb-6">Inserisci il nome del brand o dell'azienda</p>
          <Input
            value={brandName}
            onChange={(e) => setBrandName(e.target.value)}
            placeholder="Es. Acme Inc."
            className="bg-neutral-50 border-neutral-200 h-12 rounded-xl"
          />
          <Button
            onClick={() => setCurrentStep('website')}
            disabled={!brandName.trim()}
            className="w-full mt-6 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
          >
            Continua
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderWebsiteStep = () => (
    <motion.div key="website" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Qual è il sito web?</h2>
          <p className="text-neutral-500 mb-6">Opzionale - ci aiuta a capire meglio il tuo brand</p>
          <Input
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="https://www.esempio.com"
            className="bg-neutral-50 border-neutral-200 h-12 rounded-xl"
          />
          <div className="flex gap-3 mt-6">
            <Button variant="outline" onClick={() => setCurrentStep('brand_name')} className="flex-1 h-12 rounded-xl">
              Indietro
            </Button>
            <Button onClick={() => setCurrentStep('email')} className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl">
              Continua
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderEmailStep = () => (
    <motion.div key="email" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Qual è la tua email?</h2>
          <p className="text-neutral-500 mb-6">Useremo questa email per creare il tuo account</p>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@esempio.com"
            className="bg-neutral-50 border-neutral-200 h-12 rounded-xl"
          />
          <div className="flex gap-3 mt-6">
            <Button variant="outline" onClick={() => setCurrentStep('website')} className="flex-1 h-12 rounded-xl">
              Indietro
            </Button>
            <Button
              onClick={() => setCurrentStep('goal')}
              disabled={!email.trim() || !email.includes('@')}
              className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
            >
              Continua
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderGoalStep = () => (
    <motion.div key="goal" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Qual è il tuo obiettivo?</h2>
          <p className="text-neutral-500 mb-6">Seleziona cosa vuoi ottenere</p>
          <div className="space-y-3">
            <button
              onClick={() => setGoal(OnboardingGoal.COMPANY_SNAPSHOT)}
              className={`w-full p-4 rounded-xl text-left transition-colors ${
                goal === OnboardingGoal.COMPANY_SNAPSHOT
                  ? 'bg-neutral-900 text-white'
                  : 'bg-neutral-50 hover:bg-neutral-100'
              }`}
            >
              <div className="font-medium">Company Snapshot</div>
              <div className={`text-sm ${goal === OnboardingGoal.COMPANY_SNAPSHOT ? 'text-neutral-300' : 'text-neutral-500'}`}>
                Genera un profilo completo della tua azienda
              </div>
            </button>
            <button
              onClick={() => setGoal(OnboardingGoal.CONTENT_GENERATION)}
              className={`w-full p-4 rounded-xl text-left transition-colors ${
                goal === OnboardingGoal.CONTENT_GENERATION
                  ? 'bg-neutral-900 text-white'
                  : 'bg-neutral-50 hover:bg-neutral-100'
              }`}
            >
              <div className="font-medium">Content Generation</div>
              <div className={`text-sm ${goal === OnboardingGoal.CONTENT_GENERATION ? 'text-neutral-300' : 'text-neutral-500'}`}>
                Prepara il contesto per generare contenuti
              </div>
            </button>
          </div>
          <div className="flex gap-3 mt-6">
            <Button variant="outline" onClick={() => setCurrentStep('email')} className="flex-1 h-12 rounded-xl">
              Indietro
            </Button>
            <Button onClick={() => setCurrentStep('context')} className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl">
              Continua
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderContextStep = () => (
    <motion.div key="context" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Contesto aggiuntivo</h2>
          <p className="text-neutral-500 mb-6">Opzionale - aggiungi dettagli utili</p>
          <textarea
            value={additionalContext}
            onChange={(e) => setAdditionalContext(e.target.value)}
            placeholder="Es. Siamo un'azienda B2B nel settore fintech..."
            className="w-full h-32 p-4 bg-neutral-50 border border-neutral-200 rounded-xl resize-none"
          />
          <div className="flex gap-3 mt-6">
            <Button variant="outline" onClick={() => setCurrentStep('goal')} className="flex-1 h-12 rounded-xl">
              Indietro
            </Button>
            <Button
              onClick={handleStartOnboarding}
              disabled={startOnboarding.isPending}
              className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
            >
              {startOnboarding.isPending ? <Loader2 className="animate-spin" /> : 'Avvia Onboarding'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderResearchStep = () => (
    <motion.div key="research" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8 text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-neutral-400" />
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Ricerca in corso...</h2>
          <p className="text-neutral-500">Stiamo analizzando {brandName}</p>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderQuizStep = () => (
    <motion.div key="quiz" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8">
          <div className="text-sm text-neutral-400 mb-2">
            Domanda {currentQuestionIndex + 1} di {questions.length}
          </div>
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">{currentQuestion?.question}</h2>
          
          {currentQuestion?.options ? (
            <div className="space-y-2">
              {currentQuestion.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAnswerChange(currentQuestion.id, option)}
                  className={`w-full p-4 rounded-xl text-left transition-colors ${
                    answers[currentQuestion.id] === option
                      ? 'bg-neutral-900 text-white'
                      : 'bg-neutral-50 hover:bg-neutral-100'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <Input
              value={answers[currentQuestion?.id] || ''}
              onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
              placeholder="La tua risposta..."
              className="bg-neutral-50 border-neutral-200 h-12 rounded-xl"
            />
          )}

          <div className="flex gap-3 mt-6">
            <Button
              variant="outline"
              onClick={handlePrevQuestion}
              disabled={currentQuestionIndex === 0}
              className="flex-1 h-12 rounded-xl"
            >
              Indietro
            </Button>
            {isLastQuestion ? (
              <Button
                onClick={handleSubmitAnswers}
                disabled={submitAnswers.isPending}
                className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
              >
                {submitAnswers.isPending ? <Loader2 className="animate-spin" /> : 'Genera Cards'}
              </Button>
            ) : (
              <Button
                onClick={handleNextQuestion}
                className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
              >
                Avanti
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderGenerateStep = () => (
    <motion.div key="generate" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8 text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-neutral-400" />
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Generazione cards...</h2>
          <p className="text-neutral-500">Stiamo creando il tuo profilo aziendale</p>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderResultStep = () => (
    <motion.div key="result" variants={cardVariants} initial="initial" animate="animate" exit="exit">
      <Card className="bg-white border-0 shadow-sm rounded-3xl">
        <CardContent className="pt-10 pb-8 px-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Cards generate!</h2>
          <p className="text-neutral-500">Reindirizzamento alle tue cards...</p>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-neutral-100">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img src={fylleLogo} alt="Fylle" className="h-11 mx-auto" />
        </div>

        <AnimatePresence mode="wait">
          {currentStep === 'brand_name' && renderBrandNameStep()}
          {currentStep === 'website' && renderWebsiteStep()}
          {currentStep === 'email' && renderEmailStep()}
          {currentStep === 'goal' && renderGoalStep()}
          {currentStep === 'context' && renderContextStep()}
          {currentStep === 'research' && renderResearchStep()}
          {currentStep === 'quiz' && renderQuizStep()}
          {currentStep === 'generate' && renderGenerateStep()}
          {currentStep === 'result' && renderResultStep()}
        </AnimatePresence>
      </div>
    </div>
  );
}
