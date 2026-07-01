# 🚀 ShopMaster — Полная инструкция по установке

## Шаг 1: GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shopmaster.git
git push -u origin main
```

## Шаг 2: Telegram (@BotFather)
```
/newbot → получить BOT_TOKEN
/mybots → Payments → получить PAYMENT_PROVIDER_TOKEN
/setmenubutton → URL: https://your-domain.onrender.com/miniapp
/setdomain → your-domain.onrender.com
/setcommands → вставить команды из файла commands.txt
```

## Шаг 3: Render
1. New → Blueprint → Connect GitHub
2. Render автоматически создаст все сервисы
3. Добавьте ENV переменные в Dashboard

## Шаг 4: Миграции
```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
python scripts/seed.py
```

## Готово! 🎉
