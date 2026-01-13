# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

import github3
from github3 import pulls
from pytz import UTC

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ContributorsRepository(models.Model):
    _name = "contributors.repository"
    _description = "Contributors Repository"

    name = fields.Char(required=True, index=True)
    description = fields.Char(readonly=True)
    organization_id = fields.Many2one(
        comodel_name="contributors.organization",
        string="Organization",
        required=True,
    )
    created_at = fields.Datetime(readonly=True)
    stargazers_count = fields.Integer(readonly=True)
    fork_count = fields.Integer(readonly=True)
    watchers_count = fields.Integer(readonly=True)
    from_date = fields.Datetime(readonly=True, required=True)
    pull_request_ids = fields.One2many(
        "contributors.pull.request", inverse_name="repository_id"
    )
    pull_request_count = fields.Integer(compute="_compute_pull_request_count")
    active = fields.Boolean(default=True)

    @api.depends("pull_request_ids")
    def _compute_pull_request_count(self):
        for record in self:
            record.pull_request_count = len(record.pull_request_ids)

    def parse_pr(self, pr, client):
        origin_data = pr.as_dict()
        comments_url = pr.comments_url
        comments_req = client.session.get(comments_url)
        comments = comments_req.json()
        while comments_req.links.get("next"):
            comments_url = comments_req.links["next"]["url"]
            comments_req = client.session.get(comments_url)
            comments += comments_req.json()
        reviews_url = pr.reviews().url
        reviews_req = client.session.get(reviews_url)
        reviews = reviews_req.json()
        while reviews_req.links.get("next"):
            reviews_url = reviews_req.links["next"]["url"]
            reviews_req = client.session.get(reviews_url)
            reviews += reviews_req.json()
        return (
            str(pr.id),
            {
                "partner_id": self.env["res.partner"]._get_github_user(pr.user, client),
                "repository_id": self.id,
                "branch_id": self.organization_id._get_branch(pr.base.ref),
                "organization_id": self.env["res.partner"]._get_github_organization(
                    pr.head.repo[0], client
                ),
                "url": pr.html_url,
                "state": pr.state,
                "name": pr.title,
                "is_merged": any(label["name"] == "merged 🎉" for label in pr.labels)
                or pr.is_merged(),
                "created_at": self._parse_date(origin_data["created_at"]),
                "closed_at": self._parse_date(origin_data["closed_at"]),
                "number": pr.number,
                "updated_at": self._parse_date(origin_data["updated_at"]),
                "label_ids": [fields.Command.clear()]
                + [
                    fields.Command.link(
                        self.env["contributors.pull.request.label"]._get_label(
                            label["name"]
                        )
                    )
                    for label in origin_data["labels"]
                ],
                "commits": origin_data["commits"],
                "total_comments": origin_data["comments"],
                "review_comments": origin_data["review_comments"],
                "additions": origin_data["additions"],
                "deletions": origin_data["deletions"],
            },
            [
                {
                    "id": str(c["id"]),
                    "partner_id": c.get("user")
                    and self.env["res.partner"]._get_github_user(
                        c["user"].get("login"), client
                    ),
                    "body": c["body"],
                    "created_at": self._parse_date(c["created_at"]),
                    "updated_at": self._parse_date(c["updated_at"]),
                }
                for c in comments
            ],
            [
                {
                    "id": str(r["id"]),
                    "partner_id": r.get("user")
                    and self.env["res.partner"]._get_github_user(
                        r["user"].get("login"), client
                    ),
                    "body": r["body"],
                    "submitted_at": self._parse_date(r.get("submitted_at")),
                    "state": r["state"]["keyword"]
                    if isinstance(r["state"], dict)
                    else r["state"],
                }
                for r in reviews
            ],
        )

    def force_update_information(self):
        self.update_information(update_interval_days=365)

    def update_information(self, update_interval_days=None, client_for_search=0):
        self.ensure_one()
        clients = self.organization_id._get_clients()
        try:
            start = UTC.localize(self.from_date)
            end = min(
                start
                + timedelta(
                    days=update_interval_days
                    or self.organization_id.update_interval_days
                ),
                UTC.localize(datetime.now()),
            )
            start += timedelta(
                days=-1
            )  # Add buffer day to avoid missing PRs on boundary dates
            i = client_for_search % len(clients)
            for pr in clients[i].search_issues(
                f"is:pr repo:{self.organization_id.name}/{self.name} "
                f"updated:{start.isoformat()}..{end.isoformat()}"
            ):
                i = (1 + i) % len(clients)
                pr_id, pr_data, comments, reviews = self.parse_pr(
                    clients[i]._instance_or_null(
                        pulls.PullRequest,
                        clients[i]._json(
                            pr.issue._get(pr.issue.pull_request_urls.get("url")), 200
                        ),
                    ),
                    clients[i],
                )
                opr = self.env["contributors.pull.request"].search(
                    [("github_id", "=", pr_id)], limit=1
                )
                if not opr:
                    opr = (
                        self.env["contributors.pull.request"]
                        .sudo()
                        .create({"github_id": pr_id, **pr_data})
                    )
                else:
                    opr.sudo().write(pr_data)
                for comment in comments:
                    comment_id = comment.pop("id")
                    ocomment = self.env["contributors.comment"].search(
                        [("github_id", "=", comment_id)], limit=1
                    )
                    if not ocomment:
                        self.env["contributors.comment"].sudo().create(
                            {
                                "github_id": comment_id,
                                "pull_request_id": opr.id,
                                **comment,
                            }
                        )
                    else:
                        ocomment.sudo().write(comment)
                for review in reviews:
                    review_id = review.pop("id")
                    oreview = self.env["contributors.review"].search(
                        [("github_id", "=", review_id)], limit=1
                    )
                    if not oreview:
                        self.env["contributors.review"].sudo().create(
                            {
                                "github_id": review_id,
                                "pull_request_id": opr.id,
                                **review,
                            }
                        )
                    else:
                        oreview.sudo().write(review)
            self.sudo().from_date = end.replace(tzinfo=None)
        except github3.exceptions.ForbiddenError as e:
            _logger.error(e)
            rate = clients[i].rate_limit()
            reset = fields.Datetime.to_string(
                datetime.utcfromtimestamp(rate["resources"]["core"]["reset"])
            )
            raise ValidationError(self.env._(f"Reset on {reset}")) from e

    def _parse_date(self, date):
        if not date:
            return False
        return UTC.normalize(
            datetime.fromisoformat(date.replace("Z", "+00:00"))
        ).replace(tzinfo=None)

    def _update_repository(self, repo, organization):
        vals = {
            "created_at": self._parse_date(repo.created_at),
            "stargazers_count": repo.stargazers_count,
            "fork_count": repo.forks_count,
            "watchers_count": repo.watchers_count,
            "description": repo.description,
        }
        repository = self.search(
            [
                ("name", "=", repo.name),
                ("organization_id", "=", organization.id),
            ],
            limit=1,
        )
        if not repository:
            repository = (
                self.env["contributors.repository"]
                .sudo()
                .create(
                    {
                        "name": repo.name,
                        "organization_id": organization.id,
                        "from_date": vals.get("created_at"),
                        **vals,
                    }
                )
            )
        else:
            repository.sudo().write(vals)

    def _cron_update_repositories(self, limit=1):
        repositories = self.search([], limit=limit, order="from_date ASC")
        for repository in repositories:
            repository.update_information()
