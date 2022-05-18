import sys, json, codecs, requests, shutil, os
from multiprocessing import Pool, cpu_count
from functools import partial

def clean_url(url):
    return ''.join(url.split('\\'))

def png2ts(data):
    return data[120:]

def css2ts(data):
    #return data
    exit()

def get_ts(name, url):
    global out_dir
    #print(type(name), name, type(url), url)
    raw_ts = requests.get(url).content
    if url.endswith('.png'):
        raw_ts = png2ts(raw_ts)
    elif url.endswith('.css'):
        raw_ts = css2ts(raw_rs)
    else:
        raise RuntimeError(f'Not supported type: {url}')
    
    with open(os.path.join(out_dir, f'{name}.ts'), 'wb') as f:
        f.write(raw_ts)

try:
    url, out_path = str(sys.argv[1]), str(sys.argv[2])
except IndexError:
    print(f'Format: python3 {sys.argv[0]} [url] [out_path]')
    sys.exit(1)

out_dir = 'tmp_output'
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.mkdir(out_dir)

page = str(requests.get(url).content)
start = page.find('var player_data')
page = page[start:]

i = 0
for j in range(3):
    i = page[i:].find('</script>') + i + len('</script>')

player_data = json.loads(page[page.find('{'):page.find('}')+1])
print(player_data['encrypt'])
print(clean_url(player_data['url']))
print(clean_url(player_data['url_next']))

url = clean_url(player_data['url'])
#url = clean_url(player_data['url_next'])
m3u8 = requests.get(url).content.decode('unicode_escape').splitlines()

if len(m3u8) <= 5:
    raise RuntimeError('May have double m3u8')
"""
if len(m3u8) <= 5 and m3u8[-1].endswith('.m3u8'):
    print(m3u8)
    m3u8 = m3u8[-1]
    token = [v for v in m3u8.split('/') if len(v)>0][0]
    idx = url.find(token)
    if idx >= 0:
        real_url = url[:url.find(token)] + m3u8[m3u8.find(token):]
    else:
        print(m3u8)
        print(url)
        real_url = '/'.join(url.split('/')[:-1])
        real_url += f'/{m3u8}' if m3u8[0]!='/' else m3u8
    print(f'{real_url = }')
    m3u8 = requests.get(real_url).content.decode('unicode_escape').splitlines()
"""

ts_list = []
for string in m3u8:
    if string.startswith('http'):
        ts_list.append(string)
ts_name_list = [x for x in range(len(ts_list))]

"""
for name,url in zip(ts_name_list,ts_list):
    print(name, url)
"""
print("There are {} CPUs on this machine ".format(cpu_count()))
pool = Pool(cpu_count())
results = pool.starmap(get_ts, zip(ts_name_list,ts_list))
pool.close()
pool.join()

with open('tmpoutput.ts', 'wb') as f:
    for i in range(len(ts_list)):
        with open(os.path.join(out_dir, f'{i}.ts'), 'rb') as fr:
            f.write(fr.read())
shutil.rmtree(out_dir)
os.system(f'ffmpeg -i tmpoutput.ts -acodec copy -vcodec copy {out_path}')
os.remove('tmpoutput.ts')
