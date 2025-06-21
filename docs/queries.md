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

# High Malicious Requests by Country in Descending Order
```sql
select
    i.country as country,
    count(*) as high_malicious_count
from honey h
join llmdetails l
    on h.id = l.honey_id
left join ipinfo i
    on h.remote_address = i.ip_address
where l.malicious = 'high'
group by i.country
order by 2 desc;
```

# Top Malicious IP Addresses
```sql
select 
    ipinfo.ip_address,
    ipinfo.country,
    count(*) as attack_count
from honey
join  ipinfo
    on honey.remote_address = ipinfo.ip_address
join llmdetails
    on honey.id = llmdetails.honey_id
where llmdetails.malicious in ('high', 'medium')
group by 1, 2
order by 3 desc
limit 20;
```

# ASNs Generating the Most Malicious Traffic
```sql
select
    ipinfo.asn,
    ipinfo.as_name,
    ipinfo.as_domain,
    count(*) as count
from honey
join ipinfo on honey.remote_address = ipinfo.ip_address
join llmdetails on honey.id = llmdetails.honey_id
where llmdetails.malicious = 'high'
group by 1, 2, 3
order by 4 desc
limit 10;
```