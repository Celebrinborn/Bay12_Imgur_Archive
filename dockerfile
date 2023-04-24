FROM python:3.9

# Set working directory
WORKDIR /app

# Install necessary dependencies for Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip

# Add Chrome package and key
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining files
COPY app.py .
COPY chromedriver.exe .
COPY LICENSE.chromedriver .
COPY log_config.py .
COPY logging.yaml .

# Run the application
CMD ["python", "app.py"]
