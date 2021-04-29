import wikipediaapi
import argparse

SLOVJANSKE_VIKI = set("en ru pl uk sr cs sh bg sk hr be sl mk be-tarask hsb rue dsb cu".split(" "))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Kludge Translate.')
    parser.add_argument(
        'priegled', help='trieba li priegled',
        action='store_false')
    parser.add_argument(
        '--lang', help='the source lang', default='en',
    )
    parser.add_argument(
        'stranica', help='stranica za poczatok'
    )

    args = parser.parse_args()

    wiki_wiki = wikipediaapi.Wikipedia(args.lang)
    page_test = wiki_wiki.page(args.stranica.strip())
    print(page_test)

    if args.priegled:
        print(page_test.summary)

    langlinks = page_test.langlinks

    print(f"`{args.lang}` {args.stranica}")
    for k in set(langlinks.keys()) & SLOVJANSKE_VIKI:
        v = langlinks[k]
        print(f"`{k}` {v.title}")
        if args.priegled:
            local_page = page_test.langlinks[k]
            print(local_page.summary)
            print("----------")
