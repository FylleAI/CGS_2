



# Verifica stato Git attuale
echo "=== STATO REPOSITORY ==="
git status
echo ""

echo "=== BRANCH CORRENTE ==="
git branch -a
echo ""

echo "=== ULTIMO COMMIT ==="
git log --oneline -5
echo ""

echo "=== MODIFICHE NON COMMITTATE ==="
git diff --name-only
echo ""

echo "=== FILE STAGED ==="
git diff --cached --name-only
