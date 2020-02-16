import numpy as np
import sys
import os
from .osu_file import OsuFile, PLAY_AREA_HEIGHT, PLAY_AREA_WIDTH, radius


class OutOfPlayAreaException(Exception):
    pass

def path_generator(R, pos, jump, count):
    for _ in range(count):
        jump = R @ jump
        pos = pos + jump
        yield pos


def make_points(angle, spacing, count=6):
    s = np.sin(angle)
    c = np.cos(angle)
    R = np.array(((c, -s),(s,c)))


    # start in the middle, work forwards and backwards, ensures things stay centred
    new_point_count = count -2
    
    jump = np.array((spacing, 0),dtype=float)
    start_points=np.array(((0.0,0.0),jump))

    next_points = np.array([p for p in path_generator(R, start_points[1], jump, new_point_count)])



    points = np.vstack((start_points, next_points))
    mean = np.mean(points, axis=0)

    points += np.array((PLAY_AREA_WIDTH/2, PLAY_AREA_HEIGHT/2)) - mean

    if not ((points[:,0] > 0) & (points[:,0] < PLAY_AREA_WIDTH) & (points[:,1] > 0) & (points[:,1] < PLAY_AREA_HEIGHT)).all():
        raise OutOfPlayAreaException

    return points


def main():
    out_dir = sys.argv[1]

    cs = 6
    r = radius(cs)
    n_points=7

    for spacing in [ 0.4, 0.6,  0.9,  1.3,  2.0,  3.6,  4.9,  6.4,  8.1, 10.0 ]:
        for angle in np.linspace(0,np.pi,10):
            try:
                pos = make_points(angle, spacing*2*r, n_points)


                for bpm in (150, 200, 250, 300, 400, 500):
                    times = 0.5 * 60 * 1000/bpm * np.arange(n_points)
                    points = np.column_stack((pos, times))
                    name = f"s_{spacing:.1f}_a_{int(angle*180/np.pi)}_b_{bpm}"

                    filename = os.path.join(out_dir, name+".osu")

                    with open(filename, "w") as f:
                        OsuFile.save(
                            f,
                            points=points,
                            cs=cs,
                            ar=9,
                            od=7,
                            bpm=bpm,
                            version=name
                        )
            except OutOfPlayAreaException:
                print(f"skipping spacing={spacing:.1f} angle={angle*180/np.pi:.0f}")
                pass

if __name__ == "__main__":
    main()
