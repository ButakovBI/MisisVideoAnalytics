<pre>
MisisVideoAnalytics/
├── build/
│   ├── docker/
│   │   ├── backend/
│   │   │   ├── Dockerfile
│   │   │   └── test.Dockerfile
│   │   ├── build_all.py
│   │   ├── docker_compose.yml
│   │   ├── get_config.py
│   │   └── images_configuration.json
│   └── misis_bootstrap/
│       └── source/
│           ├── data/
│           │   └── versions.json
│           ├── misis_bootstrap/
│           │   ├── __init__.py
│           │   ├── bootstrap.py
│           │   └── main.py
│           ├── pyproject.toml
│           └── setup.py
└── source/
    └── backend/
        └── misis_api/
            ├── source/
            │   ├── __init__.py
            │   └── main.py
            ├── tests/
            │   ├── conftest.py
            │   └── unit/
            │       └── base/
            │           └── test_hello.py
            ├── pyproject.toml
            └── setup.py
</pre>


- Перед запуском добавить в окружение или выполнить:
export REPO_ROOT=/path_to/MisisVideoAnalytics

- Запуск тестов:
./run.sh --test

- локальное развёртывание:
./run.sh