.PHONY: run debug test clean-logs clean-data clean-conversations

run:
	@ENV_FOR_DYNACONF=production python src/bot.py

debug: clean-all
	@python src/bot.py

clean-all: clean-logs

clean-logs:
	@rm -rf logs

clean-data:
	@rm -rf data

clean-conversations:
	@rm -f data/db_conversations