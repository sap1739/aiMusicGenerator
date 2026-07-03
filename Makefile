.PHONY: dev api test check

dev:
	npm run dev

api:
	npm run api:dev

test:
	npm test && npm run api:test

check:
	npm run lint && npm run typecheck && npm run build && npm run api:test
