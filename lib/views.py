import numpy as np

from aiohttp.web import Response
from aiohttp.web import View
from aiohttp_jinja2 import render_template

from lib.image import image_to_img_src
from lib.image import PolygonDrawer
from lib.image import open_image


class IndexView(View):
    async def get(self) -> Response:
        return render_template("index.html", self.request, {})

    async def post(self) -> Response:
        try:
            form = await self.request.post()
            image = open_image(form["image"].file)
            draw = PolygonDrawer(image)
            image = np.array(image)
            threshold = 0
            if "threshold" in form:
                threshold = int(form["threshold"]) / 100
            model = self.request.app["model"]
            words = []
            for coords, word, accuracy in model.readtext(image):
                if accuracy >= threshold:
                    draw.highlight_word(coords, word)
                    cropped_img = draw.crop(coords)
                    cropped_img_b64 = image_to_img_src(cropped_img)
                    words.append(
                        {
                            "image": cropped_img_b64,
                            "word": word,
                            "accuracy": f'{accuracy:.2}',
                        }
                    )
            image_b64 = image_to_img_src(draw.get_highlighted_image())
            ctx = {"image": image_b64, "words": words}
        except Exception as e:
            ctx = {
                "error": {
                    "type": type(e).__name__,
                    "text": str(e)
                }
            }
        return render_template("index.html", self.request, ctx)
