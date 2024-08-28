import MySQLdb
from timeout_function_decorator import timeout

import values


class CdrConnector:
    """MySQL connector to access raw CDR data"""

    def __init__(self, namespace, username, password, host, port):
        try:
            dbconfig = {
                "user": username,
                "password": password,
                "host": host,
                "database": f"{namespace}-cdrdb",
                "port": int(port),
                "ssl_mode": "DISABLED",
                "connect_timeout": values.CDR_CONNECTOR_TIMEOUT_THRESHOLD
            }

            self.connector = MySQLdb.connect(**dbconfig)
            self.connector.autocommit(True)

        except Exception as e:
            raise Exception(f"Error: Connection to MySQL failed: {str(e)}")

    def close(self):
        self.connector.close()

    @timeout(values.CDR_CONNECTOR_TIMEOUT_THRESHOLD)
    def get_total_calls(self, interval: int, unit: str = "MINUTE") -> int:
        c = self.connector.cursor()

        c.execute(
            f"""
            SELECT
                COUNT(*)
            FROM cdr AS cdr1
            INNER JOIN cdr AS cdr2 ON cdr1.linkedid = cdr2.linkedid
            WHERE cdr1.disposition = 'ANSWERED'
            AND cdr2.disposition = 'ANSWERED'
            AND cdr1.dst IS NOT NULL
            AND cdr2.dst IS NULL
            AND cdr1.`start` > ((NOW() + INTERVAL 2 HOUR) - INTERVAL %s {unit})
        """, (interval, ))

        result = c.fetchall()
        c.close()

        return int(result[0][0]) if result else -1

    # Get the call latencies of the last `interval`. Notice that the latency is measured from the arrival of the A party INVITE till sending out the B party INVITE at the PBX
    @timeout(values.CDR_CONNECTOR_TIMEOUT_THRESHOLD)
    def get_latest_latencies_of_interval(self,
                                         interval: int,
                                         unit: str = "MINUTE") -> list[float]:
        c = self.connector.cursor()

        c.execute(
            f"""
            SELECT
                TIMESTAMPDIFF(SECOND, cdr1.`start`, cdr2.`start`) AS latency
            FROM cdr AS cdr1
            INNER JOIN cdr AS cdr2 ON cdr1.linkedid = cdr2.linkedid
            WHERE cdr1.disposition = 'ANSWERED'
            AND cdr2.disposition = 'ANSWERED'
            AND cdr1.dst IS NOT NULL
            AND cdr2.dst IS NULL
            AND cdr1.`start` > ((NOW() + INTERVAL 2 HOUR) - INTERVAL %s {unit})
        """, (interval, ))

        result = c.fetchall()
        c.close()

        latencies: list[float] = []

        for i in range(len(result)):
            field = result[i][0]

            if field is None:
                continue

            latencies.append(float(field))

        return latencies

    @timeout(values.CDR_CONNECTOR_TIMEOUT_THRESHOLD)
    def get_failed_calls_of_interval(self,
                                     interval: int,
                                     unit: str = "MINUTE") -> int:
        c = self.connector.cursor()

        c.execute(
            f"""
            SELECT
                COUNT(*)
            FROM cdr
            WHERE ((disposition = 'NO ANSWER' AND reason = 'NO_USER_RESPONSE') OR disposition = 'FAILED')
            AND `start` > ((NOW() + INTERVAL 2 HOUR) - INTERVAL %s {unit})
        """, (interval, ))

        result = c.fetchall()
        c.close()

        return int(result[0][0]) if result else -1
