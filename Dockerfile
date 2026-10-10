FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "fastmcp>=3.0.0,<4.0.0" "mcp>=1.25.0,<2.0.0"
COPY server.py ./
CMD ["python", "server.py"]
