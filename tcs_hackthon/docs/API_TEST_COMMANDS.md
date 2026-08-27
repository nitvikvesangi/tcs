# API Test Commands (cURL)

Test Health Check:
```bash
curl http://localhost:8000/health
```

Test Recommendations List (All):
```bash
curl "http://localhost:8000/recommendations"
```

Test Recommendations with Filter (City):
```bash
curl "http://localhost:8000/recommendations?city=Hyderabad"
```

Test Inventory:
```bash
curl "http://localhost:8000/inventory"
```

Test Promotions:
```bash
curl "http://localhost:8000/promotions"
```

Test AI Chat:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Which products should I promote?"}'
```
