FROM python:3.11-slim

# Install system dependencies
RUN apt update && apt install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    imagemagick \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Allow ImageMagick to read/write typical video/image formats
# MoviePy needs this or else ImageMagick may reject conversions.
# --- Fix ImageMagick policies for Pango/MoviePy (IM7) ---
RUN sed -i 's#<policy domain="coder" rights="none" pattern="PDF"#<policy domain="coder" rights="read|write" pattern="PDF"#' /etc/ImageMagick-7/policy.xml || true \
 && sed -i 's#<policy domain="coder" rights="none" pattern="PS"#<policy domain="coder" rights="read|write" pattern="PS"#' /etc/ImageMagick-7/policy.xml || true \
 && sed -i 's#<policy domain="coder" rights="none" pattern="EPS"#<policy domain="coder" rights="read|write" pattern="EPS"#' /etc/ImageMagick-7/policy.xml || true 

RUN sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/' /etc/ImageMagick-7/policy.xml

RUN echo '<policy domain="path" rights="read" pattern="/tmp/*.txt"/>' >> /etc/ImageMagick-7/policy.xml



WORKDIR /app

# Copy dependency list & install Python libs
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY main.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create folders for input/output
RUN mkdir /input /output

ENTRYPOINT ["./entrypoint.sh"]
