import os.path
from plugins.base import DBMetric
from utils import accumulate, ensure_date, generate_date_series, calculate_period_to


class QueryMetric(DBMetric):
    metric_type = "query"

    def get_params(self):
        query_params = self.config.get("query_params", {})
        return query_params

    def _get_query(self):
        filename = self.config.get("file", "%s.sql" % self.name)
        if filename[0] in "./~":
            return open(os.path.expanduser(filename)).read()
        else:
            filename = os.path.join(self.global_config.get("sql_dir", "."), filename)
            return open(os.path.expanduser(filename)).read()

    def generate(self, ffrom, tto):
        period_type = self.get_period_type()

        sum_type = self.config.get("sum_type", "sum")

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret

        query = self._get_query()

        with self.db.cursor() as cursor:
            params = {'ffrom': new_ffrom, 'tto': new_tto, "period": period_type}
            params.update(self.get_params())
            try:
                cursor.execute(query, params)
            except:
                import ipdb; ipdb.set_trace()
                raise
            for row in cursor.fetchall():
                ret[ensure_date(row["period"])] = row["value"]
            # Fill missing dates with zeros
            missing_dates = [d for d in generate_date_series(new_ffrom, new_tto, period_type)
                             if d not in ret]
            for missing in missing_dates:
                ret[missing] = 0

            totalized_movs = sorted(ret.items(), key=lambda k_v: k_v[0])

        accumulate(totalized_movs, sum_type)

        data = [{"label": row[0].strftime("%Y-%m-%d"), "data": float(row[1])}
                for row in totalized_movs]
        return data


class SingleValueQueryMetric(QueryMetric):
    metric_type = "single_query"

    def generate(self, ffrom, tto):
        period_type = self.get_period_type()

        sum_type = self.config.get("sum_type", "sum")

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret

        query = self._get_query()

        with self.db.cursor() as cursor:
            for period_from in generate_date_series(new_ffrom, new_tto, period_type):
                period_to = calculate_period_to(period_from, period_type)
                params = {'ffrom': period_from, 'tto': period_to, "period": period_type}
                params.update(self.get_params())
                try:
                    cursor.execute(query, params)
                except:
                    import ipdb; ipdb.set_trace()
                rrow = cursor.fetchone()
                if not rrow:
                    ret[period_from] = 0
                else:
                    ret[period_from] = rrow["value"]

            totalized_movs = sorted(ret.items(), key=lambda k_v: k_v[0])

        accumulate(totalized_movs, sum_type)

        if [row for row in totalized_movs if row[1] is None]:
            import ipdb; ipdb.set_trace()

        data = [{"label": row[0].strftime("%Y-%m-%d"), "data": float(row[1])}
                for row in totalized_movs]
        return data
