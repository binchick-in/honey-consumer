# High Malicious Intent HTTP Requests

```sql
select
    h.*,
    llm.type_of_exploit,
    llm.target_software
from llmdetails llm
join honey h
    on llm.honey_id == h.id
where llm.malicious = "high"
```
