from yt import *

# MAIN
try:
    with open('api.txt') as f:
        api = f.read()
    if api:
        while True:
            key_word = input('\nEnter the key word: ')

            if key_word:
                limit = input('Number of pages to scrape: ')
                if limit:
                    while int(limit) > 50:
                        print('\nNumber of pages could not be more than 50.')
                        limit = input('Try another number: ')
                else:
                    limit = 1

                print('Creating client...')
                yt = YoutubeStat(api, key_word, int(limit))
                yt.get_channel_video_data()
                print('Data fetched!\nSaving data in files...')
                yt.dump()

            else:
                print('Empty input!')
    else:
        print('API key not found!')

except OSError:
    print("Could not open api.txt file.")
    input('Press any key to exit...')


# DEVELOPED by SAJADSOJOUDI@gmail.com
