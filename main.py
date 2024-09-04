import asyncio
import logging
from datetime import datetime

from logging_config import setup_logging
from statistic import Statistic
from config_reader import config


setup_logging()
logger = logging.getLogger()


async def main():
    while True:
        date = datetime.now()
        if date.weekday() != 6 and False:
            logger.debug("It's not Sunday")
            await asyncio.sleep(60 * 60)

        logger.info("It's Sunday")
        statistic = Statistic(config.API_ID, config.API_HASH, config.GENERAL_CHANNEL_TELEGRAM_ID)

        await statistic.start_bot()
        await statistic.get_dialogs()
        await statistic.get_messages()

        try:
            try:
                groups = statistic.get_groups()

            except Exception as ex:
                logger.error(f"Failed to get groups: {ex}")
                return

            for group in groups:
                try:
                    posts = statistic.get_posts(group.get("telegram_id"))

                except Exception as ex:
                    logger.error(f"Error while getting posts for group {group.get('telegram_id')}: {ex}")
                    continue

                views = []
                for post in posts:
                    try:
                        views.append(await statistic.get_post_views(post))

                    except Exception as ex:
                        logger.error(f"Error while getting views for post {post.get('id')}: {ex}")

                average_post_views = int(sum(views) / len(views))
                logger.info(f"Average post views in group {group.get('telegram_id')}: {average_post_views} views")

                try:
                    statistic.set_average_post_views(group.get("id"), average_post_views)

                except Exception as ex:
                    logger.error(f"Error while setting average views for group {group.get('telegram_id')}: {ex}")

        except Exception as ex:
            logger.error(f"Error: {ex}")

        finally:
            await statistic.stop_bot()
            await asyncio.sleep(24 * 60 * 60)


if __name__ == "__main__":
    asyncio.run(main())
