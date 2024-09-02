import datetime
import json
import logging
import requests

from pyrogram import Client

from logging_config import setup_logging
from enums import Endpoint, PostStatus


setup_logging()
logger = logging.getLogger()


class Statistic:
    def __init__(self, api_id, api_hash, general_channel_telegram_id, name="statistic"):
        self.GENERAL_CHANNEL_TELEGRAM_ID = general_channel_telegram_id
        self.bot = Client(name, api_id, api_hash)

    async def start_bot(self):
        await self.bot.start()

    async def stop_bot(self):
        await self.bot.stop()

    async def get_dialogs(self):
        async for dialog in self.bot.get_dialogs():
            logger.debug(f"Got peer id from dialog: {dialog.chat.id}")

    async def get_messages(self):
        async for message in self.bot.get_chat_history(self.GENERAL_CHANNEL_TELEGRAM_ID):
            logger.debug(f"Got peer id from message: {message.id}")

    @staticmethod
    def get_full_groups():
        response = requests.get(Endpoint.GROUP.value)
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                if result.get("total") > 0:
                    logger.info(f"Found {result.get('total')} groups")
                    return result.get("responseList")

                else:
                    logger.debug(f"No groups found")

            elif error:
                logger.error(f"Get groups request failed with error: {error}")

        else:
            logger.error(f"Get groups request failed with status code: {response.status_code}, error: {error}")

        return []

    @staticmethod
    def format_groups(groups: list):
        if not groups:
            return

        formatted_groups = []

        for group in groups:
            formatted_groups.append({
                "id": group.get("id"),
                "telegram_id": group.get("groupTelegramId")
            })

        logger.debug(f"Found {len(formatted_groups)} groups telegram id")
        return formatted_groups

    def get_groups(self):
        full_groups = self.get_full_groups()
        groups_telegram_ids = self.format_groups(full_groups)
        return groups_telegram_ids

    @staticmethod
    def get_full_posts(group_telegram_id: int, date: datetime.date):
        restrict = {
            "groupTelegramId": group_telegram_id,
            "status": PostStatus.PUBLISHED.value,
            "publishDate": date.strftime("%Y-%m-%d")
        }

        response = requests.get(Endpoint.POST.value, params={"restrict": json.dumps(restrict)})
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                if result.get("total") > 0:
                    logger.info(f"Found {result.get('total')} posts for group telegram id {group_telegram_id}")
                    return result.get("responseList")

                else:
                    logger.debug(f"No posts found for group telegram id {group_telegram_id}")

            elif error:
                logger.error(f"Get posts request failed with error: {error}")

        else:
            logger.error(f"Get posts request failed with status code: {response.status_code}, error: {error}")

        return []

    @staticmethod
    def get_posts_message_ids(posts: list):
        if not posts:
            return

        posts_message_ids = []

        for post in posts:
            posts_message_ids.append(post.get("messageId"))

        logger.debug(f"Found {len(posts_message_ids)} posts message ids")
        return posts_message_ids

    def get_posts(self, group_id: int):
        full_posts = []
        today_date = datetime.date.today()
        for i in range(1, 31):
            date = today_date - datetime.timedelta(days=i)
            full_posts.extend(self.get_full_posts(group_id, date))
        posts_message_ids = self.get_posts_message_ids(full_posts)
        return posts_message_ids

    async def get_post_views(self, message_id: int):
        message = await self.bot.get_messages(self.GENERAL_CHANNEL_TELEGRAM_ID, message_id)
        logger.info(f"Got message with {message.views} views")
        return message.views

    @staticmethod
    def set_average_post_views(group_id: int, views: int):
        body = {
            "id": group_id,
            "averagePostViews": views
        }

        response = requests.put(f"{Endpoint.GROUP.value}", json=body)
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                logger.info(f"Group with id {group_id} has been set average post views as {views}")
                return result

            elif error:
                logger.error(f"Update group average post views request failed with error: {error}")

        else:
            logger.error(f"Update group average post views request request failed"
                         f"with status code: {response.status_code}, error: {error}")
