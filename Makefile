# -*- coding: utf-8 -*-
# ReYMeN Agent — Makefile
# Ortak gelistirme komutlari

.PHONY: help install test lint clean dev backup

SHELL := /bin/bash
PYTHON := python
PIP := $(PYTHON) -m pip
PROJECT := reymen-agent

# ── Yardim ──────────────────────────────────────────────────────────────────────
help: ## Bu yardim mesajini goster
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Kurulum ─────────────────────────────────────────────────────────────────────
install: ## Tum bagimliliklari kur (setup.py)
	$(PYTHON) setup.py

install-fast: ## Sadece pip paketlerini kur (hizli)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install-fast ## Dev bagimliliklari ekle
	$(PIP) install pytest pytest-cov mypy flake8 pre-commit

# ── Test ────────────────────────────────────────────────────────────────────────
test: ## Testleri calistir
	$(PYTHON) -m pytest tests/ -v --tb=short

test-quick: ## Hizli test (slow mark atlanir)
	$(PYTHON) -m pytest tests/ -v --tb=short -m "not slow"

test-cov: ## Test + coverage raporu
	$(PYTHON) -m pytest tests/ --cov=reymen --cov-report=term --cov-report=html

test-one: ## Tek test dosyasi calistir: make test-one t=tests/test_beyin.py
	$(PYTHON) -m pytest $(t) -v --tb=long

# ── Lint / Kalite ───────────────────────────────────────────────────────────────
lint: ## Tum lint kontrolleri
	-$(PYTHON) -m flake8 reymen/ --max-line-length=120 --statistics
	-$(PYTHON) -m mypy reymen/ --ignore-missing-imports --warn-unused-configs

lint-fix: ## Auto-fix ile duzelt
	$(PYTHON) -m autoflake --in-place --remove-all-unused-imports -r reymen/ 2>/dev/null || true

# ── Temizlik ────────────────────────────────────────────────────────────────────
clean: ## Gecici dosyalari temizle
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage htmlcov 2>/dev/null || true
	@echo "✅ Temizlik tamam"

clean-all: clean ## Temizlik + venv sil
	rm -rf venv/ bot_venv/ 2>/dev/null || true
	@echo "✅ Tüm temizlik tamam"

# ── Git ─────────────────────────────────────────────────────────────────────────
git-status: ## Git durumu
	git status --short

git-log: ## Son commit'ler
	git log --oneline -20

# ── Docker ──────────────────────────────────────────────────────────────────────
docker-build: ## Docker imaji olustur
	docker build -t $(PROJECT):latest .

docker-run: ## Docker konteyneri calistir
	docker run --rm -it \
		-v $(CURDIR)/.env:/app/.env:ro \
		--name reymen-agent \
		$(PROJECT):latest

# ── Yedekleme ───────────────────────────────────────────────────────────────────
backup: ## Projeyi ReYMeN-full-backup/ klasorune yedekle
	rsync -a --exclude='venv/' --exclude='bot_venv/' --exclude='node_modules/' \
		--exclude='.git/' --exclude='__pycache__/' --exclude='*.pyc' \
		./ ../ReYMeN-full-backup/
	@echo "✅ Yedek tamam: ../ReYMeN-full-backup/"

# ── Dev ─────────────────────────────────────────────────────────────────────────
dev: ## Gelistirme modu (test + lint)
	make lint
	make test-quick

check-env: ## .env dosyasini kontrol et
	@test -f .env || (echo "❌ .env dosyasi yok! setup.py calistir." && exit 1)
	@echo "✅ .env mevcut"
