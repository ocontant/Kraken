import pytest_asyncio
import pytest
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.api.schemas.assetsPairsSchemas import (
    SchemasResponse,
    SchemasFeeSchedule,
    SchemasAssetPairDetails,
    SchemasCollateralAssetDetails
)
from krakenfx.api.models.assetsPairsModel import (
    ModelFeeSchedule as ORMFeeSchedule,
    ModelAssetPairDetails as ORMAssetPairDetails,
    ModelCollateralAssetDetails as ORMCollateralAssetDetails
)
from krakenfx.services.spot_market_data.getAssetsPairsService import get_AssetsPairs
from krakenfx.repository.storeAssetsPairs import process_asset_pairs
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@pytest_asyncio.fixture(scope='function')
async def engine():
    return create_async_engine('sqlite+aiosqlite:///:memory:', future=True, echo=True)

@pytest_asyncio.fixture(scope='function', autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope='function')
async def db_session(engine):
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def display_data_model(session):
    # Display data from the asset pair table
    results = await session.execute(text('SELECT * FROM model_asset_pair_details'))
    rows = results.fetchall()
    logger.trace(f"Asset Pairs in DB: {rows}")

    # Display data from the collateral asset table
    results = await session.execute(text('SELECT * FROM model_collateral_asset_details'))
    rows = results.fetchall()
    logger.trace(f"Collateral Assets in DB: {rows}")

# The test case
@pytest.mark.asyncio
async def test_assetPairsService_orm_preparation(db_session):
    try:
        logger.flow1("Starting Test")

        asset_pair_data = {
            "XXBTZUSD": {
                "altname": "XBTUSD",
                "wsname": "XBT/USD",
                "aclass_base": "currency",
                "base": "XXBT",
                "aclass_quote": "currency",
                "quote": "ZUSD",
                "lot": "unit",
                "cost_decimals": 2,
                "pair_decimals": 5,
                "lot_decimals": 8,
                "lot_multiplier": 1,
                "leverage_buy": [2, 3, 4, 5],
                "leverage_sell": [2, 3, 4, 5],
                "fees": [[0, 0.26], [50000, 0.24], [100000, 0.22]],
                "fees_maker": [[0, 0.16], [50000, 0.14], [100000, 0.12]],
                "fee_volume_currency": "ZUSD",
                "margin_call": 80,
                "margin_stop": 40,
                "ordermin": "0.001",
                "costmin": "0.01",
                "tick_size": "0.0001",
                "status": "online",
                "long_position_limit": 500,
                "short_position_limit": 500
            },
            "ZUSD": {
                "aclass": "currency",
                "altname": "USD",
                "decimals": 4,
                "display_decimals": 2,
                "collateral_value": 1.0,
                "status": "enabled"
            }
        }

        #assetsPairs: SchemasResponse = await get_AssetsPairs()

        await process_asset_pairs(asset_pair_data, db_session)
        await display_data_model(db_session)

        # Fetch the result using the AssetPairDetails model
        result = await db_session.execute(select(ORMAssetPairDetails).where(ORMAssetPairDetails.id == "XXBTZUSD"))
        orm_asset_pair = result.scalar_one_or_none()
        if orm_asset_pair is None:
            pytest.fail("No result found in the table asset pairs for id 'XXBTZUSD'")

        # Fetch the result using the CollateralAssetDetails model
        result = await db_session.execute(select(ORMCollateralAssetDetails).where(ORMCollateralAssetDetails.id == "ZUSD"))
        orm_collateral_asset = result.scalar_one_or_none()
        if orm_collateral_asset is None:
            pytest.fail("No result found in the table collateral assets for id 'ZUSD'")

    except TimeoutError as e:
        pytest.fail(str(e))
    except RuntimeError as e:
        pytest.fail(str(e))
    except ConnectionError as e:
        pytest.fail(str(e))
    except InvalidAPIKeyException as e:
        pytest.fail(str(e))
    except FetchResponseException as e:
        pytest.fail(str(e))
    except InvalidResponseStructureException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
