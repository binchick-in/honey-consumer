

SERVICE_NAME=honey-consumer

ip_enrich:
	@dotenv run -- python -m honey_consumer.jobs.ipinfo_enrichment

run:
	@dotenv run -- python -m honey_consumer

show-schema:
	@sqlite3 honey.db .schema

# TODO: Update dockerfile to work with UV
# build:
# 	podman build -t $(SERVICE_NAME):latest .

show-db-stats:
	@echo "Total Honey Records"
	@sqlite3 honey.db "select count(id) from honey"
	@echo "Total IPInfo Enrichments"
	@sqlite3 honey.db "select count(id) from ipinfo"
	@echo "Total LLM Enrichments"
	@sqlite3 honey.db "select count(*) from llmdetails"
