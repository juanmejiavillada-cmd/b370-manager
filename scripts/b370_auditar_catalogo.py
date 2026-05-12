from b370_mcp import core


def main():
    products = []
    page = 1
    while True:
        r = core.wc_get('products', per_page=100, page=page, status='publish')
        if r.status_code != 200:
            raise SystemExit(f'HTTP {r.status_code} {r.text}')
        batch = r.json()
        if not batch:
            break
        products.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    print(f'Loaded {len(products)} published products')

    issues = []
    for p in products:
        pid = p['id']
        name = p.get('name')
        price = p.get('price')
        if p.get('type') == 'variable':
            vars_r = core.wc_get(f'products/{pid}/variations', per_page=100)
            vars_list = vars_r.json() if vars_r.status_code == 200 else []
            if not vars_list:
                issues.append((pid, name, 'variable sin variaciones', None, None, None))
            for v in vars_list:
                vid = v['id']
                vprice = v.get('regular_price') or v.get('price')
                if vprice in (None, '', '0'):
                    issues.append((pid, name, 'variación sin precio', vid, v.get('sku'), vprice))
                else:
                    try:
                        vp = float(vprice)
                    except Exception:
                        issues.append((pid, name, 'precio no numérico variación', vid, v.get('sku'), vprice))
                        continue
                    if vp < core.PRICE_MIN or vp > core.PRICE_MAX:
                        issues.append((pid, name, 'precio anómalo variación', vid, v.get('sku'), vp))
        else:
            if price in (None, '', '0'):
                issues.append((pid, name, 'sin precio padre', None, p.get('sku'), price))
            else:
                try:
                    pval = float(price)
                except Exception:
                    issues.append((pid, name, 'precio no numérico padre', None, p.get('sku'), price))
                    continue
                if pval < core.PRICE_MIN or pval > core.PRICE_MAX:
                    issues.append((pid, name, 'precio anómalo padre', None, p.get('sku'), pval))

    priority = {
        'variación sin precio': 1,
        'sin precio padre': 1,
        'precio no numérico variación': 2,
        'precio no numérico padre': 2,
        'precio anómalo variación': 3,
        'precio anómalo padre': 3,
        'variable sin variaciones': 4,
    }

    issues.sort(key=lambda x: (priority.get(x[2], 99), x[0], x[3] or 0))

    for item in issues:
        print(item)
    print('ISSUE_COUNT', len(issues))


if __name__ == '__main__':
    main()
