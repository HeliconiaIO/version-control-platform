Access the Contributors / Organization module.

Add your organization and one ore more API Keys (it might be faster if you add several ones).

Update the repositories.

The system will start fetching the data automatically.

## First Load

Usually, the first load can take a lot of time and you could find time constrains on your Odoo database.
For this reason we recommend to stop the cron in this first load and execute the following code in your shell once you have all the repositories created:

```python:
from datetime import date, datetime, timedelta
import time
self = self.env["contributors.organization"].search([], limit=1) # Use the organization you prefer
clients = self._get_clients()
FIXED_DATE = "2026-01-01"
repositories = self.env["contributors.repository"].search([("from_date", "<", FIXED_DATE), ("organization_id", "=", self.id)], order="from_date asc")
i = 0
while repositories:
    try:
        for repository in repositories:
            i = (i+1) % len(clients)
            repository.update_information(client_for_search=i)
            self.env.cr.commit()
    except Exception:
        date = False
        for client in clients:
            rate = client.rate_limit()
            print(rate)
            for code in rate["resources"]:
                if rate["resources"][code]["remaining"] == 0:
                    date = max(date or 0, rate["resources"][code]["reset"])
        if not date:
            raise
        print("%s - Sleeping for %s seconds" % (datetime.now().isoformat(), date - time.mktime(datetime.now().timetuple())))
        time.sleep(date - time.mktime(datetime.now().timetuple()))
        time.sleep(10)
    repositories = self.env["contributors.repository"].search([("from_date", "<", FIXED_DATE), ("organization_id", "=", self.id)], order="from_date asc")
```

Once it has finished, restart the cron.
