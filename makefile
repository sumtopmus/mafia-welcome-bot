.PHONY: run debug test clean clean-logs clean-data clean-conversations

run:
	@ENV_FOR_DYNACONF=prod python src/bot.py

debug: clean
	@ENV_FOR_DYNACONF=dev python src/bot.py

clean: clean-logs clean-data

clean-logs:
	@rm -rf logs

clean-data:
	@rm -rf data

clean-conversations:
	@rm -f data/db_conversations