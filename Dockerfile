# build stage
FROM python:3.10 AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md /720pdl/
COPY geckodriver /bin
COPY src/ /720pdl/src

# install dependencies and project
WORKDIR /720pdl
RUN pdm install --prod --no-lock --no-editable


# run stage
FROM python:3.10

# retrieve packages from build stage
ENV PYTHONPATH=/720pl/pkgs
COPY --from=builder /720pdl/__pypackages__/3.10/lib /720pdl/pkgs

# set command/entrypoint, adapt to fit your needs
CMD ["python", "-m", "src/720pdl.py"]