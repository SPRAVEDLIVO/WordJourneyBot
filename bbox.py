
from rect import Rect

SPREAD = 70
C = (255, 255, 255, 255)


def spreadRight(boxes, letters, pic, x, y):
    lastSeenR = x
    lastSeenL = x

    for j in range(y-SPREAD, y+SPREAD+1):
        for i in range(x-SPREAD, x+SPREAD+1):
            if i > letters.width-1:
                break
            if j > letters.height-1:
                continue
            if j < 0 or i < 0:
                continue
            if pic[i, j] == C and not point_in_rects(boxes, (i, j)):
                lastSeenR = max(lastSeenR, i)
                lastSeenL = min(lastSeenL, i)
    return lastSeenR, lastSeenL

# def spreadLeft(letters, pic, x, y):
#    lastSeen = x
#    for j in range(y-SPREAD, y+SPREAD+1):
#        for i in range(x-SPREAD+1, x+SPREAD):
#            if i < 0: continue
#            if j > letters.height-1: break
#            if pic[i, j] == C:
#                lastSeen = min(lastSeen, i)
#    return lastSeen


def spreadBottom(boxes, letters, pic, y, right, left):
    lastSeenB = y
    lastSeenT = y
    for i in range(y-SPREAD, y+SPREAD+1):
        for x in range(left, right+1):
            if i > letters.height-1:
                continue
            if i < 0:
                continue
            if pic[x, i] == C and not point_in_rects(boxes, (x, i)):
                lastSeenB = max(lastSeenB, i)
                lastSeenT = min(lastSeenT, i)
                break
    return lastSeenB, lastSeenT


def point_in_rect(box, point):
    return (point[0] <= box[2] and point[0] >= box[0] and point[1] <= box[3] and point[1] >= box[1])


def point_in_rects(boxes, point):
    for i in boxes:
        if point_in_rect(i, point):
            return True
    return False


def bbox_letters(letters):
    pic = letters.load()

    boxes = []

    for x in range(letters.width):
        for y in range(letters.height):
            if pic[x, y] == C and not point_in_rects(boxes, (x, y)):
                right, left = spreadRight(boxes, letters, pic, x, y)
                # left = spreadLeft(letters, pic, x, y)
                bottom, top = spreadBottom(boxes, letters, pic, y, right, left)
                right += 1
                bottom += 1
                boxes.append(Rect(left, top, right, bottom))
    return boxes

# normalize dataset
# for f in os.listdir("images/letters/"):
#    p = Image.open(f"images/letters/{f}")
#    bbox = bbox_letters(p)
#    img = p.crop(list(bbox[0]))
#    img.save(f"images/letters/{f}")
#
# img = Image.open("images/letters/А.png")
# bbox = bbox_letters(img)[0]
# img_o = img.crop(list(bbox))
# img_o.save("1.png")
