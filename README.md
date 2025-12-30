git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/cyysky/ai_messaging.git
git push -u origin main

python -m backend.main