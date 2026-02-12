FROM python:alpine  # NOSONAR

# Create non-root user for security
RUN adduser -D -u 1000 gixy

COPY . /src  # NOSONAR

WORKDIR /src

RUN pip install --upgrade pip setuptools wheel
# Use pip to install the project so install_requires are honored (e.g., six)
RUN pip install .

# Switch to non-root user
USER gixy

ENTRYPOINT ["gixy"]
