from time import time
from asyncio import create_task, gather, sleep as asleep
from pyrogram.filters import command, user
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from pyrogram.enums import MessageEntityType
from pyrogram.errors import QueryIdInvalid

from FZBypass import Config, Bypass, BOT_START
from FZBypass.core.bypass_checker import direct_link_checker, is_excep_link
from FZBypass.core.bot_utils import AuthChatsTopics, convert_time, BypassFilter


@Bypass.on_message(command("start"))
async def start_msg(client, message):
    await message.reply(
        f"""<b><i>ACT ADS Bypass Bot!</i></b>
    
    <i>Python မှာရေးထားတဲ့ အားကောင်းလှတဲ့ Multi Threaded Bot... အမျိုးမျိုးသော Shortener Links၊ Scrape links နှင့် အခြားအရာများကို ကျော်လွှားနိုင်သည်... </i>
    
    <i><b>Bot ကို လွန်ခဲ့သော  {convert_time(time() - BOT_START)}  တွင် စတင်ခဲ့သည်...</b></i>

🛃 <b>သုံးချင်ရင် ဒီမှာလာဆက်သွယ်ပါ။ :</b> @actanibot <i>(Bypass Topic)</i>""",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🎓 Dev", url="https://t.me/When_the_night_falls_my_soul_sea"),
                    InlineKeyboardButton(
                        "🎀 Channel",
                        url="https://t.me/actanimemm",
                    ),
                ]
            ]
        ),
    )


@Bypass.on_message(BypassFilter & (user(Config.OWNER_ID) | AuthChatsTopics))
async def bypass_check(client, message):
    uid = message.from_user.id
    if (reply_to := message.reply_to_message) and (reply_to.text is not None or reply_to.caption is not None):
        txt = reply_to.text or reply_to.caption
        entities = reply_to.entities or reply_to.caption_entities
    elif Config.AUTO_BYPASS or len(message.text.split()) > 1:
        txt = message.text
        entities = message.entities
    else:
        return await message.reply('<i>Where is your link Mf!</i>')
    
    wait_msg = await message.reply("<i>Processing wait...</i>")
    start = time()

    link, tlinks, no = '', [], 0
    atasks = []
    for enty in entities:
        if enty.type == MessageEntityType.URL:
            link = txt[enty.offset:(enty.offset+enty.length)]
        elif enty.type == MessageEntityType.TEXT_LINK:
            link = enty.url
            
        if link:
            no += 1
            tlinks.append(link)
            atasks.append(create_task(direct_link_checker(link)))
            link = ''

    completed_tasks = await gather(*atasks, return_exceptions=True)
    
    parse_data = []
    for result, link in zip(completed_tasks, tlinks):
        if isinstance(result, Exception):
            bp_link = f"\n┖ <b>Bypass Error: \n\n</b>\n\n {result}"
        elif is_excep_link(link):
            bp_link = result
        elif isinstance(result, list):
            bp_link, ui = "", "┖"
            for ind, lplink in reversed(list(enumerate(result, start=1))):
                bp_link = f"\n{ui} <b>{ind}x Bypass Link:</b> {lplink}" + bp_link
                ui = "┠"
        else:
            bp_link = f"\n\n\n┖ <b>Bypass Link: \n\n</b>\n{result}"
    
        if is_excep_link(link):
            parse_data.append(f"{bp_link}\n\n━━━━━「✦ACT✦」━━━━━\n\n")
        else:
            parse_data.append(f'┎ <b>Source Link: </b><code>{link}</code>{bp_link}\n\n━━━━━「✦ACT✦」━━━━━\n\n')
            
    end = time()

    if len(parse_data) != 0:
        parse_data[-1] = parse_data[-1] + f"┎ <b>Total Links : {no}</b>\n┠ <b>Results In <code>{convert_time(end - start)}</code></b> !\n┖ <b>By </b>{message.from_user.mention} ( 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 ACT )\n┗━━━━━━━━━━━━"
    tg_txt = "━━━━━「✦ACT✦」━━━━━\n\n"
    for tg_data in parse_data:
        tg_txt += tg_data
        if len(tg_txt) > 4000:
            await wait_msg.edit(tg_txt, disable_web_page_preview=True)
            wait_msg = await message.reply("<i>Fetching...</i>", reply_to_message_id=wait_msg.id)
            tg_txt = ""
            await asleep(2.5)
    
    if tg_txt != "":
        await wait_msg.edit(tg_txt, disable_web_page_preview=True)
    else:
        await wait_msg.delete()


@Bypass.on_message(command('log') & user(Config.OWNER_ID))
async def send_logs(client, message):
    await message.reply_document('log.txt', quote=True)


@Bypass.on_inline_query()
async def inline_query(client, query):
    answers = [] 
    string = query.query.lower()
    if string.startswith("!bp "):
        link = string.strip('!bp ')
        start = time()
        try:
            bp_link = await direct_link_checker(link, True)
            end = time()
            
            if not is_excep_link(link):
                bp_link = f"┎ <b>Source Link:</b> {link}\n┃\n┖ <b>Bypass Link:</b> {bp_link}"
            answers.append(InlineQueryResultArticle(
                title="✅️ Bypass Link Success !",
                input_message_content=InputTextMessageContent(
                    f'{bp_link}\n\n✎﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏\n\n🧭 <b>Took Only <code>{convert_time(end - start)}</code></b>',
                    disable_web_page_preview=True,
                ),
                description=f"Bypass via !bp {link}",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Bypass Again', switch_inline_query_current_chat="!bp ")]
                ])
            ))
        except Exception as e:
            bp_link = f"<b>Bypass Error:</b> {e}"
            end = time()

            answers.append(InlineQueryResultArticle(
                title="❌️ Bypass Link Error !",
                input_message_content=InputTextMessageContent(
                    f'┎ <b>Source Link:</b> {link}\n┃\n┖ {bp_link}\n\n✎﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏\n\n🧭 <b> <code>{convert_time(end - start)} သာကြာသည်၊၊ </code></b>',
                    disable_web_page_preview=True,
                ),
                description=f"Bypass via !bp {link}",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Bypass Again', switch_inline_query_current_chat="!bp ")]
                ])
            ))    
        
    else:
        answers.append(InlineQueryResultArticle(
                title="♻️ Bypass Usage: In Line",
                input_message_content=InputTextMessageContent(
                    '''<b><i>ACT Bypass bot!</i></b>
    
    <i>Python မှာရေးထားတဲ့ အားကောင်းလှတဲ့ Multi Threaded Bot... အမျိုးမျိုးသော Shortener Links၊ Scrape links နှင့် အခြားအရာများကို ကျော်လွှားနိုင်သည်...  </i>
    
🎛 <b>Inline Use :</b> !bp [Single Link]''',
                ),
                description="Bypass via !bp [link]",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("ACT", url="https://t.me/actanimemm"),
                        InlineKeyboardButton('Try Bypass', switch_inline_query_current_chat="!bp ")]
                ])
            ))
    try:
        await query.answer(
            results=answers,
            cache_time=0
        )
    except QueryIdInvalid:
        pass
