def GetChannelId():
    return "-1001964265048"
def GetTotalMembers():
        channel_id = GetChannelId()
        response = bot.get_chat_members_count(channel_id)
        total_members = response - 1