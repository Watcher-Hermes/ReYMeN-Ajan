# Eğer .git yoksa init et
if [ ! -d .git ]; then
  git init
  git remote add origin git@github.com:Izleyici-Hermes/hermes-skills.git
fi

git add -A
git commit -m "Auto backup $(date +%Y-%m-%d_%H:%M)"