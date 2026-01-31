import os

from dotenv import load_dotenv
from browser_use import Agent, Browser, ChatGoogle

load_dotenv()


async def post_to_x(image_path: str, video_path: str, caption: str) -> bool:
    abs_image = os.path.abspath(image_path)
    abs_video = os.path.abspath(video_path)

    browser = Browser(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        user_data_dir="~/Library/Application Support/Google/Chrome",
        profile_directory="Default",
    )

    try:
        agent = Agent(
            task=(
                f"Go to x.com. You are already logged in. "
                f"First, click the post button to open the compose dialog. "
                f"Then type this text: '{caption}'. "
                f"Then upload the image at '{abs_image}' as a media attachment. "
                f"Then upload the video at '{abs_video}' as a media attachment. "
                f"After uploading the video, wait at least 15 seconds for it to process before doing anything else. "
                f"Finally, click the Post button to publish it."
            ),
            llm=ChatGoogle(model="gemini-3-flash-preview"),
            browser=browser,
            available_file_paths=[abs_image, abs_video],
            max_steps=25,
        )

        result = await agent.run()
        return result.is_done()
    except Exception as e:
        print(f"Browser agent error: {e}")
        return False
    finally:
        await browser.kill()
