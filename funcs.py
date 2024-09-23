def get_day_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    else:
        last_digit = day % 10
        if last_digit == 1:
            return ' st'
        elif last_digit == 2:
            return ' nd'
        elif last_digit == 3:
            return ' rd'
        else:
            return ' th'
        

def catmull_rom_points(p0, p1, p2, p3, res):
    points = []
    for i in range(res):
        t = i / float(res)
        t2 = t * t
        t3 = t2 * t
        x = 0.5 * ((2 * p1[0]) +
                   (-p0[0] + p2[0]) * t +
                   (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                   (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
        y = 0.5 * ((2 * p1[1]) +
                   (-p0[1] + p2[1]) * t +
                   (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                   (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
        points.append((x, y))
    return points

def get_catmull_rom_chain(points, res):
    chain = []
    for i in range(len(points) - 3):
        c = catmull_rom_points(points[i], points[i+1], points[i+2], points[i+3], res)
        chain.extend(c)
    return chain