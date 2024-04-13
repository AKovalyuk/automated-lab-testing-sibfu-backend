from app.config import settings
from app.config.languages import LANGUAGES, ARCHIVED
from tests.utils import get_user_authorization_header, create_test_user


async def test_get_languages(client, session):
    user, password = await create_test_user(session)
    response = await client.get(
        url=f"{settings.PATH_PREFIX}/language",
        headers=get_user_authorization_header(user, password),
    )
    assert response.status_code == 200
    assert len(response.json()) == len(LANGUAGES) - len(ARCHIVED)
    for lang_obj in response.json():
        assert lang_obj["id"] in LANGUAGES.keys()
