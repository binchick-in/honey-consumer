# 🍯 Honey Consumer

Grab Honeypot records off the pub/sub, digest them, and load them into a SQLite database.

## Getting Started

1. Copy `.env.example` to `.env` and populate it
2. Create a service account in GCP with PubSub Read permissions.
3. Create a json key and populate `GOOGLE_SERVICE_JSON` with it in `.env`
4. `make run`

## 🤑 Enrichment Jobs

There are 2 jobs that will enrich the dataset with additional information.

These jobs live in `honey_consumer/jobs/`

## IPInfo
Fetch the free tier `ipinfo.io` records for the requesting IP addresses

```
make ip_enrich
```

or
```
dotenv run -- python -m honey_consumer.jobs.ipinfo_enrichment
```

## LLM Evaluation

I'm asking an LLM to evaluate each request that comes in and tell me the following information:

- How malicious is the request: low, medium, high.
- What type of exploit is being attempted, if one is present.
- The software being targeted, if the LLM can conclude that.

I'm running this on my local machine with Ollama and I'm using Gemma3 for evaluation. The prompt I'm using is in the code.

Note: this job is slow with many records in the main table. I'm not doing parallel or batch processing because this is only on my local machine and this is a toy project.

```
make llm_enrichment
```
or
```
dotenv run -- python -m honey_consumer.jobs.llm_enrichment
```
