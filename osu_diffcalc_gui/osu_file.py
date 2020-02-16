
import os
import jinja2
from collections import namedtuple

OsuPoint = namedtuple("OsuPoint",("x","y","t"))

def radius(cs):
    return (512 / 16) * (1 - 0.7 * (cs - 5) / 5)

PLAY_AREA_WIDTH=512
PLAY_AREA_HEIGHT=384


class OsuFile:
    path = os.path.dirname(os.path.realpath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = env.get_template("map.osu.jinja")
    
    @classmethod
    def save(cls, output_file, **kwargs):
        output = cls.template.render(**kwargs)
        output_file.write(output)
