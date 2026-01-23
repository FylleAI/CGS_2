/**
 * Packs Page for Fylle Onboarding v3
 * Shows pack details and starts brief generation
 */

import { useEffect, useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, ArrowLeft } from 'lucide-react';
import { usePacks } from '@/hooks/usePacks';
import { DEFAULT_PACKS } from '@shared/types/packs';

const fylleLogo = '/assets/fylle-logotipo-green.png';

function getQueryParam(name: string): string | null {
  if (typeof window === 'undefined') return null;
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

export default function PacksPage() {
  const [, navigate] = useLocation();
  const userId = getQueryParam('user_id');
  const packId = getQueryParam('pack_id');
  
  const { briefs, briefsLoading, startBrief } = usePacks({ userId });
  
  const pack = DEFAULT_PACKS.find(p => p.id === packId);
  const packBriefs = briefs.filter(b => b.packId === packId);

  const handleStartBrief = async () => {
    if (!packId) return;
    
    try {
      const response = await startBrief.mutateAsync(packId);
      navigate(`/brief?brief_session_id=${response.briefSessionId}&user_id=${userId}`);
    } catch (error) {
      console.error('Failed to start brief:', error);
    }
  };

  if (!pack) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <Card className="bg-white border-neutral-200 shadow-sm rounded-3xl max-w-md">
          <CardContent className="pt-10 pb-8 px-8 text-center">
            <h2 className="text-xl font-semibold text-neutral-900 mb-2">Pack non trovato</h2>
            <Button onClick={() => navigate('/cards')} className="bg-neutral-900 hover:bg-neutral-800 rounded-xl">
              Torna alle Cards
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-6 bg-neutral-100">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <img src={fylleLogo} alt="Fylle" className="h-11 mx-auto" />
        </div>

        <button
          onClick={() => navigate(`/cards?user_id=${userId}`)}
          className="flex items-center gap-2 text-neutral-500 hover:text-neutral-700 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Torna alle Cards
        </button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Pack Header */}
          <Card className="bg-white border-0 shadow-sm rounded-3xl mb-8">
            <CardContent className="p-8">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-neutral-100 rounded-2xl flex items-center justify-center text-4xl">
                  {pack.icon}
                </div>
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-neutral-900 mb-2">{pack.displayName}</h1>
                  <p className="text-neutral-500">{pack.description}</p>
                </div>
                <Button
                  onClick={handleStartBrief}
                  disabled={startBrief.isPending}
                  className="bg-neutral-900 hover:bg-neutral-800 rounded-xl px-8 py-6 text-lg"
                >
                  {startBrief.isPending ? (
                    <Loader2 className="animate-spin mr-2" />
                  ) : null}
                  Genera Nuovo Brief
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Existing Briefs */}
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">I tuoi Brief</h2>
          
          {briefsLoading ? (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-neutral-400" />
              <p className="text-neutral-500">Caricamento brief...</p>
            </div>
          ) : packBriefs.length === 0 ? (
            <Card className="bg-white border-0 shadow-sm rounded-2xl">
              <CardContent className="p-8 text-center">
                <p className="text-neutral-500 mb-4">Non hai ancora generato brief per questo pack.</p>
                <p className="text-sm text-neutral-400">
                  Clicca "Genera Nuovo Brief" per iniziare.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {packBriefs.map((brief) => (
                <Card key={brief.id} className="bg-white border-0 shadow-sm rounded-2xl">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-neutral-900">
                          {brief.title || 'Brief senza titolo'}
                        </h3>
                        <p className="text-sm text-neutral-500">
                          Creato il {new Date(brief.createdAt).toLocaleDateString('it-IT')}
                        </p>
                      </div>
                      <Button variant="outline" className="rounded-xl">
                        Visualizza
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
