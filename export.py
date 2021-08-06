import argparse
import os
import re
import sys

def get_content(filename):
    f = None
    try:
        f = open(filename)
        return f.read().strip()
    except FileNotFoundError:
        print("Ignoring missing file: " + filename)
    except PermissionError:
        print("Permission denied, ignoring: " + filename)
    except Exception as e:
        print("Ignoring, error: " + e)
    finally:
        if f:
            f.close()

def numeric_sort(a, b):
    return int(a) > int(b)

def get_last_existing_revision(d):
    dir = os.path.join(d, "revisions")
    try:
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    except:
        return
    numeric_files = list(filter(lambda f: f.isnumeric(), files))
    numeric_files.sort(key=lambda f: int(f), reverse=True)
    if len(numeric_files) > 0:
        return numeric_files[0]

def write_content(content, filename):
    with open(filename, 'w') as file:
        file.write(content)

def replace_headers(s):
    # Headers: Replace any initial == Header == with leading *:s, one extra to not
    #          conflict with the top article level.
    for i in range(1,6):
        eq = "=" * i
        stars = "*" * (i + 1)
        s = re.sub(r'^{}([^=][\s\S]+?[^=]){}'.format(eq,eq), r'{}\1'.format(stars),s)
    return s

def remove_bold(s):
    return re.sub(r'\'\'\'([\s\S]+?)\'\'\'', r'\1',s)

def replace_table_separators(s):
    return re.sub(r'\|\|([\S+?\s*?]+?)\|\|', r'|\1|',s)

# Bold: replace '''<text>''' with <text>
def moin_line_to_org_line(l):
    if len(l) <= 0:
        return l
    # Lists: Replace any initial * with -
    if l[0] == '*':
        l = '-' + l[1:]
    l = replace_headers(l)
    l = remove_bold(l)
    l = replace_table_separators(l)

    return l

def moin_text_to_org_text(text):
    result = []
    [result.append(moin_line_to_org_line(l) + '\n') for l in text.splitlines()]
    return ''.join(result)

def append_to_org(article_name, content, org_output_file):
    with open(org_output_file, 'a' if os.path.exists(org_output_file) else 'w') as file:
        file.write("* " + article_name + "\n")
        file.write(moin_text_to_org_text(content))

def moin_article_to_output(article, org_output_file, output_dir):
    revision = get_content(os.path.join(article, "current"))
    if revision is None:
        revision = get_last_existing_revision(article)
        if revision is None:
            print("No revisions found, giving up on: " + article)
            return
        print("Instead using: " + revision)
    data_file = os.path.join(article,"revisions",revision)
    content = get_content(data_file)
    if content is None:
        revision = get_last_existing_revision(article)
        if revision is None:
            print("No revisions found, giving up on: " + article)
            return
        print("Instead using: " + revision)
    article_name = os.path.basename(article)
    if content:
        if output_dir:
            write_content(content, os.path.join(output_dir, article_name))
        if org_output_file:
            append_to_org(article_name, content, org_output_file)

def main():
    parser = argparse.ArgumentParser(description='Convert moinmoin pages to text files or an org mode wiki.')
    parser.add_argument('-p, --pages-dir', dest="pages_dir", help='an integer for the accumulator')
    parser.add_argument('--org-file', dest="org_output_file", help='path to output org mode wiki file')
    parser.add_argument('-o, --output-dir', dest="output_dir", help='output dir')

    args = parser.parse_args()
    dirs = [os.path.abspath(os.path.join(args.pages_dir, f)) for f in os.listdir(args.pages_dir) if os.path.isdir(os.path.join(args.pages_dir, f))]
    [moin_article_to_output(d, args.org_output_file,args.output_dir) for d in dirs]

if __name__ == '__main__':
    main()