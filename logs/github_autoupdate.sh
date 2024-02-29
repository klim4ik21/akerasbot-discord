#!/bin/bash

# Путь к вашему боту
BOT_DIR="/root/akerasbot"

# Ветка, которую вы хотите отслеживать (main)
BRANCH="main"

# Персональный токен доступа GitHub
GITHUB_TOKEN="github token"
REPO_URL="repo url"

# Устанавливаем токен как переменную окружения
export GITHUB_TOKEN
export GIT_ASKPASS="/bin/echo"
export GIT_USERNAME="gitusername"
export GIT_PASSWORD="gitpass"

# Переход в папку с ботом
cd $BOT_DIR

# Проверяем наличие изменений в ветке main
git remote update origin --prune

# Получаем локальную и удаленную хеш-сумму текущей ветки
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/$BRANCH)

# Если хеш-суммы разные, выполняем обновление и перезапуск
if [ $LOCAL_HASH != $REMOTE_HASH ]; then
    echo "Обнаружены изменения в ветке $BRANCH. Обновление и перезапуск..."
    
    # Пул обновлений из указанной ветки
    git pull $REPO_URL $BRANCH

    # Перезапуск вашего бота (пример с использованием Supervisor)
    supervisorctl restart akeras

    echo "Бот обновлен и перезапущен."
else
    echo "Нет изменений в ветке $BRANCH. Не требуется обновление."
fi


