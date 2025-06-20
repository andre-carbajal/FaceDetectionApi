FROM python:3.12-slim AS base_image

RUN apt-get update && \
    apt-get -y install unzip && \
    apt-get -y install curl && \
    apt-get -y install gnupg && \
    apt-get -y install wget && \
    apt-get -y install cmake && \
    apt-get -y install build-essential && \
    apt-get -y install libgl1 && \
    apt-get -y install libglib2.0-0

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    ACCEPT_EULA=Y apt-get install -y mssql-tools18 && \
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && \
    apt-get install -y unixodbc-dev && \
    apt-get install -y libgssapi-krb5-2

ENV PATH="$PATH:/opt/mssql-tools18/bin"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]

EXPOSE 5000
