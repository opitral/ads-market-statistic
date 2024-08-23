import asyncio
import logging

from logging_config import setup_logging
from statistic import Statistic
from config_reader import config


setup_logging()
logger = logging.getLogger()


async def main():
    statistic = Statistic(config.API_ID, config.API_HASH, config.GENERAL_CHANNEL_TELEGRAM_ID)

    await statistic.start_bot()
    await statistic.get_dialogs()
    await statistic.get_messages()

    try:
        groups = statistic.get_groups()

        for group in groups:
            posts = statistic.get_posts(group.get("telegram_id"))
            views = []

            for post in posts:
                views.append(await statistic.get_post_views(post))

            average_post_views = int(sum(views) / len(views))
            logger.info(f"Average post views in group {group.get('telegram_id')}: {average_post_views} views")

            statistic.set_average_post_views(group.get("id"), average_post_views)

    finally:
        await statistic.stop_bot()


if __name__ == "__main__":
    asyncio.run(main())
