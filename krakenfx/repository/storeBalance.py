import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from krakenfx.repository.models.balanceModel import ModelBalance as ORMBalance
from krakenfx.services.account_data.schemas.balanceSchemas import SchemasAccountBalance
from krakenfx.utils.errors import async_handle_errors
from krakenfx.utils.logger import setup_main_logging

logger = setup_main_logging()


@async_handle_errors
async def process_balance(Balances: SchemasAccountBalance, session: AsyncSession):
    logger.info("Processing Balance")

    logger.trace(
        "L> Variable: process_balance(_ForLoop).Balances:\n{}".format(
            json.dumps(Balances.model_dump(), indent=4)
        )
    )
    for asset, amount in Balances.root.items():
        logger.trace("L> Variable: process_balance(_ForLoop): {asset}:{amount}")
        await store_balance(asset, amount, session)

    logger.flow1("Completed processing the last asset in Balances.")
    logger.info("Adding Balances to database.")
    await session.commit()


async def store_balance(asset: str, amount: str, session: AsyncSession):
    logger.flow1(f"Processing Balance Asset: {asset}")

    # Check if the asset exists
    result = await session.execute(select(ORMBalance).where(ORMBalance.asset == asset))
    orm_balance = result.scalar_one_or_none()

    if orm_balance:
        if getattr(orm_balance, amount) != amount:
            setattr(orm_balance, amount, amount)
            logger.trace(f"L-> Balance Asset {asset} updated to {amount}")
        logger.flow2(f"Updated Balance: {orm_balance}")
    else:
        orm_balance = ORMBalance(asset=asset, amount=amount)
        session.add(orm_balance)
        logger.flow2(f"Created Balance: {orm_balance}")


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
