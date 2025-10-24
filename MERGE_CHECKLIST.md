# ✅ Merge Checklist: `analytics-dashboard` → `main`

**Use this checklist to ensure a smooth merge process.**

---

## 🔴 **CRITICAL - Must Complete Before Merge**

### 1. Commit Uncommitted Changes

- [ ] **Review uncommitted changes**
  ```bash
  git status
  git diff
  ```

- [ ] **Stage Context Growth Bar feature**
  ```bash
  git add onboarding-frontend/src/components/common/ContextGrowthBar.tsx
  git add onboarding-frontend/src/components/cards/
  git add onboarding-frontend/src/components/wizard/WizardContainer.tsx
  git add onboarding-frontend/src/pages/OnboardingPage.tsx
  git add onboarding-frontend/src/components/steps/Step4QuestionsForm.tsx
  git add onboarding-frontend/src/store/onboardingStore.ts
  git add onboarding-frontend/src/hooks/useOnboarding.ts
  git add onboarding-frontend/CONTEXT_GROWTH_BAR_FEATURE.md
  git add onboarding-frontend/package.json
  git add onboarding-frontend/package-lock.json
  ```

- [ ] **Stage backend changes**
  ```bash
  git add core/infrastructure/workflows/handlers/onboarding_content_handler.py
  git add core/application/use_cases/generate_content.py
  git add core/domain/entities/content.py
  git add onboarding/application/builders/payload_builder.py
  git add onboarding/application/use_cases/execute_onboarding.py
  git add onboarding/application/use_cases/synthesize_snapshot.py
  git add onboarding/config/settings.py
  git add onboarding/domain/models.py
  git add onboarding/infrastructure/adapters/cgs_adapter.py
  ```

- [ ] **Stage frontend cleanup**
  ```bash
  git add onboarding-frontend/src/components/steps/Step1CompanyInput.tsx
  git add onboarding-frontend/src/components/steps/Step6Results.tsx
  git add onboarding-frontend/src/config/constants.ts
  git add onboarding-frontend/src/index.css
  git add onboarding-frontend/src/renderers/ContentRenderer.tsx
  git add onboarding-frontend/src/renderers/RendererRegistry.ts
  git add onboarding-frontend/src/types/onboarding.ts
  ```

- [ ] **Handle deleted files**
  ```bash
  # If analytics handler deletion was intentional:
  git rm core/infrastructure/workflows/handlers/onboarding_analytics_handler.py
  git rm onboarding-frontend/src/renderers/AnalyticsRenderer.tsx
  
  # If it was accidental, restore them:
  # git restore core/infrastructure/workflows/handlers/onboarding_analytics_handler.py
  # git restore onboarding-frontend/src/renderers/AnalyticsRenderer.tsx
  ```

- [ ] **Update __init__.py**
  ```bash
  git add core/infrastructure/workflows/__init__.py
  ```

- [ ] **Update README**
  ```bash
  git add README.md
  ```

- [ ] **Commit all changes**
  ```bash
  git commit -m "feat: Add Context Growth Bar and consolidate onboarding workflows

  - Add minimal 4px context growth bar to onboarding UI
  - Implement smooth animations with glow effects
  - Add context percentage tracking in store
  - Consolidate analytics and content handlers into single handler
  - Remove duplicate analytics renderer
  - Update payload builder for unified workflow
  - Add comprehensive documentation
  
  Features:
  - Context bar never reaches 100% (gamification)
  - Present in wizard and result cards
  - Encourages continuous context enrichment
  - Smooth incremental updates on question answers
  
  Breaking Changes: None
  "
  ```

---

### 2. Add Documentation Files

- [ ] **Stage documentation**
  ```bash
  git add CARD_DATA_EXAMPLES.md
  git add CARD_FIELDS_MAPPING.md
  git add CARD_MODIFICATION_EXAMPLES.md
  git add CARD_SYSTEM_ARCHITECTURE.md
  git add CLEANUP_SUMMARY.md
  git add CODE_EXAMPLES.md
  git add DOCUMENTATION_INDEX.md
  git add ENV_CONFIGURATION_SUMMARY.md
  git add EXECUTIVE_SUMMARY_ONBOARDING.md
  git add FRONTEND_LOADING_SCREENS_ANALYSIS.md
  git add ONBOARDING_DOCUMENTATION.md
  git add ONBOARDING_FLOW_ANALYSIS.md
  git add QUICK_REFERENCE.md
  git add MIGRATIONDOCS/
  git add docs/OTTIMIZZAZIONI_ANALYTICS_WORKFLOW.md
  git add onboarding-frontend/STABLE_STATE.md
  git add onboarding/GUIDA_FRONTEND.md
  ```

- [ ] **Commit documentation**
  ```bash
  git commit -m "docs: Add comprehensive system documentation

  - Card system architecture and examples
  - Onboarding flow analysis
  - Frontend implementation guides
  - Environment configuration summary
  - Migration documentation
  - Quick reference guides
  "
  ```

---

### 3. Clean Up Old Files

- [ ] **Remove old environment files**
  ```bash
  git rm onboarding/.env.old
  ```

- [ ] **Move test files to proper location** (optional)
  ```bash
  git mv test_analytics_payload.py scripts/
  git mv test_gemini_only.py scripts/
  git mv test_json_parse.py scripts/
  ```

- [ ] **Commit cleanup**
  ```bash
  git commit -m "chore: Clean up old files and reorganize tests"
  ```

---

### 4. Run Tests

- [ ] **Frontend tests**
  ```bash
  cd onboarding-frontend
  npm test
  npm run type-check
  cd ..
  ```

- [ ] **Backend tests** (if available)
  ```bash
  cd onboarding
  pytest
  cd ..
  ```

- [ ] **Linting**
  ```bash
  cd onboarding-frontend
  npm run lint
  cd ..
  ```

---

### 5. End-to-End Testing

- [ ] **Start all services**
  ```bash
  # Terminal 1: Backend
  python3 start_backend.py
  
  # Terminal 2: Onboarding Frontend
  cd onboarding-frontend && npm run dev
  
  # Terminal 3: CGS Frontend
  cd web/react-app && npm start
  ```

- [ ] **Test complete flow**
  - [ ] Open http://localhost:3001
  - [ ] Enter company name
  - [ ] Wait for research to complete
  - [ ] Review snapshot
  - [ ] Answer all questions
  - [ ] Verify context bar grows smoothly
  - [ ] Check results display correctly
  - [ ] Verify all 4 cards show context bar
  - [ ] Check CTA message shows correct percentage

- [ ] **Test error scenarios**
  - [ ] Invalid company name
  - [ ] Network failure during research
  - [ ] Missing required fields
  - [ ] API timeout

- [ ] **Test browser compatibility**
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari

---

## 🟡 **IMPORTANT - Should Complete Before Merge**

### 6. Code Review

- [ ] **Self-review changes**
  ```bash
  git diff main...analytics-dashboard
  ```

- [ ] **Check for sensitive data**
  - [ ] No API keys in code
  - [ ] No passwords in code
  - [ ] No personal data in code

- [ ] **Check for console.logs**
  ```bash
  grep -r "console.log" onboarding-frontend/src/
  ```

- [ ] **Check for TODOs**
  ```bash
  grep -r "TODO" onboarding-frontend/src/
  grep -r "FIXME" onboarding-frontend/src/
  ```

---

### 7. Update Documentation

- [ ] **Update main README.md**
  - [ ] Add Context Growth Bar to features list
  - [ ] Update screenshots (if any)
  - [ ] Update setup instructions

- [ ] **Create CHANGELOG entry** (if exists)
  ```markdown
  ## [Unreleased]
  
  ### Added
  - Context Growth Bar for onboarding UI
  - Metadata-driven rendering system
  - Company snapshot card visualization
  - Consolidated onboarding workflow handler
  
  ### Changed
  - Unified analytics and content generation workflows
  - Improved payload builder structure
  
  ### Removed
  - Separate analytics workflow handler (consolidated)
  - Analytics renderer (replaced by metadata-driven system)
  ```

---

### 8. Performance Check

- [ ] **Check bundle size**
  ```bash
  cd onboarding-frontend
  npm run build
  # Check dist/ folder size
  ```

- [ ] **Check for large dependencies**
  ```bash
  npm list --depth=0
  ```

- [ ] **Lighthouse audit** (optional)
  - Open http://localhost:3001
  - Run Lighthouse in Chrome DevTools
  - Check Performance, Accessibility, Best Practices, SEO

---

## 🟢 **OPTIONAL - Nice to Have**

### 9. Additional Checks

- [ ] **Accessibility audit**
  - [ ] Keyboard navigation works
  - [ ] Screen reader compatible
  - [ ] Color contrast meets WCAG AA

- [ ] **Mobile responsiveness**
  - [ ] Test on mobile viewport
  - [ ] Touch interactions work
  - [ ] No horizontal scroll

- [ ] **SEO optimization**
  - [ ] Meta tags present
  - [ ] Semantic HTML
  - [ ] Alt text on images

---

## 🚀 **MERGE PROCESS**

### 10. Pre-Merge Final Steps

- [ ] **Push all commits to remote**
  ```bash
  git push origin analytics-dashboard
  ```

- [ ] **Check CI/CD pipeline** (if exists)
  - [ ] All tests passing
  - [ ] Build successful
  - [ ] No linting errors

- [ ] **Create Pull Request** (if using GitHub/GitLab)
  - [ ] Fill in PR template
  - [ ] Add reviewers
  - [ ] Link related issues
  - [ ] Add labels

---

### 11. Merge to Main

**Option A: Squash and Merge (Recommended)**
```bash
git checkout main
git pull origin main
git merge --squash analytics-dashboard
git commit -m "feat: Add comprehensive onboarding system with Context Growth Bar

See MERGE_EVALUATION_ANALYTICS_DASHBOARD.md for full details.
"
git push origin main
```

**Option B: Merge Commit**
```bash
git checkout main
git pull origin main
git merge analytics-dashboard --no-ff
git push origin main
```

**Option C: Rebase and Merge**
```bash
git checkout analytics-dashboard
git rebase main
git checkout main
git merge analytics-dashboard --ff-only
git push origin main
```

---

### 12. Post-Merge Verification

- [ ] **Verify main branch**
  ```bash
  git checkout main
  git pull origin main
  git log --oneline -5
  ```

- [ ] **Test on main**
  - [ ] Start all services
  - [ ] Run full onboarding flow
  - [ ] Verify everything works

- [ ] **Tag release** (optional)
  ```bash
  git tag -a v1.0.0 -m "Release v1.0.0: Onboarding system with Context Growth Bar"
  git push origin v1.0.0
  ```

- [ ] **Deploy to staging/production**
  - [ ] Update environment variables
  - [ ] Run database migrations
  - [ ] Deploy frontend
  - [ ] Deploy backend
  - [ ] Smoke test

---

## 📊 **Post-Merge Monitoring**

### 13. Monitor Production

- [ ] **Check logs for errors**
  ```bash
  tail -f logs/backend.log
  ```

- [ ] **Monitor API performance**
  - [ ] Response times
  - [ ] Error rates
  - [ ] Success rates

- [ ] **Check user analytics**
  - [ ] Onboarding completion rate
  - [ ] Drop-off points
  - [ ] Average time to complete

- [ ] **Gather feedback**
  - [ ] User surveys
  - [ ] Support tickets
  - [ ] Bug reports

---

## ✅ **COMPLETION**

- [ ] **All critical items completed**
- [ ] **All important items completed**
- [ ] **Merge successful**
- [ ] **Production verified**
- [ ] **Team notified**

---

**Checklist completed by:** _________________  
**Date:** _________________  
**Merge commit:** _________________


