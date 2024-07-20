import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from krakenfx.repository.models.assetsPairsModel import ModelAssetsPairs
from krakenfx.repository.models.ohlcModel import ModelOHLCAssetPair, ModelOHLCData
from krakenfx.utils.database import Base
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
)
from krakenfx.utils.logger import setup_main_logging

logger = setup_main_logging()


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


async def display_data_model(asset_pair_id: int, session: AsyncSession):
    # Display data from the order table
    results = await session.execute(text("SELECT * FROM ohlc_data"))
    rows = results.fetchall()
    logger.trace(f"\n\n\nOHLC Data in DB: {rows}\n\n\n")


# The test case
@pytest.mark.asyncio
async def test_ohlc_data(db_session):
    try:
        # Create an asset pair
        asset_pair = ModelAssetsPairs(pair_name="XBTUSD", data={})
        db_session.add(asset_pair)
        await db_session.commit()

        # Create an OHLC asset pair
        ohlc_asset_pair = ModelOHLCAssetPair(name="XBTUSD")
        db_session.add(ohlc_asset_pair)
        await db_session.commit()

        # Get the OHLC asset pair ID
        ohlc_asset_pair_id = ohlc_asset_pair.id

        # Add OHLC data
        ohlc_data = [
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381095240,
                open=122.0,
                high=122.0,
                low=122.0,
                close=122.0,
                vwap=122.0,
                volume=0.1,
                count=1,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381179000,
                open=123.61,
                high=123.61,
                low=123.61,
                close=123.61,
                vwap=123.61,
                volume=0.1,
                count=1,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381201080,
                open=123.91,
                high=123.91,
                low=123.9,
                close=123.9,
                vwap=123.9,
                volume=1.9916,
                count=2,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381209960,
                open=124.19,
                high=124.19,
                low=124.18,
                close=124.18,
                vwap=124.18,
                volume=2,
                count=2,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381311000,
                open=124.01687,
                high=124.01687,
                low=124.01687,
                close=124.01687,
                vwap=124.01687,
                volume=1,
                count=1,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381311060,
                open=124.01687,
                high=124.01687,
                low=123.84,
                close=123.84,
                vwap=123.84,
                volume=1.823,
                count=2,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381431780,
                open=125.85,
                high=125.86,
                low=125.85,
                close=125.86,
                vwap=125.86,
                volume=2,
                count=2,
            ),
            ModelOHLCData(
                asset_pair_id=ohlc_asset_pair_id,
                time=1381571220,
                open=127.5,
                high=127.5,
                low=127.0,
                close=127.0,
                vwap=127.0,
                volume=4,
                count=3,
            ),
        ]

        db_session.add_all(ohlc_data)
        await db_session.commit()

        await display_data_model(ohlc_asset_pair_id, db_session)

        # Query the data
        query_result = await db_session.execute(
            select(ModelOHLCData).where(
                ModelOHLCData.asset_pair_id == ohlc_asset_pair_id
            )
        )
        orm_ohlc_data = query_result.scalars().all()

        assert len(orm_ohlc_data) == 8

        expected_results = [
            (1381095240, 122.0, 122.0, 122.0, 122.0, 122.0, 0.1, 1),
            (1381179000, 123.61, 123.61, 123.61, 123.61, 123.61, 0.1, 1),
            (1381201080, 123.91, 123.91, 123.9, 123.9, 123.9, 1.9916, 2),
            (1381209960, 124.19, 124.19, 124.18, 124.18, 124.18, 2, 2),
            (1381311000, 124.01687, 124.01687, 124.01687, 124.01687, 124.01687, 1, 1),
            (1381311060, 124.01687, 124.01687, 123.84, 123.84, 123.84, 1.823, 2),
            (1381431780, 125.85, 125.86, 125.85, 125.86, 125.86, 2, 2),
            (1381571220, 127.5, 127.5, 127.0, 127.0, 127.0, 4, 3),
        ]

        for i, record in enumerate(orm_ohlc_data):
            assert (
                record.time,
                record.open,
                record.high,
                record.low,
                record.close,
                record.vwap,
                record.volume,
                record.count,
            ) == expected_results[i]

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
    except KrakenNoOrdersException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))


if __name__ == "__main__":
    pytest.main()
