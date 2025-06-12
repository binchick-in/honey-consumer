

SERVICE_NAME=honey-consumer

ip_enrich:
	@dotenv run -- python -m honey_consumer.jobs.ipinfo_enrichment


run:
	@dotenv run -- python -m honey_consumer

# TODO: Update dockerfile to work with UV
# build:
# 	podman build -t $(SERVICE_NAME):latest .

