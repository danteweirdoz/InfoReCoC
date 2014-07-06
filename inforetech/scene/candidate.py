import sys
from PIL import Image


class CandidateScene(object):
    map = {
        "opponent": {
            "gold": {
                "left":   60,
                "top":    80,
                "width":  160,
                "height": 30
            },
            "elixir": {
                "left":   60,
                "top":    115,
                "width":  160,
                "height": 30
            },
            "dard_elixir": {
                "left":   60,
                "top":    150,
                "width":  160,
                "height": 30
            },
            "cup": {
                "left":   60,
                "top":    191,
                "width":  160,
                "height": 30
            }
        }
    }

    def __init__(self, image):
        self.im = image
        self.__split()

    def __split(self):
        self.info = {}
        for section, items in self.map.iteritems():
            self.info[section] = {}
            for item, pos in items.iteritems():
                item_image = self.im.crop((pos["left"],
                                           pos["top"],
                                           pos["left"] + pos["width"],
                                           pos["top"] + pos["height"]))
                self.info[section][item] = {"image": item_image}
                item_image.show()

    def show(self):
        self.im.show()


def test():
    import os
    filename = os.path.join(os.path.dirname(__file__),
                            "../../sample/800x1280/attacked_candidate.png")
    im = Image.open(filename, "r")
    cs = CandidateScene(im)


if __name__ == "__main__":
    sys.exit(test())
