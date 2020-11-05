import os, re, requests, sys, tinycss2

try:
    save_path = os.path.expanduser(sys.argv[1])
    print("Using custom save path...")
except IndexError:
     save_path = os.path.join(os.path.expanduser('~'), "Downloads", "nytfonts")
     print("No custom save path provided, using default...")

try:
    os.mkdir(save_path)
except OSError:
    pass

print(f"Saving fonts to '{save_path}'")

base_url = "https://nytimes.com"

# get homepage to find fonts stylesheet URL
homepage = requests.get(base_url)
if not homepage.ok:
    raise Exception(
        f"Could not fetch NYT homepage at {webfonts_stylesheet_url}",
        f"content: {stylesheet_r.content}",
        f"code: {stylesheet_r.status_code}"
    )

try:
    # strip stylesheet url
    webfonts_stylesheet_url = re.search("https://.{1,20}/fonts/css/web-fonts\.\w*\.css", str(homepage.content)).group()
except AttributeError:
    print(f"Couldn't find font stylesheet URL on {base_url}, check regExp for `webfonts_stylesheet_url`")
    raise

# get stylesheet
stylesheet_r = requests.get(webfonts_stylesheet_url)

if not stylesheet_r.ok:
    raise Exception(
        f"Could not fetch stylesheet at {webfonts_stylesheet_url}",
        f"content: {stylesheet_r.content}",
        f"code: {stylesheet_r.status_code}"
    )

stylesheet = stylesheet_r.content

try:
    # parse it
    parsed = tinycss2.parse_stylesheet_bytes(stylesheet)
except Exception:
    print("Failed to parse stylesheet")
    raise

functions = []
rules = [rule.content for rule in parsed[0] if rule.type == 'at-rule']
for rule in rules:
    for block in rule:
        if block.type == 'function' and block.name == 'url':
            functions.append(block)

font_urls = [f"{base_url}{function.arguments[0].value}" for function in functions]


print('Beginning NYT font download with requests')

for url in font_urls:
    match_string = "https://nytimes.com/fonts/family/(.*)/(.*)\..*\.(woff2?|ttf)"
    filename = re.sub(match_string, r"\2.\3", url)
    font_type = re.sub(match_string, r"\3", url)
    family = re.sub(match_string, r"\1", url)

    path = os.path.join(save_path, family, font_type)

    try:
        os.makedirs(path)
    except OSError as exc:
        pass
    else:
        print ("Successfully created the directory %s " % path)

    r = requests.get(url)

    with open(os.path.join(path, filename), 'wb') as f:
        f.write(r.content)
