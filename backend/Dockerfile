FROM python:3.12-alpine3.19

# Install build dependencies including git for pip git+ dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev git && \
    git --version

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
