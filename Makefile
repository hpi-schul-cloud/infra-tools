
SHELL := /bin/bash
.PHONY: all help requirements


TMPDIR				:= ./.tmp
LOCALBIN			:= ~/.local/bin
HOSTCTL_RELEASE 	:= 1.1.1
HOSTCTLGET 			:= wget -q -c  --directory-prefix=./.tmp
HOSTCTLTARGET		:= $(TMPDIR)/hostctl$(HOSTCTL_RELEASE)
HOSTCTLUNARCHIVE	:=
HOSTCTLCOPY			:=
MKDIR_P				:=

ifeq ($(OS),Windows_NT)
	HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_windows_64-bit.zip
	HOSTCTLGET += -O $(HOSTCTLTARGET)
	HOSTCTLUNARCHIVE += unzip $(HOSTCTLTARGET)
	HOSTCTLCOPY += copy $(TMPDIR)/hostctl.exe $(LOCALBIN)
	MKDIR_P += md
else
	UNAME_S := $(shell uname -s)
	MKDIR_P += mkdir -p
	ifeq ($(UNAME_S),Linux)
		HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_linux_64-bit.tar.gz
		HOSTCTLGET += -O $(HOSTCTLTARGET)
		HOSTCTLUNARCHIVE += tar -xzf $(HOSTCTLTARGET) -C $(TMPDIR) --wildcards hostctl*
		HOSTCTLCOPY += cp $(TMPDIR)/hostctl $(LOCALBIN)
	endif
	ifeq ($(UNAME_S),Darwin)
		HOSTCTLGET += https://github.com/guumaster/hostctl/releases/download/v$(HOSTCTL_RELEASE)/hostctl_$(HOSTCTL_RELEASE)_macOS_64-bit.tar.gz
		HOSTCTLGET += -O $(HOSTCTLTARGET)
		HOSTCTLUNARCHIVE += tar -xzf $(HOSTCTLTARGET) -C $(TMPDIR) --wildcards hostctl*
		HOSTCTLCOPY += cp $(TMPDIR)/hostctl $(LOCALBIN)
	endif
endif

help:
	@echo "Make commands"
	@echo "    requirements                   install all requirements"

requirements:
ifneq ($(OS),Windows_NT)
ifeq ("$(wildcard $(TMPDIR))", "")
	$(MKDIR_P) $(TMPDIR)
endif
ifeq ("$(wildcard $(LOCALBIN))", "")
	$(MKDIR_P) $(LOCALBIN)
endif
	python3 -m pip install -r s3-backup/requirements.txt
	python3 -m pip install -r sct/requirements.txt
	python3 -m pip install -r dbcmetrics/requirements.txt
endif
