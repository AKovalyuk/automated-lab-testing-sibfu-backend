from asyncio import as_completed

from httpx import AsyncClient, Response


async def send_post(client: AsyncClient, url: str, json: dict) -> Response:
    return await client.post(
        url=url,
        json=json,
    )


async def send_parallel_post(client: AsyncClient, url: str, jsons: list[dict]) -> list[Response]:
    result = []
    task_list = [send_post(client, url, json) for json in jsons]
    for task in as_completed(task_list):
        result.append(await task)
    return result
