from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.helpers import extract_image_urls
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Arg
from nonebot.typing import T_State

#from .savor import savor_image


from gradio_client import Client,handle_file


analysis = on_command("鉴赏图片", aliases={"分析图片", "解析图片"}, block=True)


@analysis.handle()
async def image_analysis(event: MessageEvent, matcher: Matcher):
    message = reply.message if (reply := event.reply) else event.message
    if imgs := message["image"]:
        matcher.set_arg("imgs", imgs)


@analysis.got("imgs", prompt="请发送需要分析的图片")
async def get_image(state: T_State, imgs: Message = Arg()):
    urls = extract_image_urls(imgs)
    if not urls:
        await analysis.finish("没有找到图片, 分析结束")
    state["urls"] = urls


@analysis.handle()
async def analysis_handle(state: T_State):
    await analysis.send("正在分析图像, 请稍等……")
    try:
        client = Client("hysts/DeepDanbooru")
        img = state["urls"][0]
        logger.info(f"img-url: {img}")
        res = await client.predict(image=handle_file(img),score_threshold=0.5, api_name="/predict")
        result=json.loads(res)["output"]["data"][0]["confidences"]
    except Exception as e:
        logger.opt(exception=e).error("分析失败")
        await analysis.finish("分析失败, 请稍后重试", reply_message=True)
    msg = ", ".join(i["label"] for i in result if not i["label"].startswith("rating:"))
    await analysis.finish(msg, reply_message=True)
