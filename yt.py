import json
import os
import sys
import urllib3


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def _get_channel_videos_per_page(url):
    http = urllib3.PoolManager()
    resp = http.request("GET", url)
    data = json.loads(resp.data)
    channel_videos = dict()

    if 'items' not in data:
        return channel_videos, None
    item_data = data['items']
    next_page_token = data.get('nextPageToken', None)

    for item in item_data:
        try:
            kind = item['id']['kind']
            if kind == 'youtube#video':
                video_id = item['id']['videoId']
                channel_videos[video_id] = dict()
        except KeyError:
            print('Error!')

    return channel_videos, next_page_token


def _name_correction(title):
    forbidden_char = ['<', '>', ':', '"', '/', "\\", '|', '?', '*', ' ']
    for char in forbidden_char:
        title = title.replace(str(char), '_')

    file_name = str(title.lower()) + '.json'
    return file_name


class YoutubeStat:

    def __init__(self, api_key, key_word, limit):
        self.api_key = api_key
        self.key_word = key_word
        self.video_data = None
        self.limit = limit

    def get_channel_video_data(self):
        # 1) get all the video IDs
        channel_videos = self._get_channel_videos(self.limit)
        print(f'Fetching {len(channel_videos)} video(s) data...')
        # print(channel_videos)
        # 2) get the video statistics
        parts = ["snippet", "statistics", "contentDetails"]
        for video_id in channel_videos:
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)

        self.video_data = channel_videos
        return channel_videos

    def _get_single_video_data(self, video_id, part):
        url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        http = urllib3.PoolManager()
        resp = http.request("GET", url)
        data = json.loads(resp.data)
        try:
            data = data['items'][0][part]
        except:
            print(f"Sorry! {video_id} is impossible to fetch data!")
            data = dict()

        return data

    def _get_channel_videos(self, limit=None):
        url = f'https://www.googleapis.com/youtube/v3/search?&maxResults={self.limit}&q={self.key_word}&' \
              f'type=video&key={self.api_key} '
        # print(url)
        vid, npt = _get_channel_videos_per_page(url)
        idx = 0
        while npt is not None and idx < 10:
            next_url = url + '&pageToken=' + npt
            next_vid, npt = _get_channel_videos_per_page(next_url)
            vid.update(next_vid)
            idx += 1
        return vid

    def dump(self):
        fused_data = dict()
        if self.video_data is None:
            print('Data is none!')
            return
        #for item in self.video_data:
            # title = self.video_data[item].get('\n\ttitle')
            # file_name = _name_correction(title)
        file_name = self.key_word + '.json'
        with open(file_name, 'w') as f:
            json.dump(self.video_data, f, indent=4)
            print(f'Data for {self.key_word} saved!')
