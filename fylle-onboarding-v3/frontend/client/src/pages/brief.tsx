/**
 * Brief Page for Fylle Onboarding v3
 * Quiz-like interface for brief generation
 */

import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, ArrowLeft, CheckCircle } from 'lucide-react';
import { usePacks } from '@/hooks/usePacks';
import type { BriefQuestion, BriefDocument } from '@shared/types/packs';

const fylleLogo = '/assets/fylle-logotipo-green.png';

function getQueryParam(name: string): string | null {
  if (typeof window === 'undefined') return null;
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

type BriefStep = 'loading' | 'questions' | 'generating' | 'complete';

export default function BriefPage() {
  const [, navigate] = useLocation();
  const userId = getQueryParam('user_id');
  const briefSessionId = getQueryParam('brief_session_id');
  
  const [currentStep, setCurrentStep] = useState<BriefStep>('loading');
  const [questions, setQuestions] = useState<BriefQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [brief, setBrief] = useState<BriefDocument | null>(null);
  
  const { startBrief, submitBriefAnswers } = usePacks({ userId });

  useEffect(() => {
    // TODO: Fetch questions for this brief session from API
    // For now, simulate with placeholder questions
    const mockQuestions: BriefQuestion[] = [
      {
        id: 'q1',
        question: 'Qual è la tua policy sugli emoji nei contenuti?',
        options: ['Emoji non consentiti', 'Emoji solo in social media', 'Emoji consentiti con moderazione', 'Emoji liberamente utilizzabili'],
        required: true,
        section: 'brand_voice' as any,
        reason: 'Per definire le linee guida di stile visivo'
      },
      {
        id: 'q2',
        question: 'Come preferisci strutturare l\'apertura degli articoli?',
        options: ['Titolo + 1 frase contesto', 'Titolo + 2-3 frasi contesto', 'Titolo + paragrafo introduttivo', 'Titolo + sezione dedicata'],
        required: true,
        section: 'editorial_structure' as any,
        reason: 'Per standardizzare il formato di apertura'
      },
      {
        id: 'q3',
        question: 'Come vuoi gestire le citazioni delle fonti?',
        options: ['(Fonte, Data) alla fine della frase', 'Nota a piè di pagina', 'Link ipertestuale nel testo', 'Sezione riferimenti finale'],
        required: true,
        section: 'citations' as any,
        reason: 'Per standardizzare il formato delle citazioni'
      },
    ];
    
    setQuestions(mockQuestions);
    setCurrentStep('questions');
  }, [briefSessionId]);

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!briefSessionId) return;
    
    setCurrentStep('generating');
    
    try {
      const response = await submitBriefAnswers.mutateAsync({
        briefSessionId,
        answers,
      });
      
      setBrief(response.brief);
      setCurrentStep('complete');
    } catch (error) {
      console.error('Failed to generate brief:', error);
      setCurrentStep('questions');
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  if (currentStep === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-neutral-400" />
          <p className="text-neutral-500">Caricamento domande...</p>
        </div>
      </div>
    );
  }

  if (currentStep === 'generating') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <Card className="bg-white border-0 shadow-sm rounded-3xl max-w-md">
          <CardContent className="pt-10 pb-8 px-8 text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-neutral-400" />
            <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Generazione brief...</h2>
            <p className="text-neutral-500">Stiamo creando il tuo brief personalizzato</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (currentStep === 'complete' && brief) {
    return (
      <div className="min-h-screen py-12 px-6 bg-neutral-100">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <img src={fylleLogo} alt="Fylle" className="h-11 mx-auto mb-4" />
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-neutral-900 mb-2">Brief Generato!</h1>
          </div>

          <Card className="bg-white border-0 shadow-sm rounded-3xl">
            <CardContent className="p-8">
              <h2 className="text-xl font-semibold text-neutral-900 mb-4">Purpose</h2>
              <p className="text-neutral-700 mb-6">{brief.purpose}</p>

              <h2 className="text-xl font-semibold text-neutral-900 mb-4">Brand Voice</h2>
              <div className="bg-neutral-50 rounded-xl p-4 mb-6">
                <p className="text-neutral-700 mb-2"><strong>Voice:</strong> {brief.brandVoice?.voice}</p>
                <p className="text-neutral-700 mb-2"><strong>Emoji Policy:</strong> {brief.brandVoice?.emojiPolicy}</p>
                <p className="text-neutral-700"><strong>Opening:</strong> {brief.brandVoice?.opening}</p>
              </div>

              <h2 className="text-xl font-semibold text-neutral-900 mb-4">Editorial Structure</h2>
              <div className="bg-neutral-50 rounded-xl p-4 mb-6">
                <p className="text-neutral-700 mb-2"><strong>Format:</strong> {brief.editorialStructure?.format}</p>
                <ul className="list-disc list-inside text-neutral-700">
                  {brief.editorialStructure?.sections?.map((section, idx) => (
                    <li key={idx}>{section}</li>
                  ))}
                </ul>
              </div>

              <div className="flex gap-4 mt-8">
                <Button
                  variant="outline"
                  onClick={() => navigate(`/cards?user_id=${userId}`)}
                  className="flex-1 h-12 rounded-xl"
                >
                  Torna alle Cards
                </Button>
                <Button
                  className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
                >
                  Scarica Brief
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-6 bg-neutral-100">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <img src={fylleLogo} alt="Fylle" className="h-11 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-neutral-900 mb-2">Crea il tuo Brief</h1>
          <p className="text-neutral-500">Rispondi alle domande per generare un brief personalizzato</p>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 bg-neutral-200 rounded-full mb-8">
          <div 
            className="h-full bg-neutral-900 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        <AnimatePresence mode="wait">
          {currentQuestion && (
            <motion.div
              key={currentQuestion.id}
              variants={cardVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.25 }}
            >
              <Card className="bg-white border-0 shadow-sm rounded-3xl">
                <CardContent className="pt-10 pb-8 px-8">
                  <div className="text-sm text-neutral-400 mb-2">
                    Domanda {currentQuestionIndex + 1} di {questions.length}
                  </div>
                  <h2 className="text-xl font-semibold text-neutral-900 mb-6">
                    {currentQuestion.question}
                  </h2>
                  
                  {currentQuestion.reason && (
                    <p className="text-sm text-neutral-500 mb-4 italic">
                      {currentQuestion.reason}
                    </p>
                  )}

                  <div className="space-y-3">
                    {currentQuestion.options.map((option, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleAnswerChange(currentQuestion.id, option)}
                        className={`w-full p-4 rounded-xl text-left transition-colors ${
                          answers[currentQuestion.id] === option
                            ? 'bg-neutral-900 text-white'
                            : 'bg-neutral-50 hover:bg-neutral-100 text-neutral-700'
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>

                  <div className="flex gap-3 mt-8">
                    <Button
                      variant="outline"
                      onClick={handlePrevious}
                      disabled={currentQuestionIndex === 0}
                      className="flex-1 h-12 rounded-xl"
                    >
                      Indietro
                    </Button>
                    {isLastQuestion ? (
                      <Button
                        onClick={handleSubmit}
                        disabled={!answers[currentQuestion.id] || submitBriefAnswers.isPending}
                        className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
                      >
                        {submitBriefAnswers.isPending ? (
                          <Loader2 className="animate-spin" />
                        ) : (
                          'Genera Brief'
                        )}
                      </Button>
                    ) : (
                      <Button
                        onClick={handleNext}
                        disabled={!answers[currentQuestion.id]}
                        className="flex-1 bg-neutral-900 hover:bg-neutral-800 h-12 rounded-xl"
                      >
                        Avanti
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
