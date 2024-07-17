import telegram
from telegram.ext import CallbackContext

from src.bot.config import moon_config
from src.bot.handlers import constants as handlers_constants
from src.bot.handlers.constants import MOON_POINTS_TASK
from src.points import service as points_service


async def send_points_dashboard(update: telegram.Update, context: CallbackContext, send_message: bool = True):
    user_id = str(update.effective_user.id)
    tasks = await points_service.get_user_tasks(user_id)

    tasks_buttons = []
    for task in tasks:
        task_title = f"{task['name']} - 🌚 {task['points']} points"
        if task["completed_at"]:
            task_title = f"{task_title} ✅"

        callback_data = task["callback_data"] or f"moon_points_task_{task['id']}"
        tasks_buttons.append([telegram.InlineKeyboardButton(task_title, callback_data=callback_data)])

    tasks_buttons.append([telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)])

    total_points = await points_service.count_user_points(user_id)
    points_text = prepare_points_dashboard_text(total_points["points"])
    if send_message:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=moon_config.IMAGE_URL_MOON_POINTS,
            caption=points_text,
            reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        )
    else:
        query = update.callback_query
        await query.edit_message_caption(
            caption=points_text,
            reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        )


def prepare_points_dashboard_text(total_points: int) -> str:
    return (
        "*Welcome to Moon Points\\!* 🌕✨\n\n"
        f"*Your Moon Points*: {total_points}\n\n"
        "Moon Points represent your future Moon Wallet rewards allocations\\.\n\n"
        "While we are still in stealth mode, complete the following limited tasks to earn exclusive points:"
    )


async def get_points_task(update: telegram.Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    query = update.callback_query
    task_id = int(query.data.split(f"{MOON_POINTS_TASK}_")[-1])

    task = await points_service.get_user_task(user_id, task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} not found for user {user_id}")

    if task["slug"] == "claim_og" and not task["completed_at"]:
        await points_service.complete_task(user_id, task_id, task["points"])

    task_title = f"{task['name']} - {task['points']} points"
    if task["completed_at"]:
        await query.answer("Task is already completed")
        return

    task_buttons = [button for button in task["buttons"] if button]
    reply_buttons = []
    for button in task_buttons:
        reply_buttons.append(
            [telegram.InlineKeyboardButton(button["button_text"], callback_data=button["button_callback_data"])]
        )
    reply_buttons.append(
        [telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_RESTORE_POINTS)]
    )

    await query.edit_message_caption(
        caption=f"{task_title}\n\n{task['description']}",
        reply_markup=telegram.InlineKeyboardMarkup(reply_buttons),
    )
