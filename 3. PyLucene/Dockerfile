FROM coady/pylucene

WORKDIR /app
COPY . .

CMD ["python3", "search_bm25.py", "--help"]

FROM coady/pylucene

# Create and set working directory
WORKDIR /app

# Copy application code
COPY . .

# Default command (show help; override with docker-compose or docker run)
CMD ["python3", "search_bm25.py", "--help"]


