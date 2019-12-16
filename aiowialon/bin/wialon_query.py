import asyncio
import argparse
import logging
import os
import pprint
import yaml
from aiowialon import connect

ACCESS_TOKEN_VAR = "WIALON_ACCESS_TOKEN"


# pylint: disable=missing-function-docstring


def configure_logger(debug_level: bool):
    level = logging.DEBUG if debug_level else logging.WARNING
    logger = logging.getLogger("aiowialon")
    if logger.level > level:
        logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)


def get_access_token():
    # TODO: Implement authentication with MechanicalSoup (see tests)
    return os.environ[ACCESS_TOKEN_VAR]


async def main_task(filepath: str, verbose: bool):
    configure_logger(verbose)
    config = yaml.safe_load(filepath)
    print("\n*** REQUEST ***\n")
    pprint.pprint(config)
    result = await request(access_token=get_access_token(), **config)
    print("\n*** RESULT ***\n")
    pprint.pprint(result)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(description="Send Wialon Remote API Request")
    parser.add_argument(
        "filepath", type=argparse.FileType("r"), help="Config YAML file path"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    return vars(args)


async def request(access_token: str, svc: str, params: dict = None):
    params = params or {}
    async with connect(access_token) as session:
        return await session.call(svc, params)


def main():
    asyncio.run(main_task(**parse_args()))


if __name__ == "__main__":
    main()
