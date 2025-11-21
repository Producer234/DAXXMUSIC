import sys
import asyncio
import traceback

from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from ..logging import LOGGER


class DAXX(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        # Validate configuration
        if not all([config.API_ID, config.API_HASH, config.BOT_TOKEN, config.LOGGER_ID]):
            LOGGER(__name__).error("Missing one or more required config values!")
            sys.exit(1)

        super().__init__(
            name="DAXXMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        self.id = self.me.id
        self.name = f"{self.me.first_name} {self.me.last_name or ''}"
        self.username = self.me.username
        self.mention = self.me.mention

        # Retry logic for sending log message
        for attempt in range(3):
            try:
                await self.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                        f"ɪᴅ : <code>{self.id}</code>\n"
                        f"ɴᴀᴍᴇ : {self.name}\n"
                        f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                    ),
                )
                break  # success
            except (errors.ChannelInvalid, errors.PeerIdInvalid):
                LOGGER(__name__).error(
                    "Bot cannot access the log group/channel. "
                    "Ensure the bot is added to the channel."
                )
                if attempt == 2:
                    LOGGER(__name__).warning("Skipping log message due to repeated failure.")
            except Exception as ex:
                LOGGER(__name__).error(
                    f"Failed to send log message. Attempt {attempt + 1}/3\n"
                    f"Reason: {type(ex).__name__}\n{traceback.format_exc()}"
                )
                await asyncio.sleep(3)

        # Check admin rights in log channel
        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).warning(
                    "Bot is not an admin in the log group/channel. Promote it to admin."
                )
        except Exception as ex:
            LOGGER(__name__).warning(
                f"Failed to verify admin status in log channel.\n{traceback.format_exc()}"
            )

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info("Music Bot Stopped Successfully")