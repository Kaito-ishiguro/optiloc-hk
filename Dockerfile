# OptiLoc HK API — Phase 1 portfolio image.
# Single-stage build. Relies on wheel-bundled native libs (no apt-get for GDAL/PROJ).
# Targets Cloud Run (Linux/amd64). Local dev parity via Docker Desktop on Windows.

FROM python:3.14-slim

# Non-root user/group for runtime (security best practice).
RUN groupadd --system app && useradd --system --gid app --create-home appuser

WORKDIR /app

# Install Python deps first — separate layer caches well across code edits.
COPY api/requirements.txt /app/api/requirements.txt
RUN python -m pip install --no-cache-dir -r api/requirements.txt

# Copy API source + the two solver notebooks the API loads via importlib.
COPY api /app/api
COPY notebooks/08_solve_weber_weiszfeld.py /app/notebooks/08_solve_weber_weiszfeld.py
COPY notebooks/16_solve_kmedian_ozp.py /app/notebooks/16_solve_kmedian_ozp.py
COPY frontend ./frontend

# Bake in HK demand + commercial-zone geometry (public WorldPop + Lands Dept data; no PII).
COPY data/processed/demand_points.csv /app/data/processed/demand_points.csv
COPY data/processed/ozp_commercial_union.geojson /app/data/processed/ozp_commercial_union.geojson
COPY data/processed/hk_road_network.graphml /app/data/processed/hk_road_network.graphml
COPY data/processed/demand_nodes_aggregated.csv /app/data/processed/demand_nodes_aggregated.csv
COPY data/rent/node_to_district.json /app/data/rent/node_to_district.json

# Drop root privileges before runtime.
RUN chown -R appuser:app /app
USER appuser

# Liveness probe using $PORT so it matches whatever Cloud Run injects.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD sh -c "python -c \"import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:'+'${PORT:-8080}'+'/healthz',timeout=3); sys.exit(0 if r.status==200 else 1)\""

EXPOSE 8080

ENV PORT=8080
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
