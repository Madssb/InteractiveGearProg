"""Shared report logging helpers."""
import logging

import discord


logger = logging.getLogger(__name__)
REPORT_PING_ROLE_ID = 1506719382213099610


async def send_report_log(
    client: discord.Client,
    report_logs_channel_id: int,
    embed: discord.Embed,
) -> bool:
    channel = client.get_channel(report_logs_channel_id)
    if channel is None:
        logger.warning(
            "report logs channel not cached; fetching channel_id=%s",
            report_logs_channel_id,
        )
        try:
            channel = await client.fetch_channel(report_logs_channel_id)
        except discord.DiscordException:
            logger.exception(
                "failed to fetch report logs channel_id=%s",
                report_logs_channel_id,
            )
            return False

    if not isinstance(channel, discord.abc.Messageable):
        logger.error(
            "report logs channel is not messageable channel_id=%s",
            report_logs_channel_id,
        )
        return False

    try:
        await channel.send(
            content=f"<@&{REPORT_PING_ROLE_ID}>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=False,
                roles=True,
            ),
        )
    except discord.DiscordException:
        logger.exception(
            "failed to send report log channel_id=%s",
            report_logs_channel_id,
        )
        return False

    return True
