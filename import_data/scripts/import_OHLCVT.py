import argparse
import asyncio
import csv
import logging
import os
import time
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from krakenfx.repository.models.assetsPairsModel import ModelAssetsPairs
from krakenfx.repository.models.ohlcModel import ModelOHLCData
from krakenfx.utils.database import (
    get_async_postgresql_session,
    get_async_sqlite_session,
)
from krakenfx.utils.logger import setup_custom_logging, setup_main_logging
from krakenfx.utils.user_utils import ask_user_yn

from .common.error_manager import ErrorManager

# Determine the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data", "Kraken_OHLCVT")
LOG_DIR = os.path.join(ROOT_DIR, "import_logs")
os.makedirs(LOG_DIR, exist_ok=True)

current_date = datetime.now().strftime("%Y%m%d")

# Setup global loggers
execution_logger = setup_main_logging()
# Create a global ErrorManager instance
global_error_manager = ErrorManager({"execution": execution_logger})


async def list_asset_pairs():
    """List all asset pairs available in the database."""
    async with get_async_postgresql_session() as session:
        result = await session.execute(select(ModelAssetsPairs))
        asset_pairs = result.scalars().all()
        for asset_pair in asset_pairs:
            print(asset_pair.pair_name)


async def display_mock_data(csv_file_path: str, chunk_size: int = 20):
    """Display a preview of the data chunks from the CSV file."""
    with open(csv_file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for chunk in get_chunks(reader, chunk_size):
            execution_logger.info("\n\nChunk data preview:\n")
            for row in chunk:
                execution_logger.info(f"{row}")
            continue


def get_chunks(reader, chunk_size: int = 1000):
    """Generator function to yield chunks of data from the CSV reader."""
    chunk = []
    for row in reader:
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
        chunk.append(row)
    if chunk:
        yield chunk


async def validate_data(
    session: AsyncSession, ohlc_data_list, error_manager: ErrorManager
):
    """Validate the imported OHLC data."""
    fail_validation_count = 0
    failed_rows = []
    for data in ohlc_data_list:
        query_result = await session.execute(
            select(ModelOHLCData).where(ModelOHLCData.time == data.time)
        )
        record = query_result.scalar_one_or_none()
        if not record or (
            record.open,
            record.high,
            record.low,
            record.close,
            record.volume,
            record.count,
        ) != (data.open, data.high, data.low, data.close, data.volume, data.count):
            fail_validation_count += 1
            failed_rows.append(data)

    if fail_validation_count > 0:
        error_manager.log_warning(
            "validation_errors", f"{fail_validation_count} rows failed validation."
        )
        error_manager.log_warning(
            "validation_errors", [f"{row}" for row in failed_rows]
        )
        return False
    return True


def deduce_asset_pair_name(file_name):
    """Deduce the asset pair name from the CSV file name."""
    try:
        asset_pair_name = file_name.split("_")[0]
        return asset_pair_name
    except IndexError:
        global_error_manager.log_error(
            "file_errors",
            f"Failed to deduce asset pair name from file name: {file_name}.",
        )
        return None


async def import_files_in_directory(
    directory: str, chunk_size=1000, interactive=False, validate=False
):
    """Import OHLC data from all CSV files in a directory."""
    for file_name in os.listdir(directory):
        if file_name.endswith(".csv"):
            asset_pair_name = deduce_asset_pair_name(file_name)
            if not asset_pair_name:
                global_error_manager.log_error(
                    "import", f"Unable to deduce asset pair from filename: {file_name}"
                )
                continue

            status = await import_ohlc_data_from_csv(
                os.path.join(directory, file_name),
                asset_pair_name,
                chunk_size,
                interactive,
                validate,
            )

            if status == "Succeed with warnings":
                global_error_manager.log_warning(
                    "import_warnings",
                    f"Import {file_name} with status: {status}.",
                )
            elif status == "Failed":
                global_error_manager.log_error(
                    "import_errors", f"Import {file_name} with status: {status}."
                )
            elif status == "Success":
                global_error_manager.log_info(
                    f"Import {file_name} with status: {status}"
                )


async def import_ohlc_data_from_csv(
    csv_file_path: str,
    asset_pair_name: str,
    chunk_size=1000,
    interactive=False,
    validate=False,
):
    """Import OHLC data from a single CSV file."""
    error_manager = ErrorManager()

    audit_log_name = (
        f"{current_date}_audit_{os.path.basename(csv_file_path).split('.')[0]}.log"
    )
    audit_logger = setup_custom_logging(audit_log_name, LOG_DIR, noscreen=True)
    error_manager.add_logger("audit", audit_logger)

    error_manager.log_info(
        f"\n\nStarting import for asset pair {asset_pair_name} from file {csv_file_path}\n\n",
    )
    global_error_manager.log_info(
        f"\n\nImporting {csv_file_path} with asset pair {asset_pair_name}\n\n"
    )

    async with get_async_postgresql_session() as session:

        asset_pair = await session.execute(
            select(ModelAssetsPairs).where(
                ModelAssetsPairs.pair_name == asset_pair_name
            )
        )
        asset_pair = asset_pair.scalar_one_or_none()

        if not asset_pair:
            error_manager.log_error(
                "execution_errors",
                f"Asset pair {asset_pair_name} does not exist in the database. Aborting ...",
            )
            global_error_manager.log_error(
                "execution_errors",
                f"Asset pair {asset_pair_name} does not exist in the database. Aborting ...",
            )
            return "Failed"

        with open(csv_file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for chunk in get_chunks(reader, chunk_size):
                ohlc_data_list = []
                for row in chunk:
                    ohlc_data = ModelOHLCData(
                        asset_pair_id=asset_pair.id,
                        time=int(row[0]),
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        vwap=0.0,  # Set to 0.0 if not provided
                        volume=float(row[5]),
                        count=int(row[6]),
                    )
                    ohlc_data_list.append(ohlc_data)

                if interactive:
                    global_error_manager.log_info(
                        f"Chunk data for asset pair {asset_pair_name}:\n {ohlc_data_list}"
                    )
                    if not ask_user_yn():
                        error_manager.log_error(
                            "user_abort",
                            f"Import pair {asset_pair_name} aborted by user.",
                        )
                        global_error_manager.log_error(
                            "user_abort",
                            f"Import pair {asset_pair_name} aborted by user.",
                        )
                        return "Aborted"

                try:
                    session.add_all(ohlc_data_list)
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    error_manager.log_warning(
                        "duplicate_errors",
                        f"Duplicate entries found in {csv_file_path} asset pair {asset_pair_name}. Duplicates Ignored...",
                    )
                    global_error_manager.log_warning(
                        "duplicate_errors",
                        f"Duplicate entries found in {csv_file_path} asset pair {asset_pair_name}. Duplicates Ignored...",
                    )

                if validate:
                    if not await validate_data(session, ohlc_data_list, error_manager):
                        await session.rollback()
                    else:
                        success_message = f"Chunk successfully validated: {chunk}"
                        error_manager.log_info(f"{success_message}")
                        global_error_manager.log_info(f"{success_message}")

        # Before destroying object, we need to collect all errors in global_error_manager
        error_manager.close()

    if error_manager.error_counter["execution_errors"] > 0:
        return "Failed"
    elif error_manager.error_counter["validation_errors"] > 0:
        return "Succeed with warnings"
    else:
        return "Succeed"


def setup_argparse():
    """Setup argument parser for command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Import OHLC data from CSV to database."
    )
    parser.add_argument("-a", "--assetpair", type=str, help="Asset pair name")
    parser.add_argument("-f", "--file", type=str, help="Path to the CSV file")
    parser.add_argument(
        "-d", "--directory", type=str, help="Path to the directory containing CSV files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making any database changes",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive mode to validate before importing",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="List all asset pairs available"
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store_true",
        help="Increase output verbosity: -v for DEBUG",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically answer yes to all prompts",
    )
    return parser


def main():
    """Main function to execute the script."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Start Logging
    global_error_manager.log_info(f"Starting import OHLCVT data from {args.file}.")
    global_error_manager.log_info(
        f"Started at: {time.strftime('%H:%M:%S', time.gmtime(global_error_manager.started_time))}"
    )

    if args.verbosity:
        execution_logger.setLevel(logging.DEBUG)

    # Select the database session based on the dry-run argument
    if args.dry_run:
        session_maker = get_async_sqlite_session("sqlite+aiosqlite:///./test.db")
    else:
        session_maker = get_async_postgresql_session()

    session = asyncio.run(session_maker)

    if args.list:
        asyncio.run(list_asset_pairs())
        return

    if args.file:
        if not args.assetpair:
            args.assetpair = deduce_asset_pair_name(os.path.basename(args.file))
            if not args.assetpair:
                execution_logger.error(
                    "Asset pair name could not be deduced from file name."
                )
                return

        if args.interactive:
            asyncio.run(display_mock_data(args.file))
            if not args.yes:
                if not ask_user_yn():
                    execution_logger.info("Import aborted by user.")
                    return

        asyncio.run(
            import_ohlc_data_from_csv(
                session,
                args.file,
                args.assetpair,
                interactive=args.interactive,
                validate=True,
            )
        )

    elif args.directory:
        asyncio.run(
            import_files_in_directory(
                args.directory, interactive=args.interactive, validate=True
            )
        )

    else:
        parser.print_help()

    # Print and log the summary
    summary_logger = setup_custom_logging(
        f"{current_date}_summary_import_OHLCVT.log", LOG_DIR, noscreen=True
    )
    global_error_manager.add_logger(summary_logger)
    global_error_manager.print_summary()


if __name__ == "__main__":
    main()
