RUN EVERYTHING FROM `data` dir

Install pre-commit
```
pre-commit install
pre-commit install-hooks
```

Create venv
```
uv venv
```

Add package
```
uv add <package>
```

Sync (after adding, lock, ...)
```
uv sync
```

Run tests
```
python -m scripts.run_tests
```

Run test
```
python -m scripts.run_tests <path-to-test-file>
```
