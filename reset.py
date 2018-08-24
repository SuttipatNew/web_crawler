import os, codecs
os.system('rm visited_q count list_robots.txt list_sitemap.txt')
with codecs.open('./frontier_q', 'w', 'utf-8') as f:
    f.write('http://www.ku.ac.th/web2012/\n')
    f.write('http://www.eng.ku.ac.th/')