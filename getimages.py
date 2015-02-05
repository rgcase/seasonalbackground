import praw
import requests
from subprocess import Popen, PIPE, STDOUT
import datetime
import re

RESOLUTION_RATIO = float(1680) / float(1050)
PATH_TO_FOLDER = '/Users/ryan/Pictures/'

def findseason(day):
    if 3 <= day.month <= 5:
        return 'spring'
    elif 6 <= day.month <= 8:
        return 'summer'
    elif 9 <= day.month <= 11:
        return 'autumn'
    else:
        return 'winter'


def current_photos():
    p = Popen(['ls', '~/Pictures/*.jpg'], stderr=STDOUT, stdout=PIPE, shell=False)
    images = set(p.communicate()[0].split('\n')[:-1])
    return images


def newest_photos(day):
    season = findseason(day)
    r = praw.Reddit(user_agent='Seasonal Background by rgcase')
    submissions = r.get_subreddit(season + 'porn').get_new(limit=100)
    photos = list(submissions)
    new_photos = filter(lambda p: today_photo(day, p), photos)
    res_photos = map(find_res, new_photos)
    good_photos = filter(good_photo, res_photos)
    return good_photos


def today_photo(day, photo):
    photo_day = datetime.date.fromtimestamp(photo.created_utc)
    yesterday = day - datetime.timedelta(days=1)
    return photo_day == day or photo_day == yesterday


def find_res(photo):
    res_re = '\[[0-9]* *x *[0-9]*\]'
    photo_res = re.search(res_re, photo.title)
    if photo_res:
        return (photo_res.group(0), photo)
    else:
        return (photo_res, photo)


def good_photo(photo):
    if photo[0]:
        x, y = photo[0].split('x')
        try:
            x = float(x[1:])
            y = float(y[:-1])
        except ValueError:
            return False

        return RESOLUTION_RATIO - 0.1 <= x / y <= RESOLUTION_RATIO + 0.1
    else:
        return False


def dl_photos(photos):
    print str(len(photos)) + " new photos!"
    for photo in photos:
        fname = photo[1].url.split('/')[-1]
        if not fname:
            continue
        file = open(PATH_TO_FOLDER + str(fname), 'a')
        r = requests.get(photo[1].url)
        file.write(r.content)
        file.close()


# clear_oldest(len(photos)) #TODO: implement clear_oldest
def clear_oldest(num):
    pass


def main():
    new_photos = newest_photos(datetime.date.today())
    dl_photos(new_photos)


if __name__ == '__main__':
    main()
