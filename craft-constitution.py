import urllib
from lxml import html
import codecs
from unidecode import unidecode
import re

URL = "http://www.conseil-constitutionnel.fr/conseil-constitutionnel/root/bank_mm/constitution/cc.htm"

content = urllib.urlopen(URL).read()

page = html.fromstring(content)

# Current output file
out = None

def set_curr_file(filename):
    global out
    out = codecs.open(filename, mode="w", encoding="utf-8")

def print_(str) :
    global out
    out.write(str + "\n")


def get_text(el) :
    res = ""
    for text in el.xpath('text() | b/text() | i/text() | u/text()') :
        res += text
    return res

def get_title(div) :
    return get_text(div.xpath('div[@data-role="header"]/h1')[0])


def process_article(article_id) :

    try :
        article_div = page.cssselect(article_id)[0]
    except :
        print "Article not found %s" % article_id
        return
    
    titre = get_title(article_div)
    print_("\n\n## %s " % titre)
    
    content_div = article_div.xpath('div[@data-role="content"]')[0]
    extract_content(content_div)
  

def extract_content(content_div) :
        for el in content_div.xpath('.//*[self::h5 or self::p]') :
            if el.tag == "p" :
                print_("\n" + get_text(el))
            elif el.tag == "h5" :
                print_("\n\n## " + get_text(el))


def section_title_to_filename(title) :

    filename = unidecode(title)
    filename = re.sub('\s*\(.*\)\s*', '', filename)
    filename = re.sub('\s*:\s*', '_', filename)
    filename = re.sub("[ ']", '-', filename) + '.txt'
    return filename
    

def process_annex(annex_id) :

    annex_div = page.cssselect(annex_id)[0]
    
    titre = get_title(annex_div)
    filename = section_title_to_filename(titre)

    set_curr_file(filename)
    
    print "Anex : %s" % filename

    print_("# %s" % titre)
    
    content_div = annex_div.xpath('div[@data-role="content"]')[0]
    extract_content(content_div)


def process_section(section_div) :
    title = section_div.xpath("h3/a/text()")[0];
    filename = section_title_to_filename(title)

    print "Out file : %s" % filename

    set_curr_file(filename);

    print_("# %s" % title)

    for cat in  section_div.xpath("a") + section_div.xpath("p/a") :
        if not cat.get("href").startswith("#titre") :
            process_article(cat.get("href"))

# MAIN
root = page.cssselect("#one")[0]
sections = root[1].cssselect("div")
annexes = root[1].xpath("h3/a")
for section in sections :
    process_section(section)
for annex in annexes :
    annex_id = annex.get('href')
    process_annex(annex_id)

