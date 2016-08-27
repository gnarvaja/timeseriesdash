from plugins.base import DBMetric
from utils import accumulate


class AccountingMetric(DBMetric):
    metric_type = "accounting"

    def generate(self, ffrom, tto):
        account_codes = self.config["account_codes"].split(",")

        accounts_plan_id = self.config["accounts_plan_id"]

        journal = self.config["journal"]
        sum_type = self.config["sum_type"]

        sign = self.config["sign"]
        account_ids = self._get_account_ids(accounts_plan_id, account_codes)
        totalized_movs = self._sumarize_movements(ffrom, tto, account_ids, journal)

        accumulate(totalized_movs, sum_type)

        data = [{"label": row[0].strftime("%Y-%m-%d"), "data": sign * int(row[1])}
                for row in totalized_movs]
        return data

    def _get_account_ids(self, accounts_plan_id, account_codes):
        ret = set()

        with self.db.cursor() as cursor:
            cursor.execute("""SELECT account_id
                FROM account
                WHERE accounts_plan_id = %(accounts_plan_id)s AND code IN %(account_codes)s""", locals())
            account_ids = [row[0] for row in cursor]
            while account_ids:
                ret.update(account_ids)
                cursor.execute("""SELECT account_id
                    FROM account
                    WHERE accounts_plan_id = %(accounts_plan_id)s AND account_parent_id IN %(account_ids)s""",
                            locals())
                account_ids = [row[0] for row in cursor]
        return list(ret)

    def _sumarize_movements(self, ffrom, tto, account_ids, journal):
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT generate_series AS month, 0 AS amount
                FROM generate_series(%(ffrom)s, %(tto)s, interval '1 month')
                """, locals())
            ret = dict((row["month"], row["amount"]) for row in cursor.fetchall())

            cursor.execute("""
                SELECT date_trunc('month', E.entry_date) AS month,
                    SUM(EI.amount) AS amount
                FROM journal_entry E
                    INNER JOIN journal_entry_item EI
                        ON EI.journal_entry_id = E.journal_entry_id
                WHERE EI.account_id IN %(account_ids)s AND
                    E.entry_date BETWEEN %(ffrom)s AND %(tto)s AND E.type_id != 5 /* ENTRY_TYPE_CLOSING */
                GROUP BY month
                ORDER BY month""", locals())
            for row in cursor.fetchall():
                ret[row["month"]] = row["amount"]
            return sorted(ret.items(), key=lambda (k, v): k)
