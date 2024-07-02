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
from krakenfx.api.models.assetsPairsModel import (
    ModelFeeSchedule as ORMFeeSchedule,
    ModelAssetPairDetails as ORMAssetPairDetails,
    ModelCollateralAssetDetails as ORMCollateralAssetDetails
)
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@handle_errors
async def process_asset_pairs(asset_pairs: dict, session: AsyncSession):
    logger.info("Processing asset pairs.")

    for asset_id, asset_data in asset_pairs.items():
        logger.trace("L> Variable: process_asset_pairs(_ForLoop).asset_data:\n{}".format(json.dumps(asset_data, indent=4, default=str)))
        await store_asset_pair(asset_id, asset_data, session)

    logger.flow1("Completed processing asset pairs.")
    logger.info("Adding asset pairs to database.")
    await session.commit()

async def store_asset_pair(asset_id: str, asset_data: dict, session: AsyncSession):
    logger.flow1(f"Processing Asset ID: {asset_id}")

    if 'aclass_base' in asset_data:
        asset_data['fees'] = [SchemasFeeSchedule.from_list(fee) for fee in asset_data['fees']]
        asset_data['fees_maker'] = [SchemasFeeSchedule.from_list(fee) for fee in asset_data['fees_maker']]
        asset_details = SchemasAssetPairDetails(**asset_data)
        logger.trace("L> Variable: process_asset_pairs(_ForLoop).asset_details:\n{}".format(json.dumps(asset_details.model_dump(), indent=4, default=str)))
        await store_asset_pair_details(asset_id, asset_details, session)
    elif 'aclass' in asset_data:
        collateral_details = SchemasCollateralAssetDetails(**asset_data)
        await store_collateral_asset_details(asset_id, collateral_details, session)

async def store_asset_pair_details(asset_id: str, asset_details: SchemasAssetPairDetails, session: AsyncSession):
    result = await session.execute(select(ORMAssetPairDetails).where(ORMAssetPairDetails.id == asset_id))
    orm_asset_pair = result.scalar_one_or_none()

    if orm_asset_pair:
        logger.flow2(f"Asset Pair ID {asset_id} found. Updating asset pair.")
        for key, value in asset_details.model_dump().items():
            if hasattr(orm_asset_pair, key) and getattr(orm_asset_pair, key) != value:
                setattr(orm_asset_pair, key, value)
                logger.trace(f"L-> Asset Pair ID {asset_id} - Field {key} updated to {value}")
    else:
        logger.flow2(f"Asset Pair ID {asset_id} not found. Creating new asset pair.")
        pdb.set_trace()
        orm_asset_pair_data = pydantic_to_sqlalchemy_model(asset_details)
        pdb.set_trace()
        orm_asset_pair = ORMAssetPairDetails(id=asset_id, **orm_asset_pair_data)
        pdb.set_trace()
        session.add(orm_asset_pair)

    await session.flush()
    logger.flow1(f"L-> Finished processing Asset Pair ID {asset_id}.")

async def store_collateral_asset_details(asset_id: str, collateral_details: SchemasCollateralAssetDetails, session: AsyncSession):
    result = await session.execute(select(ORMCollateralAssetDetails).where(ORMCollateralAssetDetails.id == asset_id))
    orm_collateral_asset = result.scalar_one_or_none()

    if orm_collateral_asset:
        logger.flow2(f"Collateral Asset ID {asset_id} found. Updating collateral asset.")
        for key, value in collateral_details.model_dump().items():
            if hasattr(orm_collateral_asset, key) and getattr(orm_collateral_asset, key) != value:
                setattr(orm_collateral_asset, key, value)
                logger.trace(f"L-> Collateral Asset ID {asset_id} - Field {key} updated to {value}")
    else:
        logger.flow2(f"Collateral Asset ID {asset_id} not found. Creating new collateral asset.")
        pdb.set_trace()
        orm_collateral_asset_data = pydantic_to_sqlalchemy_model(collateral_details)
        pdb.set_trace()
        orm_collateral_asset = ORMCollateralAssetDetails(id=asset_id, **orm_collateral_asset_data)
        pdb.set_trace()
        session.add(orm_collateral_asset)

    await session.flush()
    logger.flow1(f"L-> Finished processing Collateral Asset ID {asset_id}.")

""" async def create_orm_asset_pair(asset_id: str, asset_details: SchemasAssetPairDetails, session: AsyncSession) -> ORMAssetPairDetails:
    orm_asset_pair = ORMAssetPairDetails(id=asset_id)
    asset_details_dict = asset_details.model_dump()

    for key, value in asset_details_dict.items():
        if key in ['leverage_buy', 'leverage_sell']:
            value = ','.join(map(str, value))  # Convert list to comma-separated string
        if hasattr(orm_asset_pair, key):
            setattr(orm_asset_pair, key, value)

    # Add fees and fees_maker
    orm_fees = [ORMFeeSchedule(volume=fee.volume, fee=fee.fee) for fee in asset_details.fees]
    orm_fees_maker = [ORMFeeSchedule(volume=fee_maker.volume, fee=fee_maker.fee) for fee_maker in asset_details.fees_maker]
    
    for orm_fee in orm_fees:
        orm_asset_pair.fees.append(orm_fee)
        session.add(orm_fee)
    
    for orm_fee_maker in orm_fees_maker:
        orm_asset_pair.fees_maker.append(orm_fee_maker)
        session.add(orm_fee_maker)

    session.add_all(orm_fees + orm_fees_maker)
    return orm_asset_pair

async def create_orm_collateral_asset(asset_id: str, collateral_details: SchemasCollateralAssetDetails) -> ORMCollateralAssetDetails:
    orm_collateral_asset = ORMCollateralAssetDetails(id=asset_id)
    collateral_details_dict = collateral_details.model_dump()

    for key, value in collateral_details_dict.items():
        if hasattr(orm_collateral_asset, key):
            setattr(orm_collateral_asset, key, value)

    return orm_collateral_asset
 """
if __name__ == "__main__":
    print("This script cannot be invoked directly!")
