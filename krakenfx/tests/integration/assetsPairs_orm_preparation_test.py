import json
import logging

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from krakenfx.repository.models.assetsPairsModel import (
    ModelAssetsPairs as ORMAssetsPairs,
)
from krakenfx.repository.storeAssetsPairs import process_asset_pairs
from krakenfx.services.spot_market_data.getAssetsPairsService import (
    get_AssetsPairs,
    get_AssetsPairs_from_database,
)
from krakenfx.services.spot_market_data.schemas.assetsPairsSchemas import (
    SchemasResponse,
)
from krakenfx.utils.database import Base
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
)
from krakenfx.utils.logger import setup_main_logging
from krakenfx.utils.utils import truncated_output

logger = setup_main_logging()
logging.getLogger("aiosqlite").setLevel(logging.WARNING)


@pytest_asyncio.fixture(scope="function")
async def engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:", future=True, echo=True)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


async def display_data_model(session: AsyncSession):
    # Display data from the asset pair table
    results = await session.execute(text("SELECT * FROM assets_pairs"))
    assets_pairs_data = results.fetchall()

    # Convert SQLAlchemy Row objects to dictionaries and parse JSON data
    assets_pairs_data_dicts = []
    for row in assets_pairs_data:
        row_dict = dict(row._mapping)
        row_dict["data"] = json.loads(
            row_dict["data"]
        )  # Parse the JSON string to a dictionary
        assets_pairs_data_dicts.append(row_dict)

    # Convert to JSON formatted string
    truncated_json_data = await truncated_output(
        json.dumps(assets_pairs_data_dicts, indent=4, default=str), 100
    )

    # Log the truncated JSON formatted data
    logger.trace("Asset Pairs in DB:")
    logger.trace(truncated_json_data)


# The test case
@pytest.mark.asyncio
async def test_assetPairsService_orm_preparation(db_session):
    try:
        logger.flow1("Starting Test")

        assetsPairs: SchemasResponse = await get_AssetsPairs()
        await process_asset_pairs(assetsPairs, db_session)
        await display_data_model(db_session)

        # Fetch the result using the AssetPairDetails model
        result = await db_session.execute(
            select(ORMAssetsPairs).where(ORMAssetsPairs.pair_name == "XXBTZUSD")
        )
        orm_asset_pair = result.scalar_one_or_none()
        if orm_asset_pair is None:
            pytest.fail("No result found in the table asset pairs for id 'XXBTZUSD'")

        result = await get_AssetsPairs_from_database(db_session)
        result_truncated = await truncated_output(
            json.dumps(result.model_dump(), indent=4, default=str), 100
        )
        logger.trace(result_truncated)

        if result is None:
            pytest.fail("No data return from get_AssetsPairs_from_database()")

    except TimeoutError as e:
        pytest.fail(str(e))
    except RuntimeError as e:
        pytest.fail(str(e))
    except ConnectionError as e:
        pytest.fail(str(e))
    except KrakenInvalidAPIKeyException as e:
        pytest.fail(str(e))
    except KrakenFetchResponseException as e:
        pytest.fail(str(e))
    except KrakenInvalidResponseStructureException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
