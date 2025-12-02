import { QueryClientProvider } from "@tanstack/react-query";
import { Route, Switch } from "wouter";
import { queryClient } from "./lib/queryClient";
import { Toaster } from "@/components/ui/toast";
import OnboardingPage from "./pages/onboarding";
import CardsPage from "./pages/cards";

function Router() {
  return (
    <Switch>
      <Route path="/" component={OnboardingPage} />
      <Route path="/onboarding" component={OnboardingPage} />
      <Route path="/cards" component={CardsPage} />
      <Route>
        <div className="min-h-screen flex items-center justify-center bg-neutral-100">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-neutral-900 mb-2">404</h1>
            <p className="text-neutral-500">Pagina non trovata</p>
          </div>
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

