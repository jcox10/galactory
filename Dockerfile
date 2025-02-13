FROM python:3.11-slim as build

RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

RUN pip install --no-cache-dir --upgrade pip setuptools build wheel

COPY . /galactory

RUN pip install ./galactory


FROM python:3.11-slim as final

COPY --from=build /venv /venv
ENV PATH=/venv/bin:$PATH

ENTRYPOINT [ "python", "-m", "galactory" ]
