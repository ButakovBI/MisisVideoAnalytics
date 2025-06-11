<pre>
MisisVideoAnalytics/
├── build/
│   └── docker/
│       ├── get_config.py
│       ├── images_configuration.json
│       ├── build_all.py
│       ├── docker_compose.yml
│       └── backend/
│           ├── Dockerfile
│           └── test.Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml
└── source/
    └── backend/
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