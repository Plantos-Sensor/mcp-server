FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Set environment variables
ENV MCP_TRANSPORT=http
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PLANTOS_API_URL=https://api.plantos.co

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "-m", "plantos_mcp.server"]
