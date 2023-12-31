# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.spreadsheet_edition.tests.spreadsheet_test_case import SpreadsheetTestCase


class SpreadsheetMixinTest(SpreadsheetTestCase):


    def test_copy_revisions(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        copy = spreadsheet.copy()
        self.assertEqual(
            copy.spreadsheet_revision_ids.commands,
            spreadsheet.spreadsheet_revision_ids.commands,
        )

    def test_dont_copy_revisions_if_provided(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        copy = spreadsheet.copy({"spreadsheet_revision_ids": []})
        self.assertFalse(copy.spreadsheet_revision_ids)

    def test_company_currency(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        company_eur = self.env["res.company"].create({"currency_id": self.env.ref("base.EUR").id, "name": "EUR"})
        company_gbp = self.env["res.company"].create({"currency_id": self.env.ref("base.GBP").id, "name": "GBP"})

        data = spreadsheet.with_company(company_eur).join_spreadsheet_session()
        self.assertEqual(data["default_currency"]["code"], "EUR")
        self.assertEqual(data["default_currency"]["symbol"], "€")

        data = spreadsheet.with_company(company_gbp).join_spreadsheet_session()
        self.assertEqual(data["default_currency"]["code"], "GBP")
        self.assertEqual(data["default_currency"]["symbol"], "£")

    def test_fork_history(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        rev1 = spreadsheet.spreadsheet_revision_ids[0]
        action = spreadsheet.fork_history(rev1.id, {"test": "snapshot"})
        self.assertTrue(isinstance(action, dict))

        self.assertEqual(action["params"]["message"], "test spreadsheet created")
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["type"], "ir.actions.client")

        next_action = action["params"]["next"]

        self.assertTrue(isinstance(next_action, dict))
        copy_id = next_action["params"]["spreadsheet_id"]
        spreadsheet_copy = self.env["spreadsheet.test"].browse(copy_id)
        self.assertTrue(spreadsheet_copy.exists())
        self.assertEqual(len(spreadsheet_copy.spreadsheet_revision_ids), 1)
        self.assertEqual(spreadsheet_copy.spreadsheet_revision_ids[0].commands, rev1.commands)

    def test_rename_revision(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        revision = spreadsheet.spreadsheet_revision_ids[0]
        self.assertEqual(revision.name, False)

        spreadsheet.rename_revision(revision.id, "new revision name")
        self.assertEqual(revision.name, "new revision name")

    def test_get_spreadsheet_history(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        self.snapshot(
            spreadsheet,
            spreadsheet.server_revision_id, "snapshot-revision-id", {"sheets": [], "revisionId": "snapshot-revision-id"},
        )
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))

        data = spreadsheet.get_spreadsheet_history()
        self.assertEqual(len(data["revisions"]), 3)

        # from snapshot
        data = spreadsheet.get_spreadsheet_history(True)
        self.assertEqual(len(data["revisions"]), 1)

    def test_empty_spreadsheet_server_revision_id(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        self.assertEqual(spreadsheet.server_revision_id, "START_REVISION")

    def test_no_data_server_revision_id(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        spreadsheet.spreadsheet_snapshot = False
        spreadsheet.spreadsheet_data = False
        self.assertEqual(spreadsheet.server_revision_id, False)

    def test_last_revision_is_server_revision_id(self):
        spreadsheet = self.env["spreadsheet.test"].create({})

        revision_data = self.new_revision_data(spreadsheet)
        next_revision_id = revision_data["nextRevisionId"]
        spreadsheet.dispatch_spreadsheet_message(revision_data)
        self.assertEqual(spreadsheet.server_revision_id, next_revision_id)

        # dispatch new revision on top
        revision_data = self.new_revision_data(spreadsheet)
        next_revision_id = revision_data["nextRevisionId"]
        spreadsheet.dispatch_spreadsheet_message(revision_data)
        self.assertEqual(spreadsheet.server_revision_id, next_revision_id)

    def test_snapshotted_server_revision_id(self):
        spreadsheet = self.env["spreadsheet.test"].create({})
        snapshot_revision_id = "snapshot-id"
        self.snapshot(
            spreadsheet,
            spreadsheet.server_revision_id,
            snapshot_revision_id,
            {"revisionId": snapshot_revision_id},
        )
        self.assertEqual(spreadsheet.server_revision_id, snapshot_revision_id)

        # dispatch revision after snapshot
        revision_data = self.new_revision_data(spreadsheet)
        next_revision_id = revision_data["nextRevisionId"]
        spreadsheet.dispatch_spreadsheet_message(revision_data)
        self.assertEqual(spreadsheet.server_revision_id, next_revision_id)
