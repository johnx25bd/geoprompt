FROM postgis/postgis:16-3.5

# Set environment variables
ENV POSTGRES_DB=overture
ENV POSTGRES_USER=mapper
ENV POSTGRES_PASSWORD=password

# Copy data to volume
COPY ./init.sql /docker-entrypoint-initdb.d
COPY ./init-postgis.sh /docker-entrypoint-initdb.d

RUN chmod +x /docker-entrypoint-initdb.d/init-postgis.sh

# # Expose the default PostgreSQL port
# EXPOSE 5432