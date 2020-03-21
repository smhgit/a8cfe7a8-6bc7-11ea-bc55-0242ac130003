# Grocy

A Home Assisatnt shopping list integration based on [Grocy ERP](https://grocy.info/).

---

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

## Description

## Options

| Name | Type | Requirement | `default` Description
| ---- | ---- | ------- | -----------
| host | string | **Required** | your grocy host url
| apikey | string | **Required** | your grocy host apikey


In your `configuration.yaml` file add:

```yaml
grocy:
  host: !secret grocy_host
  apikey: !secret grocy_apikey
```

## Services

### add_to_list

### subtract_from_list

### add_product

### remove_product

### update_product

### sync

---

Enjoy my card? Help me out for a couple of :beers: or a :coffee:!

<a href="https://www.buymeacoffee.com/cgboJEh" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

[buymecoffee]: https://www.buymeacoffee.com/cgboJEh
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[hacs]: https://github.com/custom-components/hacs