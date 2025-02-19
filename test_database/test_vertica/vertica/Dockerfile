FROM python:3.13.1-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/benchmark

RUN apt-get update && apt-get install -y --no-install-recommends
RUN pip install vertica-python faker

COPY . .

# ENTRYPOINT ["/opt/benchmark/entrypoint.sh"]
CMD ["python", "benchmark_vertica.py"]