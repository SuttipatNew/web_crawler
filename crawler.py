import requests, re, os, codecs, urllib
from reppy.robots import Robots
from urllib.parse import urljoin
from urllib.parse import urlparse
from my_queue import Queue
from bs4 import BeautifulSoup

html_dir = 'D:\\Suttipat\\Documents\\Web IR\\web_crawler_result\\html'

headers = {
    'User-Agent': '01204453 bot by 5810504582',
    'From': 'suttipat.s@ku.th'
}

frontier_q = Queue('./frontier_q')
visited_q = Queue('./visited_q')
list_robots = Queue('./list_robots.txt')
list_sitemap = Queue('./list_sitemap.txt')
error_list = Queue('./error_list')

def load_downloaded_count():
    try:
        f = open('./count')
        count = int(f.read())
        f.close()
        return count
    except:
        return 0

def save_downloaded_count(count):
    with open('./count', 'w') as f:
        f.write(str(count))

def save_file(html, url):
    global html_dir
    parsed_url = urlparse(url)
    path = parsed_url.netloc + parsed_url.path
    dirname = ''

    if not re.search('.html$', path) and not re.search('.htm$', path) and not re.search('.txt', path):
        dirname = path.replace('/', '\\')
        if path[-1] != '/':
            path += '/'
        path = urljoin(path, 'index.html')
        # print(path)
    else:
        dirname = os.path.dirname(path.replace('/', '\\'))
    try:
        # print(f'dirname: {dirname}')
        os.makedirs(os.path.join(html_dir, dirname))
    except:
        pass
    path = os.path.join(html_dir, path.replace('/', '\\'))
    # print(f'saving file at {path}')
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(html)

def remove_url_queries(url):
    o = urlparse(url)
    return o.scheme + "://" + o.netloc + o.path

def get_page(url) :
    global headers
    try :
        r = requests.get(url,headers=headers,timeout=2)
        html = r.text
        if r.status_code == 404:
            print(f'404: {url}')
            html = None
        return html
    except (KeyboardInterrupt, SystemExit):
        raise
    except :
        print(f'getting page error: {url}')
        return None

def get_links(html, base_url):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        links = [urllib.parse.unquote(urllib.parse.unquote(urljoin(base_url, link.get('href')))).strip() for link in soup.find_all('a')]
        return links
    except:
        return []

def is_valid_extension(link):
    ext = os.path.splitext(link)[1]
    return (not re.search(':\\d+$', urlparse(link).netloc)) and (ext == '' or ext == '.html' or ext == '.htm')

def is_url_valid(url):
    return get_baseurl(url).find('ku.ac.th') != -1 and url[-4:] != '.php' and is_valid_extension(url) and len(re.sub('^https?://', '', url).split('/')) <= 10

def parse_robots(robots, base_url):
    disallowed = []
    reading = False
    for line in robots.split('\n'):
        if line == 'User-agent: *':
            reading = True
        elif reading and not line.startswith('User-agent'):
            disallowed.append(urljoin(base_url, line[len('disallow: '):]))
        else:
            reading = False
    return disallowed

def filter_url(urls, current_url, disallowed):
    global headers, visited_q, frontier_q, error_list
    print(f'\tgot more {len(urls)} urls')
    urls = list(set([remove_url_queries(url) for url in urls]))
    urls = [url for url in urls if is_url_valid(url) and url not in disallowed and not visited_q.is_there(url) and not frontier_q.is_there(url) and not error_list.is_there(url)]
    print(f'\t{len(urls)} are valid')
    return urls

def get_hostname(url):
    return urlparse(url).netloc

def get_baseurl(url):
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'

def main():
    global frontier_q, visited_q, list_robots, list_sitemap, error_list
    frontier_q.load(); visited_q.load(); list_robots.load(); list_sitemap.load(); error_list.load()
    count = load_downloaded_count()

    while frontier_q.length() > 0:
        found_sitemap = False
        url = frontier_q.get_first()
        visited_q.insert(url)
        print(f'getting: {url}')
        html = get_page(url)

        if html is not None:
            save_file(html, url)
            count += 1
            print(f'[{count}/10000] downloaded: {url}')

            disallowed = []
            hostname = get_hostname(url)
            if not list_robots.is_there(hostname):
                robots_url = get_baseurl(url) + '/robots.txt'
                robots_data = get_page(robots_url)
                if robots_data is not None and re.fullmatch('((#[^\n]*|((User-agent|Allow|Disallow|Sitemap|Crawl-delay):\\s?[^\\s]+))?\\s*\n*)+', robots_data):
                    disallowed = parse_robots(robots_data, get_baseurl(url))
                    list_robots.insert(hostname)
                    save_file(robots_data, robots_url)
                    if re.search('^Sitemap', robots_data, flags=re.MULTILINE):
                        list_sitemap.insert(hostname)
                        found_sitemap = True

            links = get_links(html, url)
            links = filter_url(links, url, disallowed)
            frontier_q.merge(links)
        print(f'\t{frontier_q.length()} left in queue')
        frontier_q.save(); visited_q.save(); list_robots.save(); list_sitemap.save(); save_downloaded_count(count)
        if found_sitemap:
            break
        
if __name__ == '__main__':
    main()