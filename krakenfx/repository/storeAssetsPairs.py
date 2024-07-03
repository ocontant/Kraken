# krakenfx/scripts/storeAssetsPairs.py

import pdb
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from krakenfx.utils.errors import *
from krakenfx.utils.utils import *
from krakenfx.api.schemas.assetsPairsSchemas import (
    SchemasAssetPairDetails,
    SchemasCollateralAssetDetails,
    SchemasFeeSchedule,
    SchemasResponse
)
from krakenfx.api.models.assetsPairsModel import ModelAssetsPairs
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@handle_errors
async def process_asset_pairs(assetsPairs: json, session: AsyncSession):
    logger.info("Processing asset pairs.")

    for asset_name, asset_data in assetsPairs.items():
        #logger.trace("L> Variable: process_asset_pairs(_ForLoop).asset_data:\n{}".format(json.dumps(asset_data, indent=4, default=str)))
        await store_asset_pair(asset_name, asset_data, session)

    logger.flow1("Completed processing asset pairs.")
    logger.info("Adding asset pairs to database.")
    await session.commit()

async def store_asset_pair(asset_name: str, asset_data: json, session: AsyncSession):
    logger.flow1(f"Processing Asset ID: {asset_name}")

    resultAssetPair = await session.execute(select(ModelAssetsPairs).where(ModelAssetsPairs.pair_name == asset_name))
    orm_asset_pair = resultAssetPair.scalar_one_or_none()

    if orm_asset_pair:
        logger.flow2(f"Asset Pair ID {asset_name} found. Updating asset pair.")           
        orm_asset_pair.data = asset_data
    else:
        logger.flow2(f"Asset Pair ID {asset_name} not found. Creating new asset pair.")
        new_asset_pair = ModelAssetsPairs(pair_name=asset_name, data=asset_data)
        session.add(new_asset_pair)

    await session.flush()
    logger.flow1(f"L-> Finished processing Asset Pair ID {asset_name}.")

if __name__ == "__main__":
    print("This script cannot be invoked directly!")
