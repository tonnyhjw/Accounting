from pprint import pprint
from utils.models import Voucher as mongo_table
from utils.models_sql import Voucher as sql_table, VoucherRow


def transfer(mongo_db, maria_db):
    for _ in mongo_db.objects:
        json_data = _.json()
        pprint(json_data)
        maria_db().create(**json_data)
    return

def transfer_voucher(mongo_db, maria_db):
    empty = [['', '', '', '', '', '', '', ''], []]
    for _ in mongo_db.objects:
        json_data = _.json()
        json_data = {i: json_data[i] for i in json_data if json_data[i] not in empty}

        # pprint(json_data)
        for k, v in json_data.items():

            if isinstance(v, list):
                row = {f'index_{attr_i}': attr_v for attr_i, attr_v in enumerate(v)}
                sql_row = VoucherRow.create(**row)
                json_data[k] = sql_row

        pprint(json_data)
        maria_db.create(**json_data)

    return


if __name__ == '__main__':
    # transfer(mongo_table, sql_table)
    transfer_voucher(mongo_table, sql_table)