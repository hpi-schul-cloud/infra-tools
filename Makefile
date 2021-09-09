
SHELL := /bin/bash
.PHONY: all help requirements


TMPDIR				:= ./.tmp
HOSTCTL_RELEASE 	:= 1.1.1
HOSTCTLGET 			:= wget -q -c  --directory-prefix=./.tmp
HOSTCTLTARGET		:= $(TMPDIR)/hostctl$(HOSTCTL_RELEASE)
HOSTCTLUNARCHIVE	:=
HOSTCTLCOPY			:=

ifeq ($(OS),Windows_NT)
	HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_windows_64-bit.zip
	HOSTCTLGET += -O $(HOSTCTLTARGET)
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_linux_64-bit.tar.gz
		HOSTCTLGET += -O $(HOSTCTLTARGET)
		HOSTCTLUNARCHIVE += tar -xzf $(HOSTCTLTARGET)
	endif
	ifeq ($(UNAME_S),Darwin)
		HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_macOS_64-bit.tar.gz
		HOSTCTLGET += -O $(HOSTCTLTARGET)
		HOSTCTLUNARCHIVE += tar -xzf $(HOSTCTLTARGET)
	endif
endif

help:
	@echo "Make commands"
	@echo "    requirements                   install all requirements"

requirements:
	-[ -d $(TMPDIR) ] || mkdir -p $(TMPDIR)
	python3 -m pip install -r s3-backup/requirements.txt
	python3 -m pip install -r sc-tunnel/requirements.txt
	$(HOSTCTLGET)
	$(HOSTCTLUNARCHIVE)

