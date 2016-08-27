from plugins.base import DBMetric
from utils import accumulate, ensure_date


class FierroSalesMetric(DBMetric):
    metric_type = "sales"

    def generate(self, ffrom, tto):
        sucursal_id = self.config["sucursal"]
        sucursal_negated = False
        if sucursal_id == "all":
            sucursal_id = None
        elif sucursal_id.startswith("-"):
            sucursal_negated = True
        period_type = self.config["period"]

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret

        sum_type = self.config["sum_type"]

        if sucursal_negated:
            equal = "!="
        else:
            equal = "="

        query = """SELECT date_trunc('%s', S.real_date) AS period, SUM(S.amount) AS amount
            FROM (
                SELECT D.real_date, getBuyQuotationAt(SB.currency_id, D.real_date) * SB.amount AS amount
                FROM sale_bill SB
                    INNER JOIN document D ON D.document_id = SB.document_id
                WHERE NOT SB.cancelled AND
                    (%%(sucursal_id)s IS NULL OR D.sucursal_id %s %%(sucursal_id)s) AND
                    D.real_date BETWEEN %%(ffrom)s AND %%(tto)s
                UNION ALL
                SELECT D.real_date, getBuyQuotationAt(SCN.currency_id, D.real_date) * -SCN.amount AS amount
                FROM sale_credit_note SCN
                    INNER JOIN document D ON D.document_id = SCN.document_id
                WHERE NOT SCN.cancelled AND
                    (%%(sucursal_id)s IS NULL OR D.sucursal_id %s %%(sucursal_id)s) AND
                    D.real_date BETWEEN %%(ffrom)s AND %%(tto)s
                ) AS S
            GROUP BY period
            ORDER BY period
            """ % (period_type, equal, equal)
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT generate_series AS period, 0 AS amount
                FROM generate_series(%%(ffrom)s, %%(tto)s, interval '1 %s')
                        """ % period_type, {'ffrom': new_ffrom, 'tto': new_tto})
            ret.update(dict((ensure_date(row["period"]), row["amount"]) for row in cursor.fetchall()))

            cursor.execute(query, {"sucursal_id": sucursal_id, 'ffrom': new_ffrom, 'tto': new_tto})
            for row in cursor.fetchall():
                ret[ensure_date(row["period"])] = row["amount"]
            totalized_movs = sorted(ret.items(), key=lambda (k, v): k)

        accumulate(totalized_movs, sum_type)

        data = [{"label": row[0].strftime("%Y-%m-%d"), "data": float(row[1])}
                for row in totalized_movs]
        return data
