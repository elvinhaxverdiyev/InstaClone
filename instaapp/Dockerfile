# Python image
FROM python:3.11-slim

# İş qovluğu
WORKDIR /app

# Sistem paketləri
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ortam dəyişənləri
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# requirements.txt faylını əlavə et və paketləri qur
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Layihə fayllarını əlavə et
COPY . .

# Statik faylları topla (əgər varsa)
RUN python manage.py collectstatic --noinput || true

# Portu aç
EXPOSE 8000

# Django dev server-i işə sal
CMD ["python", "instaapp/manage.py", "runserver", "0.0.0.0:8000"]
