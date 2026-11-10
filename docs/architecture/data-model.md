# Data Model

The table list with key fields is in [`docs/requirements/00-consolidated-requirements.md`, section 6](../requirements/00-consolidated-requirements.md#6-logical-data-model).

Foundation item **F8** adds the relationship diagram here when the migrations are written.

## Relationships (summary)

```
auth.users 1─1 profiles 1─1 carts 1─* cart_items *─* flavors (via cart_item_flavors)
                                         └── *─1 base_chips
profiles 1─* orders 1─* order_items 1─* order_item_flavors
base_chips 1─* staff_picks 1─* staff_pick_flavors *─1 flavors
stock_history *─1 base_chips | flavors, *─1 profiles (changed_by), *─1 orders (optional)
settings: a single row
```
