.PHONY: dev test migrate load-test seed-keys test-route dashboard gateway

dev:
	docker compose -f infra/docker-compose.yml up --build

migrate:
	alembic upgrade head

test:
	pytest tests/ -v --tb=short

dashboard:
	cd dashboard && npm run dev

gateway:
	uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000

load-test:
	cd tests/load && locust -f locustfile.py --headless -u 100 -r 10 -t 60s --host http://localhost:8000

seed-keys:
	curl -X POST http://localhost:8000/api/v1/keys \
	  -H "Content-Type: application/json" \
	  -d '{"name": "dev-key", "routing_strategy": "balanced"}'

test-route:
	curl -X POST http://localhost:8000/api/v1/routing/test \
	  -H "Authorization: Bearer $$MRX_API_KEY" \
	  -H "Content-Type: application/json" \
	  -d '{"model": "auto", "messages": [{"role": "user", "content": "Write a binary search in Python"}]}'

