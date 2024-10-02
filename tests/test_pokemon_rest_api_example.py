from dataclasses import asdict
from http import HTTPStatus

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from lecture_2.rest_example import store
from lecture_2.rest_example.main import app
from lecture_2.rest_example.store.models import PokemonEntity, PokemonInfo

faker = Faker()
client = TestClient(app)


@pytest.fixture()
def pokemon_info() -> PokemonInfo:
    return PokemonInfo(faker.name(), faker.boolean())


@pytest.fixture()
def existing_pokemon(pokemon_info: PokemonInfo):
    entity = store.add(pokemon_info)

    yield entity

    store.delete(entity.id)


@pytest.fixture()
def not_existing_pokemon(pokemon_info: PokemonInfo):
    entity = store.add(pokemon_info)
    store.delete(entity.id)

    return entity


@pytest.fixture()
def existing_pokemons():
    pokemons = [
        store.add(PokemonInfo(faker.name(), faker.boolean())) for _ in range(25)
    ]

    yield pokemons

    for pokemon in pokemons:
        store.delete(pokemon.id)


def test_get_pokemon_by_id(existing_pokemon: PokemonEntity) -> None:
    response = client.get(f"/pokemon/{existing_pokemon.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": existing_pokemon.id,
        **asdict(existing_pokemon.info),
    }


@pytest.mark.parametrize(
    ("offset", "limit", "status_code"),
    [
        (None, None, HTTPStatus.OK),
        (0, 1, HTTPStatus.OK),
        (0, 10, HTTPStatus.OK),
        (2, 10, HTTPStatus.OK),
        (100, 10, HTTPStatus.OK),
        (0, 0, HTTPStatus.UNPROCESSABLE_ENTITY),
        (0, -10, HTTPStatus.UNPROCESSABLE_ENTITY),
        (-1, 10, HTTPStatus.UNPROCESSABLE_ENTITY),
        (-1, -1, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_get_pokemon_list(
    existing_pokemons: list[PokemonEntity],
    offset: int | None,
    limit: int | None,
    status_code: int,
) -> None:
    params = {"offset": offset, "limit": limit}
    params = {k: v for k, v in params.items() if v is not None}

    response = client.get("/pokemon", params=params)

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        data = response.json()
        assert isinstance(data, list)

        for item in data:
            assert any(p.id == item["id"] for p in existing_pokemons)


def test_delete_pokemon(existing_pokemon: PokemonEntity) -> None:
    response = client.delete(f"/pokemon/{existing_pokemon.id}")

    assert response.status_code == HTTPStatus.OK

    response = client.get(f"/pokemon/{existing_pokemon.id}")

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ("pokemon", "new_body", "upsert", "status_code"),
    [
        (
            "existing_pokemon",
            {"name": "new_name"},
            None,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            "existing_pokemon",
            {"published": "new_name"},
            None,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            "existing_pokemon",
            {"name": "new_name", "published": False},
            None,
            HTTPStatus.OK,
        ),
        (
            "not_existing_pokemon",
            {"name": "new_name"},
            None,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            "not_existing_pokemon",
            {"published": "new_name"},
            None,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            "not_existing_pokemon",
            {"name": "new_name", "published": False},
            None,
            HTTPStatus.NOT_MODIFIED,
        ),
        (
            "not_existing_pokemon",
            {"name": "new_name", "published": False},
            False,
            HTTPStatus.NOT_MODIFIED,
        ),
        (
            "not_existing_pokemon",
            {"name": "new_name", "published": False},
            True,
            HTTPStatus.OK,
        ),
    ],
)
def test_put_pokemon(
    request,
    pokemon: str,
    new_body: dict,
    upsert: bool | None,
    status_code: int,
) -> None:
    entity: PokemonEntity = request.getfixturevalue(pokemon)
    response = client.put(
        f"/pokemon/{entity.id}",
        params={"upsert": upsert} if upsert is not None else None,
        json=new_body,
    )

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        assert response.json() == {"id": entity.id, **new_body}

        response = client.get(f"/pokemon/{entity.id}")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"id": entity.id, **new_body}


def test_post_pokemon(pokemon_info: PokemonInfo) -> None:
    response = client.post("/pokemon", json=asdict(pokemon_info))

    assert response.status_code == HTTPStatus.CREATED
    assert "location" in response.headers
    response_data = response.json()
    id = response_data.pop("id")

    assert response_data == asdict(pokemon_info)

    response = client.get(f"/pokemon/{id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": id, **asdict(pokemon_info)}


@pytest.mark.parametrize(
    ("pokemon", "data", "status_code"),
    [
        ("existing_pokemon", {}, HTTPStatus.OK),
        ("existing_pokemon", {"name": "new_name"}, HTTPStatus.OK),
        ("existing_pokemon", {"published": True}, HTTPStatus.OK),
        ("existing_pokemon", {"some": False}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("not_existing_pokemon", {"some": False}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ("not_existing_pokemon", {"name": "new_name"}, HTTPStatus.NOT_MODIFIED),
    ],
)
def test_patch_pokemon(request, pokemon: str, data: dict, status_code: int) -> None:
    entity: PokemonEntity = request.getfixturevalue(pokemon)

    response = client.patch(
        f"/pokemon/{entity.id}",
        json=data,
    )

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        response_data = response.json()

        for key in ["name", "published"]:
            if key in data:
                assert response_data[key] == data[key]
