FROM python:alpine

WORKDIR /src

# Copy only the files needed for pip install
COPY setup.py pyproject.toml ./
COPY gixy/ ./gixy/

RUN pip install --upgrade pip setuptools wheel
# Use pip to install the project so install_requires are honored (e.g., six)
RUN pip install .

ENTRYPOINT ["gixy"]
