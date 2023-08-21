import yt_dlp


async def yt_audio_search(query):
    title, url = None, None
    ydl_opts = {
            'format': 'mp3/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'default_search': 'auto',
            'verbose': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' not in info or not info['entries']:
            raise Exception('No video found.')

        title = info['entries'][0]['title']
        url = tuple(sorted(filter(lambda x: x.get('resolution') == 'audio only',
                                  info['entries'][0]['formats']),
                           key=lambda x: x.get('quality', 0), reverse=True))[0]['url']

    return title, url
