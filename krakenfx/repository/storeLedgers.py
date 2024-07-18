# krakenfx/scripts/fetch_ledgers.py
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from krakenfx.repository.models.ledgerModel import ModelLedger as ORMLedger
from krakenfx.services.account_data.schemas.ledgerSchemas import (
    SchemasLedger,
    SchemasLedgers,
)
from krakenfx.utils.errors import async_handle_errors
from krakenfx.utils.logger import setup_main_logging
from krakenfx.utils.utils import object_as_dict

logger = setup_main_logging()


@async_handle_errors
async def process_ledgers(Ledgers: SchemasLedgers, session: AsyncSession):
    logger.info("Processing ledgers.")

    logger.trace(
        "L> Variable: process_ledgers(_ForLoop).Ledgers:\n{}".format(
            json.dumps(Ledgers, indent=4, default=str)
        )
    )

    # Iterate all Ledgers
    for ledger_id, ledger in Ledgers.items():
        logger.trace(
            "L> Variable: process_ledgers(_ForLoop).Ledger:\n{}".format(
                json.dumps(ledger.model_dump(), indent=4, default=str)
            )
        )
        await store_ledger(ledger_id, ledger, session)

    logger.flow1("Completed last ledger.")
    # Commit the session after processing all orders
    logger.info("Adding Ledgers to database.")
    await session.commit()


@async_handle_errors
async def store_ledger(ledger_id: str, ledger: SchemasLedger, session: AsyncSession):
    logger.flow1(f"Processing Ledger ID: {ledger_id}")

    # Check if the order exists
    resultLedger = await session.execute(
        select(ORMLedger).where(ORMLedger.id == ledger_id)
    )
    orm_ledger = resultLedger.scalar_one_or_none()

    if orm_ledger:
        logger.flow2(f"Ledger ID {ledger_id} found. Updating ledger.")

        ledger_dict = ledger.model_dump()
        for key, value in ledger_dict.items():
            if getattr(orm_ledger, key) != value:
                setattr(orm_ledger, key, value)
                logger.trace(
                    f"L-> Ledger ID {ledger_id} - Field {key} updated to {value}"
                )

        logger.flow2(f"Ledger ID {ledger_id} updated.")
    else:
        logger.flow2(f"Ledger ID {ledger_id} not found. Creating new order.")

        # - Add order to session
        orm_ledger: ORMLedger = await create_orm_ledger(ledger_id, ledger)
        logger.trace(
            "L-> Variable: process_orders().orm_ledger:\n{}".format(
                json.dumps(object_as_dict(orm_ledger), indent=4, default=str)
            )
        )
        logger.trace(
            f"Table name of {orm_ledger.__class__.__name__}: {orm_ledger.__tablename__}"
        )
        logger.flow2(f"L-> Adding Ledger ID {orm_ledger.id} to session.")

        logger.flow2(f"Ledger ID {ledger_id} created.")

        session.add(orm_ledger)

    await session.flush()
    logger.flow1(f"L-> Finished processing ledger ID {ledger_id}.")


@async_handle_errors
async def create_orm_ledger(ledger_id: str, ledger: SchemasLedger) -> ORMLedger:
    logger.flow2(f"L--> Create instance of ORM model ORMLedger for {ledger_id}.")
    ledger_dict = ledger.model_dump(exclude_unset=True)

    orm_ledger = ORMLedger(id=ledger_id, **ledger_dict)
    return orm_ledger


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
