AMPY := ampy

SOURCES = \
	button.py \
	main.py \
	sensors.py \
	wifi_connect.py \
	$(NULL)

__deploy__/%.py: %.py
	@mkdir -p $(dir $@)
	$(AMPY) put $< $<
	@cp $< $@

__remove_files__/%.py : %.py
	$(AMPY) rm $< || echo 'Already deleted'
	@rm -r __deploy__/$<

deploy: $(addprefix __deploy__/, $(SOURCES))

.PHONY: clean
clean: $(addprefix __remove_files__/, $(SOURCES))
