FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

#COPY requirements.txt .
COPY requirements/ requirements/

RUN pip install --no-cache-dir -r requirements/requirements.txt
RUN pip install --no-cache-dir -r requirements/requirements-torch.txt

COPY . /app
WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "content_assistant.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
