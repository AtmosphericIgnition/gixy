# NOSONAR: docker:S6471 - Using explicit non-root user below
FROM python:alpine

# Create non-root user for security
RUN adduser -D -u 1000 gixy

# NOSONAR: docker:S6470 - .dockerignore excludes sensitive files (.git, .env, secrets)
COPY . /src

WORKDIR /src

RUN pip install --upgrade pip setuptools wheel
# Use pip to install the project so install_requires are honored (e.g., six)
RUN pip install .

# Switch to non-root user
USER gixy

ENTRYPOINT ["gixy"]
