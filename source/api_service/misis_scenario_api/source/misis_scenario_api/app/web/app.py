from fastapi import FastAPI

from misis_scenario_api.app.web.routers import router


def create_app() -> FastAPI:
    app = FastAPI(title="MISIS Scenario API")
    app.include_router(router)
    return app


app = create_app()
