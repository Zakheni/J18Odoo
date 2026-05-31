.PHONY: up down restart logs ps shell init module backup restore

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f odoo

ps:
	docker compose ps

shell:
	docker compose exec odoo /bin/bash

psql:
	docker compose exec db psql -U odoo18 -d odoo18

init:
	docker compose exec odoo odoo -d odoo18 -i base --stop-after-init
	docker compose exec odoo odoo -d odoo18 \
		-i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting \
		--stop-after-init

module:
	docker compose exec odoo odoo -d odoo18 -u $(module) --stop-after-init

backup:
	@mkdir -p backups
	docker compose exec db pg_dump -U odoo18 odoo18 > backups/odoo18_$$(date +%Y%m%d_%H%M%S).sql
	docker compose exec odoo tar czf - /var/lib/odoo > backups/filestore_$$(date +%Y%m%d_%H%M%S).tar.gz
	@echo "Backup saved to ./backups/"

restore:
	@test -f $(sql) || (echo "Usage: make restore sql=backup.sql [filestore=filestore.tar.gz]" && exit 1)
	docker compose exec -T db psql -U odoo18 -d odoo18 < $(sql)
	@if [ -n "$(filestore)" ]; then \
		docker compose exec -T odoo tar xzf - -C / < $(filestore); \
		docker compose restart odoo; \
	fi
