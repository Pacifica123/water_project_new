# Инструкция по начальной развертке проекта

## Без Docker

### Бэкенд
1. Если в `back/app` ещё нет виртуального окружения `lvenv3`, выполнить из папки `back/app`:
    ```bash
    python3 -m venv lvenv3
    ./lvenv3/bin/pip3 install -r ../req.txt
    ```
2. Запуск бэкенда из папки `back`:
    ```bash
    ./app/lvenv3/bin/uvicorn app.main:app --reload --port 8000
    ```

### Фронтенд
1. Перейти в папку `front`:
    ```bash
    cd front
    npm install   # если ещё не установлены зависимости
    npm run dev
    ```
2. Открывать в браузере `http://localhost:3000/` или `http://127.0.0.1:3000/` (не `192.x.x.x`).

---

## С Docker

### Через VSCode
1. Установить плагин **Container Tools** от `ms-azuretools`.
2. ПКМ на `docker-compose.yml` → `Compose Up`.
3. Если всё прошло успешно, увидите примерно:
    ```
    ✔ Network diplom_new_default       Created                                                          
    ✔ Container diplom_new-backend-1   Started                                                          
    ✔ Container diplom_new-frontend-1  Started 
    ```
4. Открывать фронтенд по адресу: `http://localhost:3000/`.
5. Чтобы выключить:
    - Перейти во вкладку **Containers**.
    - Выбрать контейнер с бэком и фронтом.
    - ПКМ → `Compose Down`.
    - Если всё прошло успешно:
        ```
        ✔ Container diplom_new-frontend-1  Removed                                                          
        ✔ Container diplom_new-backend-1   Removed                                                          
        ✔ Network diplom_new_default       Removed
        ```

### Через консоль Linux
1. Перейти в корень проекта, где лежит `docker-compose.yml`.
2. Поднять контейнеры:
    ```bash
    docker-compose up -d
    ```
3. Проверить статус контейнеров:
    ```bash
    docker-compose ps
    ```
4. Открывать фронтенд по адресу: `http://localhost:3000/`.
5. Остановить контейнеры:
    ```bash
    docker-compose down
    ```

---

> **Примечания:**
> - При разработке локально нужно убедится, что `.env.local` содержит:
>   ```
>   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
>   ```
> - Для Docker используется `.env.docker`:
>   ```
>   NEXT_PUBLIC_BACKEND_URL=http://backend:8000
>   ```
> - После изменения переменных окружения перезапускать dev server фронта.
