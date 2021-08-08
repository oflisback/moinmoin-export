import argparse
import os
import re
import sys

def get_lines(filename):
    f = None
    try:
        f = open(filename)
        return f.readlines()
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

# Replace any initial == Header == with leading *:s, one extra to not
# conflict with the top article level.
def replace_headers(s):
    for i in range(1,6):
        eq = "=" * i
        stars = "*" * (i + 1)
        s = re.sub(r'^{}([^=][\s\S]+?[^=]){}'.format(eq,eq), r'{}\1'.format(stars),s)
    return s

# Bold text: Replace '''<text>''' with <text>
def remove_bold(s):
    return re.sub(r'\'\'\'([\s\S]+?)\'\'\'', r'\1',s)

def replace_table_separators(s):
    return re.sub(r'\|\|([\S+?\s*?]+?)\|\|', r'|\1|',s)

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

def append_to_org(article_name, lines, org_output_file):
    with open(org_output_file, 'a' if os.path.exists(org_output_file) else 'w') as file:
        lines = list(map(lambda l: moin_line_to_org_line(l), lines))
        lines.insert(0, "* " + article_name + '\n')
        file.writelines(lines)

def moin_article_to_output(article, org_output_file, output_dir):
    revision_lines = get_lines(os.path.join(article, "current"))
    if revision_lines is None:
        revision = get_last_existing_revision(article)
        if revision is None:
            print("No revisions found, giving up on: " + article)
            return
        print("Instead using: " + revision)
    else:
        revision = revision_lines[0].strip()
    data_file = os.path.join(article,"revisions",revision)
    article_lines = get_lines(data_file)
    if article_lines is None:
        revision = get_last_existing_revision(article)
        if revision is None:
            print("No revisions found, giving up on: " + article)
            return
        print("Instead using: " + revision)
    article_name = os.path.basename(article)
    if article_lines:
        if output_dir:
            with open(os.path.join(output_dir, article_name), 'w') as file:
                file.writelines(article_lines)
        if org_output_file:
            append_to_org(article_name, article_lines, org_output_file)

def main():
    parser = argparse.ArgumentParser(description='Convert moinmoin pages to text files or an org mode wiki.')
    parser.add_argument('pages', help='path to moinmoin pages')
    parser.add_argument('--org-file', dest="org_output_file", help='path to output org mode wiki file')
    parser.add_argument('-o, --output-dir', dest="output_dir", help='output dir')

    args = parser.parse_args()
    dirs = [os.path.abspath(os.path.join(args.pages, f)) for f in os.listdir(args.pages) if os.path.isdir(os.path.join(args.pages, f))]
    dirs.sort()
    for d in dirs:
        moin_article_to_output(d, args.org_output_file,args.output_dir)

if __name__ == '__main__':
    main()
