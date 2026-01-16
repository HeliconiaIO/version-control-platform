Just access your organization and fill the data from your weblate in the specific tab.

For the first loading, might be faster to execute the code in shell by using the following commands (increase the delta if you want):

``` python
self = self.env["contributors.organization"].search([], limit=1) # Use your organization here
for i in range(1,100):
    self.get_weblate_data()
    self.env.cr.commit()
```

Once it has finished, restart the cron.