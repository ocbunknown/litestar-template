from litestar import get, status_codes

from src.api.v1 import dtos


@get(
    "/healthcheck",
    tags=["Healthcheck"],
    status_code=status_codes.HTTP_200_OK,
    exclude_from_auth=True,
)
async def healthcheck_endpoint() -> dtos.Status:
    return dtos.Status(status=True)
