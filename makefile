SHELL = /bin/bash

project_dependencies ?= $(addprefix $(project_root)/, cltl-requirements)

git_remote := https://github.com/leolani


include util/make/makefile.base.mk
include util/make/makefile.component.mk
include util/make/makefile.git.mk

sources := $(shell find $(project_root)/$(project_name)/emissor/*)
artifact_name := emissor
include util/make/makefile.py.base.mk

docker-ghcr-build:
	$(info "No docker build for $(project_name)")

docker-ghcr-push:
        $(info "No docker build for $(project_name)")
