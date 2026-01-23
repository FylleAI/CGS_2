import { Switch, Route } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { Toaster } from "@/components/ui/toaster";

import OnboardingPage from "@/pages/onboarding";
import CardsPage from "@/pages/cards";
import PacksPage from "@/pages/packs";
import BriefPage from "@/pages/brief";

function Router() {
  return (
    <Switch>
      <Route path="/" component={OnboardingPage} />
      <Route path="/onboarding" component={OnboardingPage} />
      <Route path="/cards" component={CardsPage} />
      <Route path="/packs" component={PacksPage} />
      <Route path="/brief" component={BriefPage} />
      <Route>
        <div className="min-h-screen flex items-center justify-center">
          <h1 className="text-2xl">404 - Page Not Found</h1>
        </div>
      </Route>
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
