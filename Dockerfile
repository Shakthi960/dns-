# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your code
COPY . /app

# Install dependencies (adjust if needed)
RUN pip install -r requirements.txt

# Expose DNS port (53) and your internal port (5053)
EXPOSE 53/udp
EXPOSE 53/tcp
EXPOSE 5053

# Run your DNS server
CMD ["python", "dns_server.py", "--port", "53"]
