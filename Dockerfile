FROM google/cloud-sdk:slim

# Copy files to current directory:
COPY . /app
WORKDIR /app

# Install luigi:
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set env variables:
ENV PYTHONPATH /app
ENV LUIGI_CONFIG_PATH /app/luigi.cfg

# Create path for pickle state file:
RUN mkdir /var/lib/gce-drive

# Run Luigi:
EXPOSE 8082
ENTRYPOINT ["luigid"]